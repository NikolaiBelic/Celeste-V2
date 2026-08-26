from __future__ import annotations

from typing import TypeVar

from ollama import AsyncClient
from pydantic import BaseModel

from celeste.providers.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class OllamaProvider(LLMProvider):
    def __init__(
        self,
        model: str,
        *,
        host: str = "http://localhost:11434",
        think: bool = False,
        temperature: float = 0.0,
    ) -> None:
        self.model = model
        self.think = think
        self.temperature = temperature
        self._client = AsyncClient(host=host)

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = await self._client.chat(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            format=response_model.model_json_schema(),
            think=self.think,
            options={
                "temperature": self.temperature,
            },
        )

        content = response.message.content

        if not content:
            raise RuntimeError(
                f"Model {self.model!r} returned an empty response"
            )

        return response_model.model_validate_json(content)