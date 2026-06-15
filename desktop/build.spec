# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for BlockMind Desktop
# This is a template - actual packaging uses `dotnet publish` for .NET apps

blockmind = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../src/', 'src/'),
        ('../skills/', 'skills/'),
        ('../config.example.yaml', 'config/'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'openai',
        'anthropic',
        'httpx',
        'pydantic',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(blockmind.pure)

exe = EXE(
    pyz,
    blockmind.scripts,
    [],
    exclude_binaries=True,
    name='BlockMind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='../assets/icon.ico',
)

coll = COLLECT(
    exe,
    blockmind.binaries,
    blockmind.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BlockMind',
)
