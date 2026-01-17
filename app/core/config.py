from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "AI E-commerce Bot"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # development, staging, production

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # AI 服务配置
    ANTHROPIC_API_KEY: str = ""
    COPILOT_MODEL: str = "claude-sonnet-4-20250514"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7
    AI_TIMEOUT: int = 30  # AI 请求超时时间（秒）

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ecommerce.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # 缓存配置
    CACHE_TTL: int = 3600  # 1小时
    ENABLE_CACHE: bool = True

    # 搜索配置
    MAX_SEARCH_RESULTS: int = 20
    SEARCH_TIMEOUT: int = 5

    # 会话配置
    SESSION_TIMEOUT: int = 1800  # 30分钟
    MAX_CONVERSATION_HISTORY: int = 10

    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100  # 每分钟最大请求数
    RATE_LIMIT_WINDOW: int = 60  # 时间窗口（秒）

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # 忽略额外字段

    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == "development"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()