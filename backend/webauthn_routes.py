"""
webauthn_routes.py - logare rapida cu Touch ID (Mac) / Windows Hello,
prin API-ul WebAuthn nativ al browserului. Parola ramane mereu
functionala ca fallback - asta e strict opt-in, aditiv.

rp_id = "127.0.0.1" fiindca aplicatia ruleaza local pe un port care se
schimba la fiecare pornire (find_free_port in app.py) - rp_id NU
include portul, deci o credentiala inregistrata ramane valida chiar
daca portul difera intre rulari. expected_origin, in schimb, TREBUIE sa
includa portul curent - de aceea e calculat dinamic din request.host_url,
nu hardcodat.
"""

import base64
import json

from flask import Blueprint, request, jsonify, session

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from models import db, User, WebAuthnCredential
from auth import login_required, current_user

webauthn_bp = Blueprint("webauthn", __name__)

RP_ID = "127.0.0.1"
RP_NAME = "GDC Production Manager"


def _credential_descriptors(user):
    return [
        PublicKeyCredentialDescriptor(id=base64url_to_bytes(c.credential_id))
        for c in user.webauthn_credentials
    ]


@webauthn_bp.route("/api/auth/webauthn/register-options", methods=["POST"])
@login_required
def register_options():
    user = current_user()
    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=str(user.id).encode("utf-8"),
        user_name=user.username,
        user_display_name=user.display_name or user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=_credential_descriptors(user),
    )
    session["webauthn_reg_challenge"] = base64.b64encode(options.challenge).decode()
    return options_to_json(options), 200, {"Content-Type": "application/json"}


@webauthn_bp.route("/api/auth/webauthn/register", methods=["POST"])
@login_required
def register_verify():
    user = current_user()
    challenge_b64 = session.pop("webauthn_reg_challenge", None)
    if not challenge_b64:
        return jsonify({"error": "webauthn_no_challenge"}), 400

    try:
        verification = verify_registration_response(
            credential=request.get_data(as_text=True),
            expected_challenge=base64.b64decode(challenge_b64),
            expected_rp_id=RP_ID,
            expected_origin=request.host_url.rstrip("/"),
        )
    except Exception:
        return jsonify({"error": "webauthn_invalid"}), 400

    cred_id_b64url = base64.urlsafe_b64encode(verification.credential_id).decode().rstrip("=")
    if WebAuthnCredential.query.filter_by(credential_id=cred_id_b64url).first():
        return jsonify({"error": "webauthn_invalid"}), 400

    cred = WebAuthnCredential(
        user_id=user.id,
        credential_id=cred_id_b64url,
        public_key=base64.b64encode(verification.credential_public_key).decode(),
        sign_count=verification.sign_count,
        label=(request.headers.get("User-Agent") or "")[:120],
    )
    db.session.add(cred)
    db.session.commit()
    return jsonify({"ok": True})


@webauthn_bp.route("/api/auth/webauthn/has-credential", methods=["GET"])
def has_credential():
    """Folosit de login.html ca sa decida daca arata butonul de Touch ID
    pentru ultimul username memorat local (fara sa scurgă daca username-ul
    exista - raspunde false pentru orice username necunoscut, la fel ca
    orice alt cont fara credentiala)."""
    username = (request.args.get("username") or "").strip()
    user = User.query.filter_by(username=username).first()
    has_cred = bool(user and user.webauthn_credentials)
    return jsonify({"has_credential": has_cred})


@webauthn_bp.route("/api/auth/webauthn/login-options", methods=["POST"])
def login_options():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    user = User.query.filter_by(username=username).first()
    allow = _credential_descriptors(user) if user else []
    if not allow:
        return jsonify({"error": "webauthn_no_credential"}), 404

    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=allow,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    session["webauthn_auth_challenge"] = base64.b64encode(options.challenge).decode()
    session["webauthn_auth_username"] = username
    return options_to_json(options), 200, {"Content-Type": "application/json"}


@webauthn_bp.route("/api/auth/webauthn/login", methods=["POST"])
def login_verify():
    challenge_b64 = session.pop("webauthn_auth_challenge", None)
    username = session.pop("webauthn_auth_username", None)
    if not challenge_b64 or not username:
        return jsonify({"error": "webauthn_no_challenge"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "invalid_credentials"}), 401

    body = request.get_data(as_text=True)
    try:
        raw = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"error": "webauthn_invalid"}), 400

    stored = WebAuthnCredential.query.filter_by(credential_id=raw.get("id"), user_id=user.id).first()
    if not stored:
        return jsonify({"error": "webauthn_no_credential"}), 404

    try:
        verification = verify_authentication_response(
            credential=body,
            expected_challenge=base64.b64decode(challenge_b64),
            expected_rp_id=RP_ID,
            expected_origin=request.host_url.rstrip("/"),
            credential_public_key=base64.b64decode(stored.public_key),
            credential_current_sign_count=stored.sign_count,
        )
    except Exception:
        return jsonify({"error": "webauthn_invalid"}), 400

    stored.sign_count = verification.new_sign_count
    db.session.commit()

    session["user_id"] = user.id
    return jsonify({"user": user.to_dict()})
