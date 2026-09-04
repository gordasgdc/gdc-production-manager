"""
analytics_client.py — port 1:1 al `AnalyticsClient.swift`
(gdc-plugin-manager-catalog-vendor): scrie fire-and-forget o înregistrare
în tabelul Supabase `devices`, folosit și pentru Regula 12 (profil vizibil
+ HWID) și ca sursă a verificării de revocare.

Tabelul acceptă DOAR INSERT de la cheia anon (RLS) - acest apel nu poate
niciodată citi, suprascrie sau șterge ceva; orice eroare e înghițită
tăcut, ca telemetria să nu poată bloca vreodată un login/înregistrare.

Notă specifică acestui repo: `gdc-production-manager` e 100% local (cont
username/parolă, fără email) - `email` se trimite gol, nu lipsă din
schemă, ca înregistrarea să rămână identică structural cu restul
ecosistemului.
"""

import json
import ssl
import threading
import urllib.error
import urllib.request

import certifi

from revocation_check import _SUPABASE_URL, _SUPABASE_ANON_KEY

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _post(table: str, body: dict) -> None:
    def _send():
        try:
            data = json.dumps(body).encode("utf-8")
            request = urllib.request.Request(
                _SUPABASE_URL + f"/rest/v1/{table}", data=data, method="POST",
                headers={
                    "Content-Type": "application/json",
                    "apikey": _SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {_SUPABASE_ANON_KEY}",
                    "Prefer": "return=minimal",
                },
            )
            urllib.request.urlopen(request, timeout=8, context=_SSL_CONTEXT).close()
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            pass  # deliberat ignorat - vezi doc-ul de mai sus

    threading.Thread(target=_send, daemon=True).start()


def register_device(machine_id: str, name: str) -> None:
    _post("devices", {"machine_id": machine_id, "name": (name or "").strip(), "email": ""})
