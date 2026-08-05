# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Windows build (.exe)
# Run from the repository root:  pyinstaller build/build-windows.spec

import os

block_cipher = None
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

a = Analysis(
    [os.path.join(ROOT, "backend", "app.py")],
    pathex=[os.path.join(ROOT, "backend")],
    binaries=[],
    datas=[
        (os.path.join(ROOT, "frontend"), "frontend"),
    ],
    hiddenimports=[
        "flask_sqlalchemy",
        "sqlalchemy.sql.default_comparator",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="GDCProductionManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=os.path.join(ROOT, "icon", "icon.ico"),
)
