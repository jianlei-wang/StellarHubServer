"""
统一响应格式处理模块
"""
from typing import Any, Dict, Optional

def success(data: Any = None, msg: str = "success") -> Dict[str, Any]:
    """
    成功响应格式
    """
    return {
        "code": 200,
        "msg": msg,
        "data": data
    }

def error(msg: str = "error", code: int = 400) -> Dict[str, Any]:
    """
    失败响应格式
    """
    return {
        "code": code,
        "msg": msg,
        "data": None
    }
