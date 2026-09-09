"""Smoke test : vérifie que le package afrosite_llm s'importe sans erreur."""

from afrosite_llm.cache import is_prompt_cache_enabled


def test_package_importable() -> None:
    """Le package afrosite_llm doit s'importer sans lever d'exception."""
    import afrosite_llm  # noqa: F401

    assert afrosite_llm.__version__ == "0.1.0"


def test_prompt_cache_enabled_by_default() -> None:
    """Le prompt cache est activé par défaut selon la spec."""
    assert is_prompt_cache_enabled() is True
