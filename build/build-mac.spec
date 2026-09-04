# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — macOS build (.app)
# Run from the repository root:  pyinstaller build/build-mac.spec

import os

block_cipher = None
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(SPEC)), ".."))

# Fall back to PyInstaller's default icon if icon.icns wasn't committed,
# so a missing icon can never hard-fail the whole build.
_icon_path = os.path.join(ROOT, "icon", "icon.icns")
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
    [],
    exclude_binaries=True,
    name="GDCProductionManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="GDCProductionManager",
)

app = BUNDLE(
    coll,
    name="GDCProductionManager.app",
    icon=ICON,
    bundle_identifier="com.gordasgdc.productionmanager",
    info_plist={
        "CFBundleName": "GDC Production Manager",
        "CFBundleDisplayName": "GDC Production Manager",
        "CFBundleShortVersionString": "2.0.1",  # tine sincronizat manual cu backend/config.py APP_VERSION
        "CFBundleVersion": "2.0.1",
        "NSHighResolutionCapable": True,
        "LSMinimumSystemVersion": "11.0",
        "NSHumanReadableCopyright": "© Cristi Gordas (GDC)",
    },
)
