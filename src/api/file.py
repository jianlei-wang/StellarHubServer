import logging
from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from core.response import success, error
from service.file_service import list_directory, read_text_file

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
        return error(str(e))

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
        return error(str(e))

@router.get("/api/file", summary="获取文件流")
async def get_file(path: str = Query(..., description="文件路径")):
    """
    直接返回文件流，用于下载或展示图片等
    """
    try:
        return FileResponse(path)
    except Exception as e:
        logger.error(f"获取文件流失败: {path}, 错误: {str(e)}")
        return error("文件获取失败")
