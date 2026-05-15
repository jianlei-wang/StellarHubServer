import logging
import os
from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from core.response import success, error
from service.file_service import list_directory, read_text_file
from utils.path_util import normalize_path

router = APIRouter(tags=["文件服务"])
logger = logging.getLogger("StellarHub.file")

@router.get("/api/read-dir", summary="读取目录内容")
async def read_dir(path: str = Query(..., description="要读取的目录路径")):
    """
    获取指定目录下的文件和文件夹列表
    """
    try:
        data = list_directory(path)
        return success(data)
    except Exception as e:
        logger.error(f"读取目录失败: {path}, 错误: {str(e)}")
        return error(str(e), code=400)

@router.get("/api/read-text", summary="读取文本文件内容")
async def read_text(path: str = Query(..., description="文本文件路径")):
    """
    读取并返回指定文本文件的内容
    """
    try:
        content = read_text_file(path)
        return success(content)
    except Exception as e:
        logger.error(f"读取文本文件失败: {path}, 错误: {str(e)}")
        return error(str(e), code=400)

@router.get("/api/file", summary="获取文件流")
async def get_file(request: Request, path: str = Query(..., description="文件路径")):
    """
    备用文件流接口。对于 COG 等大文件，建议使用 /fs/{drive}/... 挂载路径。
    """
    try:
        norm_path = normalize_path(path)
        if not os.path.exists(norm_path) or not os.path.isfile(norm_path):
            return JSONResponse(status_code=404, content=error("文件不存在", code=404))
            
        stat_result = os.stat(norm_path)
        
        # 针对 TIFF 明确类型
        media_type = "image/tiff" if norm_path.lower().endswith(('.tif', '.tiff')) else None
        
        # FileResponse 配合 stat_result 可以支持基础的 Range 请求
        return FileResponse(
            norm_path, 
            media_type=media_type,
            stat_result=stat_result
        )
    except Exception as e:
        logger.error(f"获取文件流失败: {path}, 错误: {str(e)}")
        return JSONResponse(status_code=500, content=error("文件获取失败", code=500))
