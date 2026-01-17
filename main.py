from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from app.routes import search, chat
from app.core.config import settings
from app.core.database import init_db, close_db
from app.utils.logger import setup_logging
from app.utils.exceptions import AIEcommerceException

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    logger.info("🚀 AI E-commerce Bot 启动中...")
    try:
        init_db()
        
        # 启动会话清理任务
        from app.services.session_manager import SessionManager
        session_manager = SessionManager()
        session_manager.start_cleanup_task()
        
        logger.info(f"📝 API 文档: http://{settings.HOST}:{settings.PORT}/docs")
        logger.info(f"🌍 环境: {settings.ENVIRONMENT}")
        yield
    finally:
        # 关闭
        logger.info("👋 AI E-commerce Bot 关闭中...")
        close_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="智能电商助手 API - 提供商品搜索、智能对话、订单管理等功能",
    version=settings.VERSION,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 处理请求
    response = await call_next(request)
    
    # 计算耗时
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} "
        f"- {response.status_code} - {process_time:.3f}s"
    )
    
    # 添加响应头
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# 全局异常处理
@app.exception_handler(AIEcommerceException)
async def custom_exception_handler(request: Request, exc: AIEcommerceException):
    """自定义异常处理"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.code,
            "message": exc.message,
            "path": str(request.url)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "message": "请求参数验证失败",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "服务器内部错误" if settings.is_production() else str(exc)
        }
    )


# 注册路由
app.include_router(search.router, prefix="/api/v1", tags=["商品搜索"])
app.include_router(chat.router, prefix="/api/v1", tags=["智能对话"])


@app.get("/", summary="根路径")
async def root():
    """API 根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production() else None,
        "health": "/health"
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )