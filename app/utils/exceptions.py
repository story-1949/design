"""自定义异常"""


class AIEcommerceException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SessionNotFoundException(AIEcommerceException):
    """会话不存在"""
    def __init__(self, session_id: str):
        super().__init__(
            message=f"会话不存在: {session_id}",
            code="SESSION_NOT_FOUND"
        )


class ProductNotFoundException(AIEcommerceException):
    """商品不存在"""
    def __init__(self, product_id: str):
        super().__init__(
            message=f"商品不存在: {product_id}",
            code="PRODUCT_NOT_FOUND"
        )


class RateLimitExceededException(AIEcommerceException):
    """超过限流"""
    def __init__(self):
        super().__init__(
            message="请求过于频繁，请稍后再试",
            code="RATE_LIMIT_EXCEEDED"
        )


class AIServiceException(AIEcommerceException):
    """AI 服务异常"""
    def __init__(self, message: str):
        super().__init__(
            message=f"AI 服务错误: {message}",
            code="AI_SERVICE_ERROR"
        )


class ValidationException(AIEcommerceException):
    """验证异常"""
    def __init__(self, message: str):
        super().__init__(
            message=f"验证失败: {message}",
            code="VALIDATION_ERROR"
        )
