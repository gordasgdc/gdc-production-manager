"""
machine_id.py — ID de masina, in Python, folosind ACEEASI metoda ca
partea C++ din gdc-resolve-encoder (hash SHA-512 trunchiat la 6 octeti,
Base32) — rezultatul e identic pentru aceeasi masina, indiferent de care
produs GDC il cere.

GDC-SEC-02 (audit securitate 2026-08-24): pe Windows NU mai folosim
MachineGuid din Registry — se rescrie cu un simplu "reg add" din orice
cont admin. Formula STRICTA pe Windows (obligatorie identic in Python,
C#, C++ — vezi docs/MACHINE_ID.md sau echivalentul din gdc-resolve-encoder):

    raw = trim(Win32_ComputerSystemProduct.UUID) + "|" + trim(Win32_DiskDrive[0].SerialNumber)
    hash = SHA-512(raw), primii 6 octeti, Base32

Orice implementare noua TREBUIE sa respecte exact acest format (inclusiv
trim-ul si separatorul "|"), altfel machine_id-ul afisat difera intre
componente pentru aceeasi masina, iar licentele Windows deja emise devin
invalide. Pe Mac ramane doar IOPlatformUUID (nu e afectat de GDC-SEC-02 —
nu exista un echivalent trivial de "reg add" pentru el).
"""

import hashlib
import subprocess
import sys


def _raw_machine_id():
    """Intoarce (raw: str, available: bool). `available=False` inseamna ca
    hardware-ul n-a putut fi citit acum (WMI/ioreg indisponibil, timeout,
    etc.) — `raw` primeste placeholder-ul stabil de mai jos, DAR apelantul
    (license_manager.py, prin validate_serial_compact) NU trebuie sa trateze
    asta ca "masina diferita": vezi kill-switch-ul diferentiat, decizie
    2026-08-24 (hwid_unavailable -> grace period, nu blocare)."""
    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.splitlines():
                if "IOPlatformUUID" in line:
                    return line.split("=")[-1].strip().strip('"'), True
        except Exception:
            pass
        return "mac-machine-id-unavailable", False

    elif sys.platform.startswith("win"):
        try:
            # Vezi nota GDC-SEC-02 din antetul fisierului — formula STRICTA,
            # identica byte-cu-byte cu C++/C#.
            ps_cmd = (
                "$b = (Get-CimInstance Win32_ComputerSystemProduct).UUID; "
                "$d = (Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber); "
                "Write-Output ($b.Trim() + '|' + $d.Trim())"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=5,
            )
            combined = result.stdout.strip()
            if combined and combined != "|":
                return combined, True
        except Exception:
            pass
        return "windows-machine-id-unavailable", False

    else:
        try:
            with open("/etc/machine-id") as f:
                return f.read().strip(), True
        except Exception:
            return "linux-machine-id-unavailable", False


def get_machine_id_display():
    """Intoarce ID-ul de masina, ca string Base32 scurt, lizibil —
    identic ca format (si, pe aceeasi masina, identic ca valoare) cu
    get_machine_id_display() din C++ (gdc-resolve-encoder). Foloseste
    placeholder-ul stabil daca hardware-ul nu poate fi citit — pentru
    afisare, nu conteaza (vezi is_available() pentru logica de validare)."""
    import base64
    raw, _available = _raw_machine_id()
    digest = hashlib.sha512(raw.encode("utf-8")).digest()[:6]
    return base64.b32encode(digest).decode("ascii").rstrip("=")


def is_available() -> bool:
    """True daca hardware-ul a putut fi citit efectiv acum — vezi nota
    despre kill-switch diferentiat din _raw_machine_id()."""
    _raw, available = _raw_machine_id()
    return available
