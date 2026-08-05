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

from flask import Flask, send_from_directory, jsonify

from config import Config, APP_VERSION, is_frozen
from models import db
from auth import auth_bp
from routes import api_bp
from sync import sync_bp


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


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(sync_bp)

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
