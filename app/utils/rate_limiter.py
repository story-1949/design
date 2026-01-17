"""限流工具"""
from typing import Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """简单的限流器（基于内存，生产环境建议使用 Redis）"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Args:
            max_requests: 时间窗口内最大请求数
            window_seconds: 时间窗口（秒）
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self._requests: Dict[str, list] = {}
    
    def is_allowed(self, key: str) -> bool:
        """检查是否允许请求"""
        now = datetime.now()
        
        # 初始化或清理过期记录
        if key not in self._requests:
            self._requests[key] = []
        
        # 移除过期的请求记录
        cutoff_time = now - self.window
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff_time
        ]
        
        # 检查是否超过限制
        if len(self._requests[key]) >= self.max_requests:
            logger.warning(f"限流触发: {key}")
            return False
        
        # 记录本次请求
        self._requests[key].append(now)
        return True
    
    def get_remaining(self, key: str) -> int:
        """获取剩余请求次数"""
        if key not in self._requests:
            return self.max_requests
        
        now = datetime.now()
        cutoff_time = now - self.window
        valid_requests = [
            req_time for req_time in self._requests[key]
            if req_time > cutoff_time
        ]
        
        return max(0, self.max_requests - len(valid_requests))


# 全局限流器实例
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)
