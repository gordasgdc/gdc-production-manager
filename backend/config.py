"""
GDC Production Manager - Configuration
Determines where per-user data (SQLite DB, secret key) lives on disk.
Each user who installs the app gets their own local, private data folder.
"""

import os
import sys
import platform
import secrets


APP_NAME = "GDCProductionManager"
APP_VERSION = "1.0.0"
BUNDLE_ID = "com.gordasgdc.productionmanager"


def is_frozen() -> bool:
    """True when running from a PyInstaller-built executable."""
    return getattr(sys, "frozen", False)


def get_data_dir() -> str:
    """
    Returns the per-user, per-machine data directory.
    Mac:     ~/Library/Application Support/GDCProductionManager
    Windows: %APPDATA%\\GDCProductionManager
    Linux:   ~/.local/share/GDCProductionManager
    """
    system = platform.system()

    if system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif system == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get(
            "XDG_DATA_HOME", os.path.expanduser("~/.local/share")
        )

    data_dir = os.path.join(base, APP_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_or_create_secret_key(data_dir: str) -> str:
    """Persist a random Flask secret key locally so sessions survive restarts."""
    key_path = os.path.join(data_dir, ".secret_key")
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            key = f.read().strip()
            if key:
                return key
    key = secrets.token_hex(32)
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(key)
    return key


DATA_DIR = get_data_dir()
DATABASE_PATH = os.path.join(DATA_DIR, "gdc_production_manager.db")


class Config:
    SECRET_KEY = get_or_create_secret_key(DATA_DIR)
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    JSON_SORT_KEYS = False
