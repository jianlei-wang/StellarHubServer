import os
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

from utils.progress_util import update_task

logger = logging.getLogger("StellarHub.cog_utils")

# PROJ_LIB 路径配置，确保在某些环境下能够找到坐标转换引擎
BASE_DIR = Path(__file__).resolve().parent.parent
PROJ_DIR = BASE_DIR / "proj"
if PROJ_DIR.exists():
    os.environ["PROJ_LIB"] = str(PROJ_DIR)

def tif_to_cog(
    input_path: str, 
    output_path: str, 
    task_id: str, 
    dst_crs: Optional[str] = None,
    profile: str = "deflate",
    overview_level: int = 6,
    blocksize: int = 512,
    resampling: str = "bilinear"
) -> bool:
    """
    将 TIFF 文件转换为 COG 格式，支持自定义参数。
    :param input_path: 输入文件路径
    :param output_path: 输出文件路径
    :param task_id: 任务 ID
    :param dst_crs: 目标坐标系 (EPSG:4326等)
    :param profile: 压缩配置文件 (deflate, lzw, packbits 等)
    :param overview_level: 金字塔层级
    :param blocksize: 瓦片大小
    :param resampling: 重采样算法 (nearest, bilinear, cubic, lanczos 等)
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    temp_file = output_file.with_suffix(output_file.suffix + ".temp.tif")

    # 映射重采样算法字符串到 rasterio 枚举
    resampling_map = {
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic,
        "lanczos": Resampling.lanczos,
        "average": Resampling.average
    }
    resampling_method = resampling_map.get(resampling.lower(), Resampling.bilinear)

    try:
        update_task(task_id, 5, "running", "读取TIF文件...")

        with rasterio.Env():
            with rasterio.open(input_path) as src:
                src_crs = src.crs
                width, height = src.width, src.height
                count = src.count
                dtype = src.dtypes[0]

                logger.info(f"读取文件: {input_path} (W:{width}, H:{height}, B:{count}, CRS:{src_crs})")
                update_task(task_id, 10, "running", f"读取成功: 波段数={count}, 坐标系={src_crs}")

                # 目标坐标系解析
                target_crs = src_crs
                if dst_crs and dst_crs.strip():
                    try:
                        target_crs = rasterio.crs.CRS.from_string(dst_crs)
                        update_task(task_id, 15, "running", f"目标坐标系已设置为: {dst_crs}")
                    except Exception as e:
                        logger.error(f"无效坐标系: {dst_crs}, 错误: {str(e)}")
                        update_task(task_id, 0, "failed", f"无效坐标系: {dst_crs}")
                        return False

                # 配置 COG 参数
                cog_config = cog_profiles.get(profile)
                cog_config.update({
                    "blockxsize": blocksize,
                    "blockysize": blocksize,
                    "BIGTIFF": "IF_SAFER"  # 启用 BigTIFF 支持以处理超大文件
                })

                # 无需重投影，直接生成 COG
                if target_crs == src_crs:
                    update_task(task_id, 25, "running", "坐标系一致，正在生成 COG 瓦片...")
                    cog_translate(
                        src,
                        str(output_file),
                        cog_config,
                        overview_level=overview_level,
                        quiet=True
                    )
                    update_task(task_id, 100, "completed", f"✅ 转换完成: {output_path}")
                    return True

                # 需要重投影
                update_task(task_id, 20, "running", f"正在进行重投影转换 (算法: {resampling})...")

                # 计算变换参数
                transform, new_w, new_h = calculate_default_transform(
                    src_crs, target_crs, width, height, *src.bounds
                )

                new_meta = src.meta.copy()
                new_meta.update({
                    "crs": target_crs,
                    "transform": transform,
                    "width": new_w,
                    "height": new_h,
                    "BIGTIFF": "IF_SAFER"  # 临时文件也启用 BigTIFF 支持
                })

                # 重投影所有波段
                bands = []
                for i in range(1, count + 1):
                    update_task(task_id, 20 + int(10 * i / count), "running", f"重投影波段 {i}/{count}")
                    src_band = src.read(i)
                    dst_band = np.zeros((new_h, new_w), dtype=dtype)

                    reproject(
                        source=src_band,
                        src_crs=src_crs,
                        src_transform=src.transform,
                        destination=dst_band,
                        dst_crs=target_crs,
                        dst_transform=transform,
                        resampling=resampling_method
                    )
                    bands.append(dst_band)

                # 写入临时文件
                update_task(task_id, 35, "running", "写入临时重投影数据...")
                with rasterio.open(str(temp_file), "w", **new_meta) as dst:
                    for idx, band in enumerate(bands, 1):
                        dst.write(band, idx)

                # 从临时文件转换为 COG
                update_task(task_id, 40, "running", "正在生成 COG 瓦片...")
                with rasterio.open(str(temp_file)) as tmp_src:
                    cog_translate(
                        tmp_src,
                        str(output_file),
                        cog_config,
                        overview_level=overview_level,
                        quiet=True
                    )

                # 清理临时文件
                if temp_file.exists():
                    temp_file.unlink()

                update_task(task_id, 100, "completed", f"✅ 转换完成: {output_path}")
                return True

    except Exception as e:
        logger.error(f"转换失败: {input_path}, 错误: {str(e)}", exc_info=True)
        update_task(task_id, 0, "failed", f"❌ 转换失败: {str(e)}")
        # 发生异常时也尝试清理临时文件
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False