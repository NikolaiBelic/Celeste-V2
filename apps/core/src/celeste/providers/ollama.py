from __future__ import annotations

from typing import TypeVar

from ollama import AsyncClient
from pydantic import BaseModel, ValidationError

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
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        response = await self._client.chat(
            model=self.model,
            messages=messages,
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

        try:
            return response_model.model_validate_json(content)

        except ValidationError as exc:
            repair_prompt = (
                "Your previous structured output was invalid.\n\n"
                "Validation errors:\n"
                f"{exc}\n\n"
                "Pay special attention to semantic validation rules that may "
                "not be fully represented by the JSON schema.\n"
                "If a Claim requires either object_entity or value, ensure "
                "that at least one of them is non-null.\n"
                "Do not repeat the invalid structure.\n\n"
                "Correct the structured output while preserving the "
                "meaning of the original user message.\n"
                "Return only a valid object matching the required schema."
            )

            repair_response = await self._client.chat(
                model=self.model,
                messages=[
                    *messages,
                    {
                        "role": "assistant",
                        "content": content,
                    },
                    {
                        "role": "user",
                        "content": repair_prompt,
                    },
                ],
                format=response_model.model_json_schema(),
                think=self.think,
                options={
                    "temperature": 0.0,
                },
            )

            repaired_content = repair_response.message.content

            if not repaired_content:
                raise RuntimeError(
                    f"Model {self.model!r} returned an empty repair response"
                ) from exc

            return response_model.model_validate_json(
                repaired_content
            )