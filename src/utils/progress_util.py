"""
任务进度管理工具模块
"""
import time
from typing import Dict, Any

# 内存中的任务状态字典 (生产环境建议使用 Redis 或 数据库)
_tasks: Dict[str, Dict[str, Any]] = {}

def init_task(task_id: str):
    """
    初始化一个新任务
    """
    _tasks[task_id] = {
        "task_id": task_id,
        "progress": 0,
        "status": "pending",
        "msg": "任务已创建",
        "start_time": time.time(),
        "update_time": time.time(),
        "output_path": None
    }

def update_task(task_id: str, progress: int, status: str, msg: str, output_path: str = None):
    """
    更新任务进度和状态
    """
    if task_id in _tasks:
        _tasks[task_id].update({
            "progress": progress,
            "status": status,
            "msg": msg,
            "update_time": time.time()
        })
        if output_path:
            _tasks[task_id]["output_path"] = output_path

def get_task(task_id: str) -> Dict[str, Any]:
    """
    获取任务详情
    """
    return _tasks.get(task_id, {"code": 404, "msg": "任务未找到"})

def clear_old_tasks(timeout: int = 3600):
    """
    清理超时的旧任务（防止内存溢出）
    """
    now = time.time()
    to_delete = [
        tid for tid, task in _tasks.items() 
        if now - task["update_time"] > timeout
    ]
    for tid in to_delete:
        del _tasks[tid]