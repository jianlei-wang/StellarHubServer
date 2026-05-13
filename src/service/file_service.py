"""
文件系统相关业务逻辑模块
"""
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger("StellarHub.file_service")

def list_directory(path: str) -> List[Dict[str, Any]]:
    """
    列出目录下的所有文件和文件夹
    """
    if not os.path.exists(path):
        raise Exception(f"路径不存在: {path}")
    
    if not os.path.isdir(path):
        raise Exception(f"该路径不是一个目录: {path}")

    items = []
    try:
        for name in os.listdir(path):
            full_path = os.path.join(path, name)
            is_dir = os.path.isdir(full_path)
            items.append({
                "name": name,
                "path": full_path,
                "is_dir": is_dir,
                "size": os.path.getsize(full_path) if not is_dir else 0,
                "ext": os.path.splitext(name)[1].lower() if not is_dir else ""
            })
        
        # 排序：文件夹在前，文件名升序
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return items
    except PermissionError:
        logger.error(f"权限不足，无法访问目录: {path}")
        raise Exception("权限不足，无法访问该目录")
    except Exception as e:
        logger.error(f"遍历目录出错: {path}, 错误: {str(e)}")
        raise e

def read_text_file(path: str) -> str:
    """
    读取文本文件内容
    """
    if not os.path.exists(path):
        raise Exception("文件不存在")
    
    try:
        # 尝试使用 utf-8 读取，如果失败可以考虑自动检测编码
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # 如果 utf-8 失败，尝试 gbk (Windows 常用)
        try:
            with open(path, "r", encoding="gbk") as f:
                return f.read()
        except Exception:
            logger.error(f"无法解析文件编码: {path}")
            raise Exception("文件编码不支持，请确保是 UTF-8 或 GBK 格式")
    except Exception as e:
        logger.error(f"读取文件出错: {path}, 错误: {str(e)}")
        raise e
