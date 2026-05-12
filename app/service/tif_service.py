import os
from typing import Optional

import rasterio
from rasterio.shutil import copy as rasterio_copy


def convert_tif_to_cog(input_path: str, output_path: Optional[str] = None) -> str:
    """将 TIF/TIFF 文件转换为 Cloud Optimized GeoTIFF (COG)。"""
    if not os.path.exists(input_path):
        raise Exception("输入文件不存在")

    lower_name = input_path.lower()
    if not lower_name.endswith(('.tif', '.tiff')):
        raise Exception("仅支持 TIF/TIFF 文件")

    if output_path:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
    else:
        base_name, _ = os.path.splitext(input_path)
        output_path = f"{base_name}_cog.tif"

    with rasterio.open(input_path) as src:
        rasterio_copy(src, output_path, driver="COG", compress="deflate")

    return os.path.abspath(output_path)
