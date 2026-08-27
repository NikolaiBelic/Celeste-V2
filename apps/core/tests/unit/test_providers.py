from __future__ import annotations

import pytest

from celeste.providers.factory import create_provider
from celeste.providers.ollama import OllamaProvider


def test_factory_creates_default_ollama_provider() -> None:
    provider = create_provider("ollama")

    assert isinstance(provider, OllamaProvider)
    assert provider.model == "qwen3.5:9b"


def test_factory_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unknown provider"):
        create_provider("unknown")


def test_gemini_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "celeste.providers.gemini.load_dotenv",
        lambda: False,
    )
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        create_provider("gemini")
