"""LiteLLM router interface wrapper."""

from collections.abc import AsyncGenerator
from typing import Any

from afrosite_llm.cache import cache_completion_options


async def generate(prompt: str, model: str = "gpt-4o-mini", **kwargs: Any) -> dict[str, Any]:
    """Generate completion using configured LLM router."""
    options = {**cache_completion_options(), **kwargs}
    return {
        "content": "Placeholder response",
        "model": model,
        "prompt_preview": prompt[:80],
        "cache": {key: options[key] for key in ("caching", "ttl") if key in options},
    }


async def stream(
    prompt: str, model: str = "gpt-4o-mini", **kwargs: Any
) -> AsyncGenerator[str, None]:
    """Stream completion tokens."""
    _ = (prompt, model, kwargs, cache_completion_options())
    yield "Placeholder"
    yield " response"
