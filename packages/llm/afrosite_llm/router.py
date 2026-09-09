"""LiteLLM router interface wrapper."""

from typing import Any, AsyncGenerator, Dict


async def generate(prompt: str, model: str = "gpt-4o-mini", **kwargs: Any) -> Dict[str, Any]:
    """Generate completion using configured LLM router."""
    # Placeholder for LLM generation with LiteLLM adapter
    return {"content": "Placeholder response", "model": model}


async def stream(prompt: str, model: str = "gpt-4o-mini", **kwargs: Any) -> AsyncGenerator[str, None]:
    """Stream completion tokens."""
    yield "Placeholder"
    yield " response"
