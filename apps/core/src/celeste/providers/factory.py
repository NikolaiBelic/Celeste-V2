from __future__ import annotations

from typing import Any

from celeste.providers.base import LLMProvider


DEFAULT_MODELS = {
    "ollama": "qwen3.5:9b",
    "gemini": "gemini-3.5-flash",
}


def create_provider(
    provider: str,
    *,
    model: str | None = None,
    temperature: float = 0.0,
    **options: Any,
) -> LLMProvider:
    """Create an LLM provider without coupling callers to its SDK."""
    provider_name = provider.strip().lower()
    selected_model = model or DEFAULT_MODELS.get(provider_name)

    if provider_name == "ollama":
        from celeste.providers.ollama import OllamaProvider

        return OllamaProvider(
            model=selected_model or DEFAULT_MODELS["ollama"],
            temperature=temperature,
            **options,
        )

    if provider_name == "gemini":
        from celeste.providers.gemini import GeminiProvider

        return GeminiProvider(
            model=selected_model or DEFAULT_MODELS["gemini"],
            temperature=temperature,
            **options,
        )

    available = ", ".join(sorted(DEFAULT_MODELS))
    raise ValueError(
        f"Unknown provider {provider!r}. Available providers: {available}"
    )
