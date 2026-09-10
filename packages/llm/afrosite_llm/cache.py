"""Prompt cache configuration — activé par défaut (playbook §2, deep 04 §2C)."""

from __future__ import annotations

import os
from typing import Any

_OFF = frozenset({"0", "false", "off", "no"})


def is_prompt_cache_enabled() -> bool:
    """Le cache de prompts est ON sauf AFROSITE_LLM_PROMPT_CACHE=0|false|off|no."""
    raw = os.environ.get("AFROSITE_LLM_PROMPT_CACHE", "1").strip().lower()
    return raw not in _OFF


def cache_completion_options() -> dict[str, Any]:
    """Options LiteLLM à fusionner dans chaque completion."""
    if not is_prompt_cache_enabled():
        return {}
    return {"caching": True, "ttl": 600}
