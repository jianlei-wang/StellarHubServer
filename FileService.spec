import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 确保当前目录在 path 中，以便 collect_submodules 等能正常工作
sys.path.insert(0, os.path.abspath('src'))

hiddenimports = [
    'numpy',
    'core',
    'api',
    'service',
    'utils',
    'core.config',
    'core.exception',
    'core.response',
    'api.file',
    'api.cog_api',
    'service.cog_service',
    'service.file_service',
    'utils.cog_utils',
    'utils.path_util',
    'utils.progress_util',
] + collect_submodules('rasterio') + collect_submodules('rio_cogeo')

datas = [
    ('web', 'web'),
    ('src/proj', 'proj'),
] + collect_data_files('morecantile', include_py_files=False, subdir='data')

a = Analysis(
    ['src/main.py'],
    pathex=['src', '.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='StellarHubService',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)