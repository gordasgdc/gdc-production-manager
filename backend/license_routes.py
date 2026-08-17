"""
GDC Production Manager - License / trial API.

Ruta e publica (fara login_required) fiindca trebuie sa functioneze
INAINTE ca cineva sa aiba vreun cont local creat - e vorba de licenta
instalarii, nu a unui user anume.
"""

from flask import Blueprint, request, jsonify

import license_manager

license_bp = Blueprint("license", __name__)


@license_bp.route("/api/license/status", methods=["GET"])
def get_status():
    return jsonify(license_manager.status())


@license_bp.route("/api/license/activate", methods=["POST"])
def activate():
    data = request.get_json(silent=True) or {}
    serial = (data.get("serial") or "").strip()
    if not serial:
        return jsonify({"error": "missing_serial"}), 400

    result = license_manager.activate(serial)
    if not result.valid:
        error_key = "expired" if result.expired else "invalid"
        return jsonify({"error": error_key, "message": result.error}), 400

    return jsonify(license_manager.status())
