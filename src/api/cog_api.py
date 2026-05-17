import os
from typing import List, Optional
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, FileResponse
from service.cog_service import convert_single, batch_convert
from utils.progress_util import get_task

router = APIRouter(prefix="/cog", tags=["COG转换"])

@router.post("/local/convert", summary="单文件本地转换")
async def local_convert(
    file_path: str = Form(..., description="TIF文件绝对路径"),
    output_dir: str = Form("", description="输出目录，默认同输入目录"),
    output_filename: str = Form("", description="输出文件名，默认: {原文件名}_{时间戳}_cog.tif"),
    dst_crs: str = Form("", description="目标坐标系 (EPSG:4326等)"),
    profile: str = Form("deflate", description="压缩配置文件 (deflate, lzw, packbits, jpeg, webp, zstd, lzma, none)"),
    overview_level: int = Form(6, description="金字塔层级 (0-10)"),
    blocksize: int = Form(512, description="瓦片大小 (128/256/512/1024)"),
    resampling: str = Form("bilinear", description="重采样算法 (nearest, bilinear, cubic, lanczos, average)"),
    overviews_resampling: str = Form("", description="金字塔重采样算法，默认与resampling相同 (nearest, bilinear, cubic, lanczos, average)"),
    nodata: float = Form(None, description="NoData值，留空则自动读取源文件"),
    dtype: str = Form("", description="输出数据类型 (uint8, uint16, int16, uint32, int32, float32, float64)"),
    bigtiff: str = Form("IF_SAFER", description="BigTIFF策略 (YES, NO, IF_NEEDED, IF_SAFER)"),
    quality: int = Form(None, description="JPEG/WebP压缩质量 (1-100)，仅jpeg/webp压缩时有效"),
):
    """
    启动单个 TIFF 文件的 COG 转换任务，支持详细参数配置。

    输出文件名规则：
    - 留空：自动生成 {原文件名}_{时间戳}_cog.tif
    - 指定名称：直接使用指定名称（.tif后缀可选，缺失自动补全）
    """
    if not os.path.exists(file_path):
        return JSONResponse(status_code=400, content={"code": 400, "msg": "输入文件不存在"})

    kwargs = {
        "output_filename": output_filename,
        "profile": profile,
        "overview_level": overview_level,
        "blocksize": blocksize,
        "resampling": resampling,
        "overviews_resampling": overviews_resampling,
        "nodata": nodata,
        "dtype": dtype,
        "bigtiff": bigtiff,
    }
    if quality is not None:
        kwargs["quality"] = quality

    task_id = convert_single(file_path, output_dir, dst_crs, **kwargs)
    return {"code": 200, "task_id": task_id}

@router.post("/batch/local", summary="批量本地转换")
async def batch_local(
    file_paths: List[str],
    output_dir: str = Form("", description="输出目录"),
    output_filename: str = Form("", description="输出文件名规则，批量时不建议指定具体名称"),
    dst_crs: str = Form("", description="目标坐标系"),
    profile: str = Form("deflate", description="压缩配置"),
    overview_level: int = Form(6, description="金字塔层级"),
    blocksize: int = Form(512, description="瓦片大小"),
    resampling: str = Form("bilinear", description="重采样算法"),
    overviews_resampling: str = Form("", description="金字塔重采样算法"),
    nodata: float = Form(None, description="NoData值"),
    dtype: str = Form("", description="输出数据类型"),
    bigtiff: str = Form("IF_SAFER", description="BigTIFF策略"),
    quality: int = Form(None, description="JPEG/WebP压缩质量"),
):
    """
    启动多个 TIFF 文件的批量转换任务
    """
    kwargs = {
        "output_filename": output_filename,
        "profile": profile,
        "overview_level": overview_level,
        "blocksize": blocksize,
        "resampling": resampling,
        "overviews_resampling": overviews_resampling,
        "nodata": nodata,
        "dtype": dtype,
        "bigtiff": bigtiff,
    }
    if quality is not None:
        kwargs["quality"] = quality

    tasks = batch_convert(file_paths, output_dir, dst_crs, **kwargs)
    return {"code": 200, "tasks": tasks}

@router.get("/progress/{task_id}", summary="查询转换进度")
async def progress(task_id: str):
    """
    根据任务 ID 获取转换状态和进度
    """
    return get_task(task_id)

@router.get("/result/{task_id}", summary="下载/查看转换结果")
async def result(task_id: str):
    """
    获取转换后的 COG 文件。如果未完成或不存在则返回错误。
    """
    task = get_task(task_id)
    path = task.get("output_path")

    if not path or not os.path.exists(path):
        return JSONResponse(status_code=400, content={"code": 400, "msg": "文件不存在或转换未完成"})

    return FileResponse(path, filename=os.path.basename(path))