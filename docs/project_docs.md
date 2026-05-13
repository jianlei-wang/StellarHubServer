# StellarHubServer 项目说明文档

## 1. 项目概述
StellarHubServer 是一个基于 Python FastAPI 开发的高性能后端服务，旨在提供以下核心功能：
- **本地文件服务化**：通过 API 接口远程浏览、读取本地文件系统内容，支持文本文件预览与文件流下载。
- **TIFF 转换 COG**：支持将普通的 GeoTIFF 文件转换为云优化 GeoTIFF (Cloud Optimized GeoTIFF, COG) 格式，并支持坐标系重投影转换。

项目设计目标是：结构清晰、易于扩展、符合 PEP 8 规范，且能够通过 PyInstaller 等工具打包为独立运行的可执行文件。

**依赖环境**：
- Python 3.8+
- 核心库：FastAPI, Rasterio, Rio-cogeo, Uvicorn

---

## 2. 项目结构说明
优化后的项目遵循标准的 Python 项目目录规范，将源代码、配置、文档和测试完全分离：

```text
StellarHubServer/
├── src/                    # 源代码根目录
│   ├── api/                # 接口层：定义 FastAPI 路由与请求处理
│   │   ├── cog_api.py      # COG 转换相关接口
│   │   └── file.py         # 文件浏览相关接口
│   ├── core/               # 核心层：全局配置、异常处理、响应封装
│   │   ├── config.py       # 服务端口、跨域等配置
│   │   ├── exception.py    # 自定义异常类
│   │   └── response.py     # 统一响应格式
│   ├── service/            # 业务逻辑层：核心业务逻辑实现
│   │   ├── cog_service.py  # COG 转换业务调度（多线程）
│   │   └── file_service.py # 文件系统操作逻辑
│   ├── utils/              # 工具类层：通用功能插件
│   │   ├── cog_utils.py    # 栅格数据处理工具
│   │   ├── path_util.py    # 路径兼容性工具
│   │   └── progress_util.py# 任务进度管理工具
│   ├── proj/               # 坐标转换引擎依赖库 (proj.db)
│   └── main.py             # 项目入口文件
├── config/                 # 外部配置文件目录 (可选)
├── docs/                   # 项目文档目录
├── tests/                  # 单元测试用例目录
├── web/                    # 静态前端页面
├── requirements.txt        # 项目依赖清单
└── README.md               # 项目快速入门指南
```

---

## 3. 模块化说明
项目采用经典的 **API-Service-Utils** 三层架构，确保各组件职责单一、高内聚低耦合：

- **API 层**：仅负责解析请求、校验参数并调用 Service 层。不包含任何业务逻辑。
- **Service 层**：负责处理业务流程。例如，`cog_service` 负责管理任务 ID、初始化进度条、并启动后台线程执行转换。
- **Utils 层**：负责底层的技术细节实现。例如，`cog_utils` 利用 `rasterio` 处理复杂的地理空间数据转换。
- **__init__.py**：每个目录下均包含该文件，使目录成为规范的 Python 包，便于模块化导入。

---

## 4. 优化说明
本次优化对原有项目进行了全方位的重构与清理：

- **代码清洗**：
  - 移除了所有冗余的空行、未使用的变量及废弃的调试注释。
  - 清理了未使用的 `import` 语句，减少了模块加载开销。
- **PEP 8 规范化**：
  - 统一使用 4 空格缩进，禁止使用制表符。
  - 函数与变量命名统一采用 `snake_case`，类名采用 `PascalCase`。
  - 运算符与逗号前后增加了规范的空格，提升代码可读性。
- **结构调整**：
  - 将所有源码移入 `src/` 目录，实现了源码与配置的分离。
  - 规范了模块导入路径，解决了潜在的循环依赖问题。
- **性能与鲁棒性**：
  - 引入了 `logging` 模块替代 `print`，实现规范的日志记录。
  - 优化了 TIFF 转换逻辑，通过临时文件机制避免了内存锁定问题。
  - 增加了对 GBK 编码文件的兼容性支持（Windows 环境）。

---

## 5. 维护与扩展指南
### 后续维护建议
- **代码规范**：所有新增代码必须遵循 PEP 8 规范，建议使用 `flake8` 或 `black` 进行静态检查。
- **异常处理**：避免使用 `bare except`，应尽量捕获具体的异常类型，并记录日志。
- **任务管理**：当前进度管理在内存中，若后续任务量极大，建议将 `progress_util.py` 中的存储改为 Redis。

### 功能扩展方法
- **新增接口**：在 `src/api/` 下创建新的 `.py` 文件，定义 `APIRouter`，并在 `src/main.py` 中挂载。
- **新增业务**：在 `src/service/` 下编写对应的 Service 函数，保持逻辑独立。

---

## 6. 运行说明
### 运行环境
- 操作系统：Windows / Linux / macOS
- Python 版本：3.8+

### 搭建步骤
1. **创建虚拟环境** (推荐)：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   .\venv\Scripts\activate   # Windows
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **启动服务**：
   ```bash
   python src/main.py
   ```
   服务默认启动在 `http://127.0.0.1:10086`。

### 接口预览
- 根目录 (API 概览): `GET /`
- 目录读取: `GET /api/read-dir?path=...`
- COG 转换: `POST /cog/local/convert` (Form 参数)
- 进度查询: `GET /cog/progress/{task_id}`
