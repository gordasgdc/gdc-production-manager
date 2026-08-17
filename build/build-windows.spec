# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — Windows build (.exe)
# Run from the repository root:  pyinstaller build/build-windows.spec

import os

block_cipher = None
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

_icon_path = os.path.join(ROOT, "icon", "icon.ico")
ICON = _icon_path if os.path.isfile(_icon_path) else None

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
        "cryptography",
        "cryptography.hazmat.primitives.asymmetric.ed25519",
        "cryptography.hazmat.bindings._rust",
        "webauthn",
        "cbor2",
        "pyasn1",
        "pyasn1_modules",
        "OpenSSL",
        "certifi",
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
    icon=ICON,
)
