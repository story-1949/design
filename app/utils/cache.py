"""缓存工具"""
import json
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器（内存缓存，生产环境建议使用 Redis）"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            import time
            if key in self._ttl and time.time() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存"""
        self._cache[key] = value
        if ttl:
            import time
            self._ttl[key] = time.time() + ttl
    
    def delete(self, key: str):
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._ttl.clear()


# 全局缓存实例
cache = CacheManager()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """缓存装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func.__name__, key_prefix, args, kwargs)
            
            # 尝试从缓存获取
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            cache.set(cache_key, result, ttl)
            logger.debug(f"缓存存储: {cache_key}")
            
            return result
        return wrapper
    return decorator


def _generate_cache_key(func_name: str, prefix: str, args: tuple, kwargs: dict) -> str:
    """生成缓存键"""
    key_parts = [prefix, func_name]
    
    # 添加参数
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.append(json.dumps(kwargs, sort_keys=True))
    
    key_str = ":".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()
