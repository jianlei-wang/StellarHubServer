# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('web', 'web'),  # 只需要打包网页
    ],
    # hiddenimports = 完全删除！
    hiddenimports=['rasterio._shim', 'rasterio._io'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    name='FileService',
    debug=False,
    strip=False,
    upx=True,
    console=True,
)