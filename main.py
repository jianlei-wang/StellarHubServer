import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# ========================
# 【关键】显式 import 所有自定义包，让 PyInstaller 扫描到
# 不需要使用它们，只要导入就够了
# ========================
import app

# 正常导入使用
from app.core.config import HOST, PORT, DEBUG, CORS_ORIGINS
from app.core.exception import APIException
from app.core.response import error
from app.api.file import router
from app.api.tif import router as tif_router
from app.utils.path_util import resource_path


# 初始化应用
app = FastAPI(title="本地文件服务", debug=DEBUG)

# 跨域（终极解决，支持任意前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常捕获


@app.exception_handler(APIException)
async def handle_api_exception(request: Request, exc: APIException):
    return JSONResponse(status_code=200, content=error(exc.msg, exc.code))

# 挂载静态页面
web_dir = resource_path("web")
app.mount("/web", StaticFiles(directory=web_dir), name="web")

# 挂载文件服务接口（对齐 main.go）
app.include_router(router)
app.include_router(tif_router)

# 健康检查


@app.get("/")
def index():
    return {
        "name": "本地文件服务",
        "status": "running",
        "api": ["/api/read-dir", "/api/read-text", "/api/file", "/api/convert-cog"]
    }


# 启动
if __name__ == "__main__":
    print(f"✅ 服务启动: http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)
