"""
update_routes.py - verificare de actualizari, ca la DataMover/CursorPro GDC.

Cererea catre docs/update.json se face din BACKEND (nu din JS-ul din
browser) ca sa evitam CORS si ca sa nu depindem de politica de retea a
browserului local.
"""

import json
import ssl
import urllib.request
from urllib.error import URLError

import certifi
from flask import Blueprint, jsonify

from config import APP_VERSION, APP_VERSION_URL

update_bp = Blueprint("update", __name__)

# urllib foloseste contextul SSL implicit al Python-ului, care - odata
# compilat cu PyInstaller - nu mai gaseste certificatele CA ale sistemului
# (eroare tipica: "certificate verify failed: unable to get local issuer
# certificate"). certifi vine cu propriul lant de certificate CA, bundle-uit
# explicit ca fisier de date (vezi hiddenimports/datas din build-*.spec).
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _version_tuple(v: str):
    try:
        return tuple(int(p) for p in v.strip().split("."))
    except (ValueError, AttributeError):
        return (0,)


@update_bp.route("/api/update/check", methods=["GET"])
def check_update():
    try:
        with urllib.request.urlopen(APP_VERSION_URL, timeout=10, context=_SSL_CONTEXT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, OSError):
        return jsonify({"error": "check_failed"}), 502

    latest_version = data.get("version", APP_VERSION)
    update_available = _version_tuple(latest_version) > _version_tuple(APP_VERSION)

    return jsonify({
        "current_version": APP_VERSION,
        "latest_version": latest_version,
        "update_available": update_available,
        "changes": data.get("changes", ""),
        "download_url": data.get("download_url", {}),
    })
