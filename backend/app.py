"""
GDC Production Manager
-----------------------
Local, standalone desktop app for managing video production projects.
Runs a small local web server and opens the UI in the system browser.
No data ever leaves the machine.

Author: Cristi Gordas (GDC)
"""

import os
import sys
import socket
import threading
import webbrowser

from flask import Flask, send_from_directory, jsonify, request

from config import Config, APP_VERSION, is_frozen
from models import db
from auth import auth_bp
from routes import api_bp
from sync import sync_bp
from license_routes import license_bp
from update_routes import update_bp
from webauthn_routes import webauthn_bp
import license_manager


def resource_path(*parts) -> str:
    """Resolve a path that works both in dev and inside a PyInstaller bundle."""
    if is_frozen():
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


FRONTEND_DIR = resource_path("frontend")


def find_free_port(preferred: int = 5175) -> int:
    for port in range(preferred, preferred + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return 0  # let the OS pick


def _migrate_schema():
    """db.create_all() doar creeaza tabele LIPSA - nu adauga coloane noi
    la un tabel deja existent. Cine a instalat deja v1.0.0 are un
    users.db fara coloana recovery_code_hash - o adaugam manual daca
    lipseste, ca sa nu crape la primul SELECT/INSERT dupa update."""
    from sqlalchemy import text
    existing_cols = {row[1] for row in db.session.execute(text("PRAGMA table_info(users)"))}
    if "recovery_code_hash" not in existing_cols:
        db.session.execute(text("ALTER TABLE users ADD COLUMN recovery_code_hash VARCHAR(255)"))
        db.session.commit()

    # v1.3.0: Client gained company_id/role (linking a contact person to a
    # full Company record) - the `companies` table itself is brand new, so
    # db.create_all() above already made it; only ALTER is needed on the
    # pre-existing `clients` table.
    existing_client_cols = {row[1] for row in db.session.execute(text("PRAGMA table_info(clients)"))}
    if "company_id" not in existing_client_cols:
        db.session.execute(text("ALTER TABLE clients ADD COLUMN company_id INTEGER"))
        db.session.commit()
    if "role" not in existing_client_cols:
        db.session.execute(text("ALTER TABLE clients ADD COLUMN role VARCHAR(100)"))
        db.session.commit()

    # v1.4.0: Project gained imported_clip_count/imported_structure, filled
    # in by importing a DataMover export.
    existing_project_cols = {row[1] for row in db.session.execute(text("PRAGMA table_info(projects)"))}
    if "imported_clip_count" not in existing_project_cols:
        db.session.execute(text("ALTER TABLE projects ADD COLUMN imported_clip_count INTEGER"))
        db.session.commit()
    if "imported_structure" not in existing_project_cols:
        db.session.execute(text("ALTER TABLE projects ADD COLUMN imported_structure JSON"))
        db.session.commit()

    # v1.4.0: User gained calendar_token (stable ICS "subscribe by URL" feed).
    if "calendar_token" not in existing_cols:
        db.session.execute(text("ALTER TABLE users ADD COLUMN calendar_token VARCHAR(64)"))
        db.session.commit()


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()
        _migrate_schema()

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(license_bp)
    app.register_blueprint(update_bp)
    app.register_blueprint(webauthn_bp)

    # Blocheaza orice apel de API cat timp trialul a expirat si nu exista
    # o licenta valida activata - verificat la FIECARE request, nu doar
    # la pornirea procesului (serverul ramane pornit pe termen lung, spre
    # deosebire de o aplicatie Tkinter care blocheaza o singura data la boot).
    _LICENSE_EXEMPT_PREFIXES = ("/api/license/", "/api/version")

    @app.before_request
    def _enforce_license():
        if not request.path.startswith("/api/"):
            return None
        if request.path.startswith(_LICENSE_EXEMPT_PREFIXES):
            return None
        if not license_manager.is_unlocked():
            return jsonify({"error": "trial_expired"}), 403
        return None

    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/<path:filename>")
    def frontend_files(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    @app.route("/api/version")
    def version():
        return jsonify({"version": APP_VERSION})

    @app.route("/api/quit", methods=["POST"])
    def quit_app():
        """Lets the UI cleanly stop the local server before the window closes."""
        threading.Timer(0.3, lambda: os._exit(0)).start()
        return jsonify({"ok": True})

    return app


def main():
    app = create_app()
    port = find_free_port()
    url = f"http://127.0.0.1:{port}/"

    threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    print(f"GDC Production Manager v{APP_VERSION}")
    print(f"Running locally at {url}")
    print("Close this window / press Ctrl+C to stop the app.")

    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)


if __name__ == "__main__":
    main()
