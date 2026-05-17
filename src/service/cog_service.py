import os
import uuid
import threading
import logging
from datetime import datetime
from typing import List, Optional
from utils.cog_utils import tif_to_cog
from utils.progress_util import init_task, update_task

logger = logging.getLogger("StellarHub.cog_service")

def _generate_output_filename(input_path: str, output_filename: str = "") -> str:
    """
    生成输出文件名。
    - 留空：自动生成 {原文件名}_{时间戳}_cog.tif
    - 指定名称：直接使用（.tif后缀可选，缺失自动补全）
    """
    if output_filename and output_filename.strip():
        # 用户指定了文件名
        name = output_filename.strip()
        if not name.lower().endswith(('.tif', '.tiff')):
            name += '.tif'
        return name

    # 自动生成: {原文件名}_{时间戳}_cog.tif
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{base_name}_{timestamp}_cog.tif"

def convert_single(
    input_path: str, 
    output_dir: str = "", 
    dst_crs: str = "",
    output_filename: str = "",
    **kwargs
) -> str:
    """
    处理单个 TIFF 转换任务
    :param input_path: 输入文件路径
    :param output_dir: 输出目录
    :param dst_crs: 目标坐标系
    :param output_filename: 输出文件名（留空自动生成 {原文件名}_{时间戳}_cog.tif）
    :param kwargs: 其他 COG 转换参数 (profile, overview_level, blocksize, resampling, etc.)
    :return: 任务 ID
    """
    task_id = str(uuid.uuid4())
    init_task(task_id, input_path=input_path)

    # 输出目录处理：默认使用输入文件所在目录
    if not output_dir or not output_dir.strip():
        output_dir = os.path.dirname(input_path)

    try:
        os.makedirs(output_dir, exist_ok=True)

        # 生成输出文件名
        filename = _generate_output_filename(input_path, output_filename)
        output_path = os.path.join(output_dir, filename)

        logger.info(f"创建转换任务: {task_id}, 输入: {input_path}, 输出: {output_path}, 参数: {kwargs}")

        # 将 output_path 写入任务信息，便于后续下载
        update_task(task_id, 0, "pending", "任务已创建", output_path=output_path)

        def run_task():
            tif_to_cog(input_path, output_path, task_id, dst_crs, **kwargs)

        # 使用守护线程运行转换任务
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        
    except Exception as e:
        logger.error(f"任务启动失败: {str(e)}")
        update_task(task_id, 0, "failed", f"启动失败: {str(e)}")

    return task_id

def batch_convert(
    file_paths: List[str], 
    output_dir: str = "", 
    dst_crs: str = "",
    output_filename: str = "",
    **kwargs
) -> List[str]:
    """
    处理批量 TIFF 转换任务
    """
    task_ids = []
    for path in file_paths:
        if os.path.exists(path) and path.lower().endswith((".tif", ".tiff")):
            task_ids.append(convert_single(path, output_dir, dst_crs, output_filename=output_filename, **kwargs))
        else:
            logger.warning(f"跳过无效文件: {path}")
    return task_ids