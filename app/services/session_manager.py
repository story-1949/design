from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import logging
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器 - 管理用户对话会话（单例模式）"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            # 使用内存存储（生产环境应使用 Redis）
            self.sessions: Dict[str, Dict] = {}
            self.session_timeout = timedelta(seconds=settings.SESSION_TIMEOUT)
            self._cleanup_task = None
            self.initialized = True
    
    def start_cleanup_task(self):
        """启动清理任务（在事件循环中调用）"""
        if self._cleanup_task is None:
            try:
                self._cleanup_task = asyncio.create_task(self._cleanup_loop())
                logger.info("会话清理任务已启动")
            except RuntimeError:
                # 如果没有运行的事件循环，忽略
                pass

    async def create_session(self, user_id: Optional[str] = None) -> Dict:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "history": [],
            "context": {},
            "metadata": {}
        }
        self.sessions[session_id] = session
        logger.info(f"创建会话: {session_id}")
        return session

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话"""
        session = self.sessions.get(session_id)

        if not session:
            logger.warning(f"会话不存在: {session_id}")
            return None

        # 检查会话是否过期
        if self._is_expired(session):
            logger.info(f"会话已过期: {session_id}")
            await self.delete_session(session_id)
            return None

        # 更新活动时间
        session["last_activity"] = datetime.utcnow()
        return session

    async def add_message(
        self, 
        session_id: str, 
        message: Dict,
        save_to_db: bool = False
    ) -> bool:
        """添加消息到会话历史"""
        session = await self.get_session(session_id)
        if not session:
            logger.warning(f"无法添加消息，会话不存在: {session_id}")
            return False

        # 添加时间戳
        message_with_timestamp = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        session["history"].append(message_with_timestamp)

        # 限制历史记录长度
        max_history = settings.MAX_CONVERSATION_HISTORY * 2  # 用户+助手各算一条
        if len(session["history"]) > max_history:
            session["history"] = session["history"][-max_history:]
            logger.debug(f"会话历史已截断: {session_id}")

        # TODO: 如果需要持久化，保存到数据库
        if save_to_db:
            pass  # 实现数据库保存逻辑

        return True

    async def update_context(self, session_id: str, context: Dict) -> bool:
        """更新会话上下文"""
        session = await self.get_session(session_id)
        if not session:
            return False

        session["context"].update(context)
        logger.debug(f"更新会话上下文: {session_id}")
        return True
    
    async def update_metadata(self, session_id: str, metadata: Dict) -> bool:
        """更新会话元数据"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session["metadata"].update(metadata)
        return True

    async def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False

    async def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        expired_sessions = [
            sid for sid, session in self.sessions.items()
            if self._is_expired(session)
        ]

        for session_id in expired_sessions:
            await self.delete_session(session_id)

        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
        
        return len(expired_sessions)
    
    async def _cleanup_loop(self):
        """定期清理过期会话"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分钟清理一次
                await self.cleanup_expired_sessions()
            except Exception as e:
                logger.error(f"清理会话失败: {e}")
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        return len(self.sessions)
    
    def get_active_sessions(self, minutes: int = 5) -> List[str]:
        """获取最近活跃的会话"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        return [
            sid for sid, session in self.sessions.items()
            if session.get("last_activity", datetime.min) > cutoff_time
        ]

    def _is_expired(self, session: Dict) -> bool:
        """检查会话是否过期"""
        last_activity = session.get("last_activity")
        if not last_activity:
            return True
        return datetime.utcnow() - last_activity > self.session_timeout