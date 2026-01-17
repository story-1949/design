"""限流中间件"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.rate_limiter import rate_limiter
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """全局限流中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和文档路径
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # 如果未启用限流，直接通过
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # 获取客户端标识（IP 地址）
        client_ip = request.client.host if request.client else "unknown"
        
        # 检查限流
        if not rate_limiter.is_allowed(client_ip):
            logger.warning(f"限流触发: {client_ip} - {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )
        
        # 添加限流信息到响应头
        response = await call_next(request)
        remaining = rate_limiter.get_remaining(client_ip)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        
        return response
