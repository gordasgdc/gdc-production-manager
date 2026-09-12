"""
license_manager.py — trial de 25 zile + licență lifetime pentru GDC
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
import revocation_check
from config import DATA_DIR

TRIAL_DAYS = 25

# ---------------------------------------------------------------------------
# MOD "PREVIZUALIZARE GRATUITA" (2026-09-12, decizie explicita de produs)
#
# Cat timp aceasta constanta e True, aplicatia e COMPLET gratuita si NIMIC nu
# se blocheaza: fara proba care expira, fara ecran de activare, fara pret
# afisat nicaieri. Motivul e de pozitionare, nu tehnic: aplicatia e inca in
# dezvoltare activa, iar un pret afisat pe ceva neconcretizat reduce atractia
# si, mai important, descurajeaza exact feedback-ul care ne trebuie acum de la
# cei care o descarca.
#
# Trecerea la False (= licentiere reala, proba de TRIAL_DAYS zile + pret) se
# face DOAR la o declaratie explicita a lui Cristi ca versiunea e oficiala.
# Nu se reactiveaza automat la o anumita versiune, nu expira dupa o data.
# Intreaga infrastructura de licentiere de mai jos ramane INTACTA si testata
# — se schimba un singur flag, nu se rescrie nimic.
# ---------------------------------------------------------------------------
PREVIEW_FREE_MODE = True

# Kill-switch diferentiat (decizie 2026-08-24): cate secunde tinem o
# licenta anterior-valida "activa" cand hardware-ul nu poate fi citit acum
# (WMI restrictionat, VM, ioreg indisponibil) — suficient cat un client
# cinstit sa nu piarda accesul dintr-o eroare temporara, dar nu nelimitat.
GRACE_PERIOD_SECONDS = 5 * 86400  # 5 zile

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
    """Reverifica semnatura la fiecare apel (niciodata un flag cache-uit —
    vezi GDC-SEC-05). Kill-switch diferentiat (decizie 2026-08-24) dupa
    `result.reason`:
      - valid -> licentiat, salveaza timestamp-ul ca "ultima stare buna".
      - bad_signature -> tamper evident: sterge serialul stocat (hard lock).
      - hwid_unavailable -> grace period: ramane licentiat daca ultima stare
        buna e mai recenta de GRACE_PERIOD_SECONDS, altfel demo (fara sa
        stearga serialul — poate reveni hardware-ul).
      - wrong_machine / wrong_product / expired -> demo, serialul ramane
        salvat (nu e tamper, poate fi hardware schimbat legitim)."""
    state = _load_state()
    serial = state.get("serial")
    if not serial:
        return False

    result = license_validator.check(serial)

    if result.valid:
        # v2.0.0 (Regula 12): revocare online, fail-open - o licenta deja
        # activata NU se blocheaza pentru ca userul e offline; se aplica
        # abia dupa un raspuns explicit "true" din Supabase (vezi
        # revocation_check.py). Verificarea in sine ruleaza in fundal
        # (app.py::main -> revocation_check.start_periodic_refresh) - aici
        # doar citim starea deja cunoscuta, sincron, fara retea.
        if revocation_check.is_revoked():
            return False
        state["last_valid_check_ts"] = int(time.time())
        _save_state(state)
        return True

    if result.reason == "bad_signature":
        state["serial"] = None
        _save_state(state)
        return False

    if result.reason == "hwid_unavailable":
        last_good = state.get("last_valid_check_ts", 0)
        if last_good and (time.time() - last_good) < GRACE_PERIOD_SECONDS:
            return True  # grace activ — nu atingem serialul stocat
        return False  # grace expirat -> mod demo, serialul ramane pe disc

    # wrong_machine / wrong_product / expired -> mod demo, fara stergere
    return False


def is_unlocked() -> bool:
    # In modul de previzualizare gratuita nimic nu se blocheaza — vezi
    # PREVIEW_FREE_MODE de mai sus.
    if PREVIEW_FREE_MODE:
        return True
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
    state = _load_state()
    demo_reason = None
    if not licensed and state.get("serial"):
        # Serialul exista dar nu (mai) valideaza — afla motivul, pentru mesaj
        # explicativ in UI (vezi kill-switch diferentiat din is_licensed()).
        demo_reason = license_validator.check(state["serial"]).reason
    return {
        # `preview_free` spune UI-ului sa nu arate nici proba, nici pretul,
        # nici formularul de activare — vezi PREVIEW_FREE_MODE.
        "preview_free": PREVIEW_FREE_MODE,
        "unlocked": is_unlocked(),
        "licensed": licensed,
        "trial_days_remaining": trial_days_remaining(),
        "machine_id": machine_id.get_machine_id_display(),
        "demo_reason": demo_reason,
    }
