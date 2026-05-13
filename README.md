# StellarHubServer

基于 Python FastAPI 的本地文件服务与 TIFF 转 COG 工具。

## 快速开始

1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：`python src/main.py`
3. 访问页面：`http://127.0.0.1:10086/web/index.html`

## 详细文档

请参阅 [项目说明文档](docs/project_docs.md) 获取详细的结构说明、API 指南及优化细节。

## 核心功能

- **文件浏览**：远程查看服务器本地目录与文件。
- **COG 转换**：TIFF 转换为 Cloud Optimized GeoTIFF，支持重投影。
- **进度追踪**：支持大文件转换的实时进度查询。

## 优化记录 (2026-05-13)

- 项目结构重构，引入 `src/` 标准布局。
- 全面适配 PEP 8 编码规范。
- 强化模块化设计，解耦 API 与业务逻辑。
- 完善日志记录与异常捕获机制。
