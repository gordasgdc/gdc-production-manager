"""
pricing_checker.py — preț dinamic, fără recompilare (CLAUDE.md, Partea 1,
Regula 27). Port 1:1 al `PricingChecker.swift` (DataMover) pentru stack-ul
Flask al acestei aplicații: citește `https://gordas.dev/pricing.json`
(publicat de Furnizor, gdc-plugin-manager-catalog-vendor) în loc de o
valoare hardcodată în cod.

Fail-open, ca RevocationCheck: fără conexiune, sau dacă produsul lipsește
din pricing.json, se folosește `FALLBACK_PRICE` - IDENTIC cu suma
documentată azi în UI (settings.html, mesajul WhatsApp) la data acestei
implementări - niciodată un ecran de activare gol/eronat.
"""

import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone

import certifi

_PRICING_URL = "https://gordas.dev/pricing.json"
_PRODUCT_ID = "gdc-production-manager"
FALLBACK_PRICE = 25.0
FALLBACK_CURRENCY = "EUR"

_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def _parse_iso(value: str) -> datetime:
    # pricing.json foloseste ISO8601 cu sufix "Z" - fromisoformat vrea
    # "+00:00" explicit pe unele versiuni de Python.
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def fetch_effective_price() -> dict:
    fallback = {"price": FALLBACK_PRICE, "currency": FALLBACK_CURRENCY, "promo_label": None,
                "show_countdown": False, "ends_at": None}
    try:
        with urllib.request.urlopen(_PRICING_URL, timeout=8, context=_SSL_CONTEXT) as resp:
            if resp.status != 200:
                return fallback
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return fallback

    product = (data.get("products") or {}).get(_PRODUCT_ID)
    if not product:
        return fallback

    now = datetime.now(timezone.utc)
    active_promo = None
    for promo in product.get("promoSchedule") or []:
        try:
            starts = _parse_iso(promo["startsAt"])
            ends = _parse_iso(promo["endsAt"])
        except (KeyError, ValueError):
            continue
        if starts <= now <= ends:
            active_promo = promo
            break

    currency = product.get("currency", FALLBACK_CURRENCY)
    if active_promo:
        return {
            "price": active_promo.get("price", FALLBACK_PRICE),
            "currency": currency,
            "promo_label": active_promo.get("label"),
            "show_countdown": bool(active_promo.get("showCountdown")),
            "ends_at": active_promo.get("endsAt"),
        }
    return {
        "price": product.get("basePrice", FALLBACK_PRICE),
        "currency": currency,
        "promo_label": None,
        "show_countdown": False,
        "ends_at": None,
    }
