"""Numéros Bénin uniquement — identifiant CRM, pas une identité globale."""

from __future__ import annotations

import re

_ALLOWED = re.compile(r"^[0-9+ ]+$")


def normalize_bj_phone(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned or not _ALLOWED.match(cleaned):
        raise ValueError("Numéro invalide.")
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    if digits.startswith("00229"):
        digits = digits[2:]
    if digits.startswith("229"):
        national = digits[3:]
    else:
        national = digits
    if len(national) not in (8, 10):
        raise ValueError("Numéro Bénin : 8 ou 10 chiffres.")
    return f"+229{national}"


def phone_path_key(canonical: str) -> str:
    if not canonical.startswith("+229"):
        raise ValueError("Numéro Bénin requis.")
    return canonical[1:]
