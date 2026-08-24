"""
license_validator.py — verificare cod serial pentru GDC Production Manager.
ACEST FIȘIER se distribuie cu aplicația. Conține doar cheia PUBLICĂ —
sigur de distribuit, nu compromite nimic.
"""

import os
import license_core
import machine_id

# ─────────────────────────────────────────────────────────────────────
# Aceeași cheie publică folosită de toate produsele GDC (DataMover,
# CursorPro GDC, gdc-resolve-encoder) — aceeași cheie privată, la Cristi,
# semnează pentru fiecare produs; product_id-ul de mai jos e ce le
# separă.
PUBLIC_KEY_B64 = "I1h23MNMRbOhc0ObKJrfa3oFHKA9w+SzbNrroAIy8hs="

PRODUCT_ID = "gdc-production-manager"
# ─────────────────────────────────────────────────────────────────────


def check(serial):
    current_machine_id = machine_id.get_machine_id_display()
    # machine_id_available: vezi kill-switch diferentiat din machine_id.py /
    # license_manager.py — o citire esuata de hardware NU trebuie tratata ca
    # "alta masina".
    return license_core.validate_serial_compact(
        PUBLIC_KEY_B64, serial, PRODUCT_ID,
        machine_id_b32=current_machine_id,
        machine_id_available=machine_id.is_available(),
    )
