
# 本地文件服务化工具

基于 FastAPI 构建的轻量级本地文件服务，支持 Web 页面调用、接口管理、无限扩展。

## 启动命令

1. 安装依赖：pip install -r requirements.txt
2. 启动服务：python main.py

## 访问地址

- 服务地址：<http://127.0.0.1:10086>
- Web管理端：<http://127.0.0.1:10086/web/index.html>
- 接口文档：<http://127.0.0.1:10086/docs>

## 功能列表

1. 读取本地文件夹
2. 读取文本文件（UTF-8/GBK兼容）
3. 预览/下载任意文件
4. 本地 TIF/TIFF 转换为 COG (Cloud Optimized GeoTIFF)

## 结构

``` plaintext
StellarHubServer/
├── app/                     # 核心业务模块（未来所有新功能都放这里）
│   ├── __init__.py          # 包标识
│   ├── core/                # 系统核心（配置、异常、响应）
│   │   ├── __init__.py
│   │   ├── config.py        # 全局配置（端口、IP、跨域等）
│   │   ├── exception.py     # 全局异常处理
│   │   └── response.py      # 统一响应格式
│   ├── api/                 # 接口模块（按功能拆分）
│   │   ├── __init__.py
│   │   ├── file.py          # 文件服务接口
│   │   └── tif.py           # TIF 转 COG 接口
│   ├── service/             # 业务服务模块
│   │   ├── __init__.py
│   │   ├── file_service.py  # 文件操作服务
│   │   └── tif_service.py   # TIF 转 COG 服务
│   └── utils/               # 工具类（通用方法）
│       ├── __init__.py
│       └── path_util.py     # 资源路径兼容工具
├── web/                     # Web前端页面（后续可直接放Vue/HTML）
│   └── index.html           # 测试用Web页面
├── main.py                  # 项目启动入口
├── requirements.txt         # 依赖声明
└── README.md                # 使用说明
```
