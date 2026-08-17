"""
license_manager.py — trial de 7 zile + licență lifetime pentru GDC
Production Manager.

Spre deosebire de DataMover (aplicație Tkinter care blochează O DATĂ, la
pornirea procesului), aici serverul Flask rămâne pornit pe termen lung —
starea trialului/licenței trebuie verificată la FIECARE cerere de API
(vezi before_request-ul din app.py), nu doar la boot.
"""

import json
import os
import time

import license_validator
import machine_id
from config import DATA_DIR

TRIAL_DAYS = 7

_STATE_PATH = os.path.join(DATA_DIR, "license_state.json")


def _load_state() -> dict:
    if not os.path.isfile(_STATE_PATH):
        state = {"trial_start": int(time.time()), "serial": None}
        _save_state(state)
        return state
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            state = json.load(f)
    except (json.JSONDecodeError, OSError):
        state = {}
    if "trial_start" not in state:
        state["trial_start"] = int(time.time())
        _save_state(state)
    state.setdefault("serial", None)
    return state


def _save_state(state: dict) -> None:
    tmp_path = _STATE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f)
    os.replace(tmp_path, _STATE_PATH)


def trial_days_remaining() -> int:
    state = _load_state()
    elapsed_days = (time.time() - state["trial_start"]) / 86400
    remaining = TRIAL_DAYS - elapsed_days
    return max(0, int(remaining + 0.999))  # rotunjire in sus, ca la DataMover


def is_licensed() -> bool:
    state = _load_state()
    serial = state.get("serial")
    if not serial:
        return False
    result = license_validator.check(serial)
    return bool(result.valid)


def is_unlocked() -> bool:
    return is_licensed() or trial_days_remaining() > 0


def activate(serial: str):
    """Valideaza si, daca e ok, salveaza serialul. Intoarce ValidationResult."""
    result = license_validator.check(serial.strip())
    if result.valid:
        state = _load_state()
        state["serial"] = serial.strip()
        _save_state(state)
    return result


def status() -> dict:
    licensed = is_licensed()
    return {
        "unlocked": licensed or trial_days_remaining() > 0,
        "licensed": licensed,
        "trial_days_remaining": trial_days_remaining(),
        "machine_id": machine_id.get_machine_id_display(),
    }
