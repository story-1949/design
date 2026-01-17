from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import logging
import json

from app.services.copilot_client import CopilotClient
from app.services.session_manager import SessionManager
from app.services.intent_classifier import IntentClassifier
from app.utils.rate_limiter import rate_limiter
from app.utils.exceptions import (
    SessionNotFoundException,
    RateLimitExceededException,
    AIServiceException
)

logger = logging.getLogger(__name__)
router = APIRouter()


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., pattern="^(user|assistant)$", description="角色")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    session_id: Optional[str] = Field(None, description="会话ID（可选）")
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    context: Optional[Dict] = Field(default_factory=dict, description="额外上下文")


class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="助手回复")
    intent: Optional[str] = Field(None, description="识别的意图")
    entities: Optional[Dict] = Field(None, description="提取的实体")
    suggested_actions: Optional[List[str]] = Field(None, description="建议操作")
    products: Optional[List[Dict]] = Field(None, description="推荐商品")


# 服务实例（单例）
copilot = CopilotClient()
session_manager = SessionManager()
intent_classifier = IntentClassifier()


def check_rate_limit(client_id: str):
    """检查限流"""
    if not rate_limiter.is_allowed(client_id):
        raise RateLimitExceededException()


@router.post("/chat", response_model=ChatResponse, summary="智能对话")
async def chat(request: ChatRequest):
    """
    智能对话接口
    
    功能：
    - 多轮对话上下文管理
    - 自动意图识别
    - 实体提取
    - 商品推荐
    - 订单查询
    - 售后咨询
    
    示例：
    ```json
    {
        "message": "我想买一部性价比高的手机",
        "session_id": "optional-session-id"
    }
    ```
    """
    try:
        # 简单限流（实际应该基于用户 IP 或 ID）
        check_rate_limit("global")
        
        # 获取或创建会话
        if request.session_id:
            session = await session_manager.get_session(request.session_id)
            if not session:
                raise SessionNotFoundException(request.session_id)
        else:
            session = await session_manager.create_session()

        session_id = session["session_id"]
        history = session.get("history", [])

        logger.info(f"会话 {session_id}: {request.message[:50]}...")

        # 意图识别
        intent_result = await intent_classifier.classify(request.message, history)
        intent = intent_result.get("intent")
        entities = intent_result.get("entities", {})

        logger.info(f"识别意图: {intent}, 实体: {entities}")

        # 构建对话上下文
        context = {
            "history": history,
            "intent": intent,
            "entities": entities,
            "user_context": request.context
        }

        # 调用 Copilot 生成回复
        response = await copilot.chat(
            message=request.message,
            context=context
        )

        # 更新会话历史
        await session_manager.add_message(
            session_id,
            {"role": "user", "content": request.message, "intent": intent}
        )
        await session_manager.add_message(
            session_id,
            {"role": "assistant", "content": response["message"]}
        )

        return ChatResponse(
            session_id=session_id,
            message=response["message"],
            intent=intent,
            entities=entities,
            suggested_actions=response.get("suggested_actions"),
            products=response.get("products")
        )

    except (SessionNotFoundException, RateLimitExceededException, AIServiceException):
        raise
    except Exception as e:
        logger.error(f"聊天失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@router.get("/chat/history/{session_id}", summary="获取聊天历史")
async def get_chat_history(session_id: str):
    """获取指定会话的聊天历史"""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise SessionNotFoundException(session_id)
        
        return {
            "session_id": session_id,
            "history": session.get("history", []),
            "created_at": session.get("created_at"),
            "last_activity": session.get("last_activity")
        }
    except SessionNotFoundException:
        raise
    except Exception as e:
        logger.error(f"获取历史失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/session/{session_id}", summary="清除会话")
async def clear_session(session_id: str):
    """清除指定会话及其历史记录"""
    try:
        success = await session_manager.delete_session(session_id)
        if not success:
            raise SessionNotFoundException(session_id)
        return {"message": "会话已清除", "session_id": session_id}
    except SessionNotFoundException:
        raise
    except Exception as e:
        logger.error(f"清除会话失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat/ws")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket 实时聊天
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            request_data = json.loads(data)

            message = request_data.get("message")
            if not message:
                await websocket.send_json({"error": "消息不能为空"})
                continue

            # 创建或获取会话
            if not session_id:
                session = await session_manager.create_session()
                session_id = session["session_id"]

            session = await session_manager.get_session(session_id)
            history = session.get("history", [])

            # 意图识别
            intent_result = await intent_classifier.classify(message, history)

            # 发送意图识别结果
            await websocket.send_json({
                "type": "intent",
                "intent": intent_result.get("intent"),
                "entities": intent_result.get("entities")
            })

            # 流式生成回复
            async for chunk in copilot.chat_stream(
                    message=message,
                    context={"history": history}
            ):
                await websocket.send_json({
                    "type": "message_chunk",
                    "content": chunk
                })

            # 更新会话
            await session_manager.add_message(
                session_id,
                {"role": "user", "content": message}
            )

            await websocket.send_json({
                "type": "done",
                "session_id": session_id
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket 连接断开: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket 错误: {str(e)}")
        await websocket.send_json({"error": str(e)})