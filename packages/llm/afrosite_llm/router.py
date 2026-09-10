"""LiteLLM router interface wrapper."""

from collections.abc import AsyncGenerator
from typing import Any


async def generate(prompt: str, model: str = "gpt-4o-mini", **kwargs: Any) -> dict[str, Any]:
    """Generate completion using configured LLM router."""
    # Placeholder for LLM generation with LiteLLM adapter
    return {"content": "Placeholder response", "model": model}


async def stream(
    prompt: str, model: str = "gpt-4o-mini", **kwargs: Any
) -> AsyncGenerator[str, None]:
    """Stream completion tokens."""
    yield "Placeholder"
    yield " response"
