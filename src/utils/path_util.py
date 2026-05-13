"""
路径处理工具模块
"""
import os
import sys
from pathlib import Path

def resource_path(relative_path: str) -> str:
    """
    获取资源的绝对路径，兼容 PyInstaller 打包后的路径
    """
    try:
        # PyInstaller 创建临时文件夹并存储路径在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        # 非打包环境下使用项目根目录
        # 这里假设 path_util.py 在 src/utils/ 下
        base_path = Path(__file__).resolve().parent.parent.parent

    target_path = Path(base_path) / relative_path
    return str(target_path)
