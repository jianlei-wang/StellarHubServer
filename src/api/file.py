import logging
import os
from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
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

@router.get("/api/file", summary="获取文件流（支持 HTTP Range 请求）")
async def get_file(request: Request, path: str = Query(..., description="文件路径")):
    """
    文件流接口，完整支持 HTTP Range 请求（206 Partial Content）。
    COG/GeoTIFF 等栅格数据必须使用此接口，geotiff.js 依赖 Range 请求实现按需读取。
    """
    try:
        norm_path = normalize_path(path)
        if not os.path.exists(norm_path) or not os.path.isfile(norm_path):
            return JSONResponse(status_code=404, content=error("文件不存在", code=404))
        
        file_size = os.path.getsize(norm_path)
        
        # 针对 TIFF 明确类型
        media_type = "image/tiff" if norm_path.lower().endswith(('.tif', '.tiff')) else "application/octet-stream"
        
        # 检查是否包含 Range 请求头
        range_header = request.headers.get("range")
        
        if range_header:
            # 解析 Range 头（例如: "bytes=0-1023" 或 "bytes=500-"）
            import re
            range_match = re.search(r'bytes=(\d*)-(\d*)', range_header)
            if not range_match:
                return JSONResponse(status_code=400, content=error("无效的 Range 请求头", code=400))
            
            start_str, end_str = range_match.groups()
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
            
            # 验证范围合法性
            if start >= file_size or end >= file_size or start > end:
                return JSONResponse(
                    status_code=416, 
                    content=error("请求范围超出文件大小", code=416),
                    headers={"Content-Range": f"bytes */{file_size}"}
                )
            
            # 限制单次读取最大 10MB，防止恶意请求
            max_chunk = 10 * 1024 * 1024
            if end - start + 1 > max_chunk:
                end = start + max_chunk - 1
            
            content_length = end - start + 1
            
            # 异步文件读取生成器
            async def file_iterator():
                with open(norm_path, 'rb') as f:
                    f.seek(start)
                    remaining = content_length
                    chunk_size = 8192  # 8KB 分块读取
                    while remaining > 0:
                        chunk = f.read(min(chunk_size, remaining))
                        if not chunk:
                            break
                        yield chunk
                        remaining -= len(chunk)
            
            # 返回 206 Partial Content
            return StreamingResponse(
                file_iterator(),
                status_code=206,
                media_type=media_type,
                headers={
                    "Content-Range": f"bytes {start}-{end}/{file_size}",
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(content_length),
                }
            )
        else:
            # 无 Range 头，返回完整文件
            async def full_file_iterator():
                with open(norm_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        yield chunk
            
            return StreamingResponse(
                full_file_iterator(),
                status_code=200,
                media_type=media_type,
                headers={
                    "Accept-Ranges": "bytes",
                    "Content-Length": str(file_size),
                }
            )
    except Exception as e:
        logger.error(f"获取文件流失败: {path}, 错误: {str(e)}")
        return JSONResponse(status_code=500, content=error("文件获取失败", code=500))
