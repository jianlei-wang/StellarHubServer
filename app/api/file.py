from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from app.core.response import success, error
from app.service.file_service import list_directory, read_text_file

router = APIRouter()

# 1. 读取目录（对齐 main.go /api/read-dir）


@router.get("/api/read-dir")
def read_dir(path: str = Query(...)):
    try:
        data = list_directory(path)
        return success(data)
    except Exception as e:
        return error(str(e))

# 2. 读取文本（对齐 main.go /api/read-text）


@router.get("/api/read-text")
def read_text(path: str = Query(...)):
    try:
        content = read_text_file(path)
        return success(content)
    except Exception as e:
        return error(str(e))

# 3. 获取文件（对齐 main.go /api/file）


@router.get("/api/file")
def get_file(path: str = Query(...)):
    return FileResponse(path)
