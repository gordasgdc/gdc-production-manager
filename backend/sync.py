"""
GDC Production Manager - optional self-hosted sync.

This is intentionally simple: two independent installs of this same app can
exchange one full JSON snapshot (the same shape used by Export/Import) over
plain HTTP(S), authenticated with a shared secret the person sets on both
sides ("sync token"). There is no third-party server involved — the person
supplies the address of another machine running this same app.

Nothing is sent anywhere until the person explicitly presses "Push" or
"Pull" in Settings.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime

from flask import Blueprint, request, jsonify

from models import db, User
from auth import login_required, current_user
from routes import build_export_dict, apply_import_payload

sync_bp = Blueprint("sync", __name__)

REQUEST_TIMEOUT_SECONDS = 15


def _user_by_token(token: str):
    if not token:
        return None
    return User.query.filter_by(sync_token=token).first()


def _bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    return ""


# --------------------------------------------------- incoming (server side)

@sync_bp.route("/api/sync/snapshot", methods=["GET"])
def sync_snapshot():
    """Another instance calls this to PULL our data. Token-authenticated,
    independent of any browser session."""
    user = _user_by_token(_bearer_token())
    if not user:
        return jsonify({"error": "invalid_token"}), 401
    return jsonify(build_export_dict(user))


@sync_bp.route("/api/sync/receive", methods=["POST"])
def sync_receive():
    """Another instance calls this to PUSH data into our account matching
    the shared token."""
    user = _user_by_token(_bearer_token())
    if not user:
        return jsonify({"error": "invalid_token"}), 401

    payload = request.get_json(silent=True) or {}
    if "clients" not in payload and "projects" not in payload:
        return jsonify({"error": "invalid_payload"}), 400

    result = apply_import_payload(user, payload)
    user.last_synced_at = datetime.utcnow()
    db.session.commit()
    return jsonify(result)


# --------------------------------------------------- outgoing (client side)

def _remote_request(url: str, token: str, method: str = "GET", body: dict = None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            detail = json.loads(e.read().decode("utf-8"))
        except Exception:
            detail = {"error": f"http_{e.code}"}
        return False, detail
    except urllib.error.URLError as e:
        return False, {"error": "unreachable", "detail": str(e.reason)}
    except Exception as e:
        return False, {"error": "unexpected", "detail": str(e)}


@sync_bp.route("/api/sync/push", methods=["POST"])
@login_required
def sync_push():
    user = current_user()
    if not user.sync_remote_url or not user.sync_token:
        return jsonify({"error": "sync_not_configured"}), 400

    url = user.sync_remote_url.rstrip("/") + "/api/sync/receive"
    snapshot = build_export_dict(user)
    ok, result = _remote_request(url, user.sync_token, method="POST", body=snapshot)
    if not ok:
        return jsonify({"error": "push_failed", "detail": result}), 502

    user.last_synced_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True, "result": result})


@sync_bp.route("/api/sync/pull", methods=["POST"])
@login_required
def sync_pull():
    user = current_user()
    if not user.sync_remote_url or not user.sync_token:
        return jsonify({"error": "sync_not_configured"}), 400

    url = user.sync_remote_url.rstrip("/") + "/api/sync/snapshot"
    ok, snapshot = _remote_request(url, user.sync_token, method="GET")
    if not ok:
        return jsonify({"error": "pull_failed", "detail": snapshot}), 502

    result = apply_import_payload(user, snapshot)
    user.last_synced_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True, "result": result})
