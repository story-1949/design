from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 数据库引擎配置
engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

# SQLite 特殊配置
if "sqlite" in settings.DATABASE_URL:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL/MySQL 连接池配置
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,  # 连接前检查
        "pool_recycle": 3600,  # 1小时回收连接
    })

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 数据模型
class Product(Base):
    """商品表"""
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category = Column(String, index=True)
    image_url = Column(String)
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 复合索引
    __table_args__ = (
        Index('idx_category_price', 'category', 'price'),
        Index('idx_rating_reviews', 'rating', 'reviews_count'),
    )


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    product_id = Column(String, index=True)
    quantity = Column(Integer)
    total_price = Column(Float)
    status = Column(String)  # pending, paid, shipped, delivered, cancelled
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.now)


class ChatHistory(Base):
    """聊天历史表"""
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=True)
    role = Column(String, nullable=False)  # user or assistant
    content = Column(Text, nullable=False)
    intent = Column(String)  # 用户意图
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
    )


# 创建所有表
def init_db():
    """初始化数据库"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


# 获取数据库会话
def get_db():
    """获取数据库会话（依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()


# 关闭数据库连接
def close_db():
    """关闭数据库连接"""
    try:
        engine.dispose()
        logger.info("数据库连接已关闭")
    except Exception as e:
        logger.error(f"关闭数据库连接失败: {e}")