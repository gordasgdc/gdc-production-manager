"""
self_updater.py - descarca si instaleaza automat un update, fara sa mai
treaca prin browser/pagina de GitHub (vezi CLAUDE.md Partea 1, Regula 20).
Port conceptual al SelfUpdater.swift/.cs (Swift/C#) pentru stack-ul
Flask/PyInstaller al acestei aplicatii.

Diferenta fata de restul ecosistemului: aici NU exista o fereastra
nativa proprie (UI-ul e servit intr-un tab de browser local, catre
127.0.0.1) - de-asta acest modul scrie progresul intr-un fisier de status
citit prin polling de `frontend/settings.html`/`script.js`
(`GET /api/update/install-status`), in loc sa deseneze o fereastra.

Flux:
  Mac: descarca .pkg-ul, il instaleaza printr-un script bash elevat cu
       `osascript ... with administrator privileges` (prompt NATIV de
       parola admin, la fel ca SelfUpdater.swift), relanseaza aplicatia
       cu `open -a`, apoi termina procesul Flask curent.
  Windows: descarca .exe-ul, il lanseaza cu `subprocess.Popen` (proces
       detasat), apoi termina procesul Flask curent - installer.iss
       (`[Run] ... Flags: nowait postinstall skipifsilent`) relanseaza
       aplicatia dupa instalare, la fel ca GDCVaultWin/GDCPluginManagerWin.

WARNING: pasul de instalare efectiv (promptul de parola admin pe Mac,
wizardul Inno pe Windows) NU poate fi verificat automat de Claude.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import urllib.error

_STATUS_PATH = os.path.join(tempfile.gettempdir(), "gdc_production_manager_update_status.json")
_status_lock = threading.Lock()


def _write_status(stage, error=None):
    with _status_lock:
        with open(_STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump({"stage": stage, "error": error, "ts": time.time()}, f)


def read_status():
    try:
        with open(_STATUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"stage": "idle", "error": None}


def start_update_async(download_url, version):
    """Porneste descarcarea+instalarea intr-un thread de fundal. Nu
    blocheaza cererea HTTP care a declansat update-ul - frontend-ul
    face polling pe /api/update/install-status."""
    thread = threading.Thread(target=_run, args=(download_url, version), daemon=True)
    thread.start()


def _run(download_url, version):
    try:
        if not download_url:
            raise RuntimeError("Lipsește link-ul de descărcare pentru această platformă.")

        _write_status("downloading")
        tmp_dir = tempfile.mkdtemp(prefix="gdc-production-manager-update-")
        is_mac = platform.system() == "Darwin"
        installer_path = os.path.join(tmp_dir, f"GDCProductionManager-{version}" + (".pkg" if is_mac else ".exe"))
        _download(download_url, installer_path)

        _write_status("installing")
        if is_mac:
            _install_mac(installer_path, tmp_dir)
        else:
            _install_windows(installer_path)

        _write_status("done")
        # Lasa frontend-ul sa apuce sa citeasca "done" inainte sa moara
        # serverul Flask (polling la ~1s) - fara asta, cererea de status
        # ar putea esua cu conexiune refuzata chiar inainte de a afisa
        # mesajul de succes.
        time.sleep(2)
        os._exit(0)
    except Exception as e:
        _write_status("failed", error=str(e))


def _download(url, destination):
    request = urllib.request.Request(url, headers={"User-Agent": "GDCProductionManager-Updater"})
    try:
        with urllib.request.urlopen(request, timeout=300) as response, open(destination, "wb") as out_file:
            while True:
                chunk = response.read(1024 * 256)
                if not chunk:
                    break
                out_file.write(chunk)
    except urllib.error.URLError as e:
        raise RuntimeError(f"Descărcarea a eșuat: {e.reason}") from e


def _install_mac(pkg_path, tmp_dir):
    log_path = os.path.join(tmp_dir, "update.log")
    script_path = os.path.join(tmp_dir, "update.sh")
    script_content = f"""#!/bin/bash
exec > "{log_path}" 2>&1
sleep 2
echo "Instalez actualizarea..."
installer -pkg "{pkg_path}" -target /
status=$?
if [ $status -ne 0 ]; then
    echo "Instalarea a esuat (cod $status)."
    exit $status
fi
echo "Pornesc aplicatia actualizata..."
open -a "GDC Production Manager"
rm -rf "{tmp_dir}"
"""
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)

    escaped_path = script_path.replace('"', '\\"')
    apple_script = f'do shell script "{escaped_path}" with administrator privileges'
    subprocess.Popen(["/usr/bin/osascript", "-e", apple_script])


def _install_windows(exe_path):
    # DETACHED_PROCESS: installer-ul supravietuieste dupa ce procesul
    # nostru se inchide - fara asta, pe Windows copilul ar putea fi
    # omorat odata cu parintele in unele configuratii.
    creationflags = subprocess.DETACHED_PROCESS if sys.platform == "win32" else 0
    subprocess.Popen([exe_path], creationflags=creationflags, close_fds=True)
