"""
GDC Production Manager - Local authentication.

This is a single-machine, local-first app: "accounts" simply let more than
one person share one installed copy while keeping their data separate.
Nothing here is transmitted over a network.
"""

from functools import wraps
from flask import Blueprint, request, jsonify, session

from models import db, User

auth_bp = Blueprint("auth", __name__)


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "not_authenticated"}), 401
        return view_func(*args, **kwargs)

    return wrapped


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@auth_bp.route("/api/auth/status", methods=["GET"])
def status():
    user = current_user()
    return jsonify({"authenticated": user is not None, "user": user.to_dict() if user else None})


@auth_bp.route("/api/auth/has-account", methods=["GET"])
def has_account():
    """Lets the frontend decide whether to show 'Register' or 'Login' first."""
    exists = db.session.query(User.id).first() is not None
    return jsonify({"has_account": exists})


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    display_name = (data.get("display_name") or "").strip() or username
    language = data.get("language") or "ro"

    if len(username) < 3:
        return jsonify({"error": "username_too_short"}), 400
    if len(password) < 6:
        return jsonify({"error": "password_too_short"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "username_taken"}), 409

    user = User(username=username, display_name=display_name, language=language)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()}), 201


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.route("/api/auth/language", methods=["POST"])
@login_required
def set_language():
    data = request.get_json(silent=True) or {}
    language = data.get("language")
    if language not in ("ro", "en", "es"):
        return jsonify({"error": "invalid_language"}), 400
    user = current_user()
    user.language = language
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/api/auth/theme", methods=["POST"])
@login_required
def set_theme():
    data = request.get_json(silent=True) or {}
    theme = data.get("theme")
    if theme not in ("dark", "light"):
        return jsonify({"error": "invalid_theme"}), 400
    user = current_user()
    user.theme = theme
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/api/auth/currency", methods=["POST"])
@login_required
def set_currency():
    data = request.get_json(silent=True) or {}
    currency = data.get("currency")
    if currency not in ("EUR", "RON"):
        return jsonify({"error": "invalid_currency"}), 400
    user = current_user()
    user.currency = currency
    db.session.commit()
    return jsonify({"user": user.to_dict()})


@auth_bp.route("/api/auth/sync-settings", methods=["POST"])
@login_required
def set_sync_settings():
    """Stores the address of another GDC Production Manager instance this
    one can push/pull a full data snapshot to/from. Nothing is sent anywhere
    until the person explicitly triggers a sync."""
    data = request.get_json(silent=True) or {}
    user = current_user()
    user.sync_remote_url = (data.get("sync_remote_url") or "").strip() or None
    user.sync_token = (data.get("sync_token") or "").strip() or None
    db.session.commit()
    return jsonify({"user": user.to_dict()})
