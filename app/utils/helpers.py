"""辅助工具函数"""
from typing import Any, Dict, Optional
from datetime import datetime
import hashlib
import json


def generate_id(prefix: str = "", length: int = 16) -> str:
    """生成唯一 ID"""
    import uuid
    unique_id = str(uuid.uuid4()).replace("-", "")[:length]
    return f"{prefix}{unique_id}" if prefix else unique_id


def hash_string(text: str) -> str:
    """生成字符串哈希"""
    return hashlib.sha256(text.encode()).hexdigest()


def safe_json_loads(text: str, default: Any = None) -> Any:
    """安全的 JSON 解析"""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def format_price(price: float, currency: str = "¥") -> str:
    """格式化价格"""
    return f"{currency}{price:,.2f}"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_current_timestamp() -> int:
    """获取当前时间戳（毫秒）"""
    return int(datetime.now().timestamp() * 1000)


def format_datetime(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def merge_dicts(*dicts: Dict) -> Dict:
    """合并多个字典"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def remove_none_values(data: Dict) -> Dict:
    """移除字典中的 None 值"""
    return {k: v for k, v in data.items() if v is not None}


def chunk_list(lst: list, chunk_size: int) -> list:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
