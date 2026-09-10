"""Smoke test : vérifie que le package afrosite_llm s'importe sans erreur."""

import pytest

from afrosite_llm.cache import cache_completion_options, is_prompt_cache_enabled
from afrosite_llm.router import generate


def test_package_importable() -> None:
    """Le package afrosite_llm doit s'importer sans lever d'exception."""
    import afrosite_llm  # noqa: F401

    assert afrosite_llm.__version__ == "0.1.0"


def test_prompt_cache_enabled_by_default() -> None:
    """Le prompt cache est activé par défaut selon la spec."""
    assert is_prompt_cache_enabled() is True
    assert cache_completion_options() == {"caching": True, "ttl": 600}


def test_prompt_cache_can_be_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AFROSITE_LLM_PROMPT_CACHE", "0")
    assert is_prompt_cache_enabled() is False
    assert cache_completion_options() == {}


async def test_generate_passes_cache_by_default() -> None:
    result = await generate("Boutique wax à Cadjehoun")
    assert result["cache"]["caching"] is True
    assert result["cache"]["ttl"] == 600
