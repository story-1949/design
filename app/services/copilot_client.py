import anthropic
from typing import Dict, List, Optional, AsyncGenerator
from app.core.config import settings
from app.utils.exceptions import AIServiceException
from app.utils.cache import cached
import logging
import json
import asyncio

logger = logging.getLogger(__name__)


class CopilotClient:
    """AI Copilot 客户端 - 封装 Anthropic Claude API"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY 未配置")
            
            self.client = anthropic.AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                timeout=settings.AI_TIMEOUT
            )
            self.model = settings.COPILOT_MODEL
            self.initialized = True

        # 系统提示词
        self.system_prompt = """你是一个专业的电商智能助手，名字叫"智购助手"。你的职责是：

1. **商品咨询**：帮助用户找到合适的商品，提供专业的购买建议
2. **订单查询**：协助查询订单状态、物流信息
3. **售后服务**：处理退换货、投诉建议等问题
4. **购物指导**：提供使用教程、尺码建议、搭配推荐等

回复要求：
- 友好、专业、简洁
- 理解用户真实需求，不要机械回复
- 主动提供有价值的建议
- 遇到无法处理的问题，引导用户联系人工客服
- 必要时以 JSON 格式返回结构化数据

当前时间：{current_time}
"""

    async def chat(
            self,
            message: str,
            context: Optional[Dict] = None
    ) -> Dict:
        """
        发送聊天请求

        Args:
            message: 用户消息
            context: 上下文信息（历史记录、意图、实体等）

        Returns:
            回复内容和相关数据
        """
        try:
            # 构建消息历史
            messages = []

            if context and context.get("history"):
                # 保留最近的对话，限制 token 数量
                messages.extend(context["history"][-settings.MAX_CONVERSATION_HISTORY:])

            messages.append({
                "role": "user",
                "content": message
            })

            # 构建系统提示
            system = self.system_prompt.format(
                current_time=self._get_current_time()
            )

            # 添加上下文信息
            if context:
                if context.get("intent"):
                    system += f"\n\n当前用户意图：{context['intent']}"
                if context.get("entities"):
                    system += f"\n识别到的实体：{json.dumps(context['entities'], ensure_ascii=False)}"

            # 调用 API（带超时）
            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    system=system,
                    messages=messages
                ),
                timeout=settings.AI_TIMEOUT
            )

            content = response.content[0].text

            # 尝试解析结构化响应
            result = self._parse_response(content)

            return result

        except asyncio.TimeoutError:
            logger.error("AI 请求超时")
            raise AIServiceException("AI 服务响应超时，请稍后重试")
        except anthropic.APIError as e:
            logger.error(f"Anthropic API 错误: {e}")
            raise AIServiceException(f"AI 服务错误: {e}")
        except Exception as e:
            logger.error(f"Copilot 调用失败: {str(e)}", exc_info=True)
            raise AIServiceException(str(e))

    async def chat_stream(
            self,
            message: str,
            context: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天
        """
        try:
            messages = []
            if context and context.get("history"):
                messages.extend(context["history"][-10:])
            messages.append({"role": "user", "content": message})

            system = self.system_prompt.format(
                current_time=self._get_current_time()
            )

            async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    system=system,
                    messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"流式聊天失败: {str(e)}")
            raise

    @cached(ttl=1800, key_prefix="search_intent")
    async def analyze_search_intent(self, query: str) -> Dict:
        """
        分析搜索意图，增强搜索查询（带缓存）
        """
        try:
            prompt = f"""分析以下搜索查询，提取关键信息并优化搜索词：

用户查询：{query}

请返回 JSON 格式：
{{
    "enhanced_query": "优化后的搜索词",
    "intent": "搜索意图（浏览/购买/比较/咨询）",
    "category": "商品类别",
    "attributes": {{"颜色": "红色", "尺寸": "L"}},
    "price_range": {{"min": 100, "max": 500}},
    "insights": "用户可能的真实需求"
}}"""

            response = await asyncio.wait_for(
                self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                ),
                timeout=10  # 搜索意图分析超时时间较短
            )

            content = response.content[0].text
            # 提取 JSON
            result = self._extract_json(content)
            return result if result else {"enhanced_query": query}

        except asyncio.TimeoutError:
            logger.warning("搜索意图分析超时，使用原始查询")
            return {"enhanced_query": query}
        except Exception as e:
            logger.error(f"意图分析失败: {str(e)}")
            return {"enhanced_query": query}

    async def generate_product_recommendation(
            self,
            user_profile: Dict,
            browsing_history: List[Dict],
            limit: int = 5
    ) -> List[Dict]:
        """
        生成个性化商品推荐
        """
        try:
            prompt = f"""基于用户画像和浏览历史，推荐合适的商品：

用户画像：{json.dumps(user_profile, ensure_ascii=False)}
浏览历史：{json.dumps(browsing_history[-10:], ensure_ascii=False)}

请推荐 {limit} 个商品，返回 JSON 格式：
[
    {{
        "product_id": "商品ID",
        "reason": "推荐理由",
        "score": 0.95
    }}
]"""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            result = self._extract_json(content)
            return result if isinstance(result, list) else []

        except Exception as e:
            logger.error(f"推荐生成失败: {str(e)}")
            return []

    def _parse_response(self, content: str) -> Dict:
        """解析回复内容"""
        result = {"message": content}

        # 尝试提取 JSON 数据
        json_data = self._extract_json(content)
        if json_data:
            result.update(json_data)

        return result

    def _extract_json(self, text: str) -> Optional[Dict]:
        """从文本中提取 JSON"""
        try:
            # 查找 JSON 块
            import re
            json_pattern = r'```json\s*(.*?)\s*```|```\s*(.*?)\s*```|(\{.*\}|\[.*\])'
            matches = re.findall(json_pattern, text, re.DOTALL)

            for match in matches:
                json_str = next((m for m in match if m), None)
                if json_str:
                    return json.loads(json_str)

            # 尝试直接解析整个文本
            return json.loads(text)
        except:
            return None

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")