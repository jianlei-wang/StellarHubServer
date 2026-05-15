import sys
import os
import logging
from pathlib import Path

# ========================================================
# PyInstaller 环境兼容性修复
# ========================================================
if getattr(sys, 'frozen', False):
    # 如果是打包后的 EXE 运行，sys._MEIPASS 是解压后的临时根目录
    bundle_dir = sys._MEIPASS
    # 确保 bundle_dir 在 sys.path 中，以便能正确导入 core, api, service, utils 等模块
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    
    # 修复工作目录，确保相对路径资源能被找到
    os.chdir(bundle_dir)

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from core.config import HOST, PORT, DEBUG, CORS_ORIGINS
from core.exception import APIException
from core.response import error
from api.file import router as file_router
from api.cog_api import router as cog_router
from utils.path_util import resource_path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("StellarHub")

# 初始化应用
app = FastAPI(
    title="StellarHub - 本地文件与COG服务",
    description="提供本地文件浏览与 TIFF 转 COG 服务的 Python 后端",
    version="1.0.0",
    debug=DEBUG
)

# 跨域中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "Accept-Ranges", "Content-Length", "Content-Type"],
)

@app.exception_handler(APIException)
async def handle_api_exception(request: Request, exc: APIException):
    """全局 API 异常处理"""
    return JSONResponse(status_code=200, content=error(exc.msg, exc.code))

# 挂载静态页面
web_dir = resource_path("web")
app.mount("/web", StaticFiles(directory=web_dir), name="web")

# ========================================================
# 突破性改进：模拟 Nginx 静态文件挂载
# ========================================================
# 自动探测并挂载本地盘符，解决 API 模式下 Range 请求不稳定问题
for drive in ['C', 'D', 'E', 'F', 'G', 'H']:
    drive_root = f"{drive}:/"
    if os.path.exists(drive_root):
        try:
            # 使用静态文件挂载模式，原生支持 206 Partial Content
            app.mount(f"/fs/{drive}", StaticFiles(directory=drive_root), name=f"fs_{drive}")
            logger.info(f"🚀 已挂载本地驱动器 {drive}: 到虚拟路径 /fs/{drive}")
        except Exception as e:
            logger.error(f"无法挂载驱动器 {drive}: {str(e)}")

# 路由挂载
app.include_router(file_router)
app.include_router(cog_router)

@app.get("/", tags=["Root"])
async def index():
    """健康检查与 API 概览"""
    return {
        "project": "StellarHubServer",
        "status": "running",
        "endpoints": {
            "file_service": ["/api/read-dir", "/api/read-text", "/api/file"],
            "cog_service": ["/cog/local/convert", "/cog/batch/local", "/cog/progress/{task_id}"]
        }
    }

if __name__ == "__main__":
    logger.info(f"✅ 服务启动: http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
