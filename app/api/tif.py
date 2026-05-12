from typing import Optional

from fastapi import APIRouter, Query
from app.core.response import success, error
from app.service.tif_service import convert_tif_to_cog

router = APIRouter()


@router.post("/api/convert-cog")
def convert_cog(input_path: str = Query(...), output_path: Optional[str] = Query(None)):
    """转换本地 TIF/TIFF 文件为 COG，并返回生成文件路径。"""
    try:
        cog_path = convert_tif_to_cog(input_path, output_path)
        return success({"cog_path": cog_path})
    except Exception as e:
        return error(str(e))
