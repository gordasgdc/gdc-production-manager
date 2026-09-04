"""
revocation_check.py — verificare ONLINE, opțională, peste licențierea
existentă (Ed25519, 100% offline) — CLAUDE.md, Partea 1, Regula 12. Port
1:1 al `RevocationCheck.swift` (gdc-plugin-manager-catalog-vendor) pentru
stack-ul Flask al acestei aplicații. Adaugă un "kill-switch" pe care
Cristi îl poate declanșa manual din Furnizor, FĂRĂ să schimbe deloc
formatul criptografic al codurilor existente.

FAIL-OPEN, niciodată fail-closed: absența unui răspuns POZITIV de
revocare (eroare de rețea, offline, request eșuat) înseamnă NErevocat. O
licență deja activată local nu se blochează NICIODATĂ doar pentru că
utilizatorul e offline — revocarea se aplică abia la următoarea
verificare online reușită care confirmă explicit `true`. Odată marcat
revocat, rămâne așa pentru restul acestui proces (nu se "de-revocă" pe un
răspuns "false" ulterior — la fel ca RevocationCheck.swift, care doar
adaugă la set, niciodată nu elimină).

Folosește apelul RPC `is_license_revoked(machine_id, product_id)` din
Supabase (vezi gdc-plugin-manager-catalog-vendor/supabase/migrations/
2026-08-26_license_revocations.sql) — NICIODATĂ un SELECT direct pe
tabel: RLS blochează complet accesul direct cu cheia anon.
"""

import json
import ssl
import threading
import time
import urllib.error
import urllib.request

import certifi

_SUPABASE_URL = "https://jvxrclpyngdcqnbwvtfn.supabase.co"
# Cheia "anon public" - sigur de comis, vezi doc-ul SupabaseConfig.swift
# din gdc-plugin-manager-catalog-vendor: fiecare tabel/funcție pe care-l
# poate atinge are RLS activ, fără nicio policy de citire pentru anon.
_SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2eHJjbHB5bmdkY3FuYnd2dGZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODcwODMxMDksImV4cCI6MjEwMjY1OTEwOX0."
    "uCLgrVPLhovwdBc82KermRbtWykquWoJmg9WmGk2L-s"
)
_PRODUCT_ID = "gdc-production-manager"
_REFRESH_INTERVAL_SECONDS = 6 * 3600  # 6 ore - la fel de des ca update checker-ul

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
_lock = threading.Lock()
_is_revoked = False


def is_revoked() -> bool:
    with _lock:
        return _is_revoked


def _check_once(machine_id: str) -> None:
    global _is_revoked
    url = _SUPABASE_URL + "/rest/v1/rpc/is_license_revoked"
    body = json.dumps({"p_machine_id": machine_id, "p_product_id": _PRODUCT_ID}).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Content-Type": "application/json",
            "apikey": _SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {_SUPABASE_ANON_KEY}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8, context=_SSL_CONTEXT) as resp:
            if resp.status != 200:
                return  # fail-open
            # PostgREST pentru o functie ce intoarce `boolean` da inapoi
            # literal `true`/`false` ca body JSON.
            text = resp.read().decode("utf-8").strip()
            if text == "true":
                with _lock:
                    _is_revoked = True
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return  # orice eroare de retea/server -> fail-open, NU revocat


def refresh_once(machine_id: str) -> None:
    """Verificare unică, într-un thread de fundal - niciodată blocantă."""
    threading.Thread(target=_check_once, args=(machine_id,), daemon=True).start()


def start_periodic_refresh(get_machine_id) -> None:
    """Pornește o buclă de fundal care reverifică la fiecare
    `_REFRESH_INTERVAL_SECONDS` - apelată o singură dată, la pornirea
    aplicației. `get_machine_id` e un callable (nu un string), ca
    machine_id-ul să fie citit din nou la fiecare iterație, nu prins o
    singură dată la boot."""
    def _loop():
        while True:
            _check_once(get_machine_id())
            time.sleep(_REFRESH_INTERVAL_SECONDS)

    threading.Thread(target=_loop, daemon=True).start()
