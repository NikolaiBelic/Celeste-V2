from __future__ import annotations

import os
from typing import Any, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

from celeste.providers.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class GeminiProvider(LLMProvider):
    """Gemini implementation of Celeste's provider contract."""

    def __init__(
        self,
        model: str = "gemini-3.5-flash",
        *,
        api_key: str | None = None,
        temperature: float = 0.0,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.temperature = temperature

        if client is not None:
            self._client = client
            return

        load_dotenv()
        resolved_api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not resolved_api_key:
            raise RuntimeError(
                "Gemini requires the GEMINI_API_KEY environment variable"
            )

        self._client = genai.Client(api_key=resolved_api_key)

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        response = await self._generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=response_model,
            temperature=self.temperature,
        )
        content = response.text

        if not content:
            raise RuntimeError(
                f"Model {self.model!r} returned an empty response"
            )

        try:
            return response_model.model_validate_json(content)
        except ValidationError as exc:
            repair_prompt = (
                f"Original request:\n{user_prompt}\n\n"
                "Your previous structured output did not satisfy the "
                "required response model.\n\n"
                f"Previous output:\n{content}\n\n"
                f"Validation errors:\n{exc}\n\n"
                "Correct the structured output while preserving the meaning "
                "of the original request. Do not invent information."
            )
            repaired = await self._generate(
                system_prompt=system_prompt,
                user_prompt=repair_prompt,
                response_model=response_model,
                temperature=0.0,
            )

            if not repaired.text:
                raise RuntimeError(
                    f"Model {self.model!r} returned an empty repair response"
                ) from exc

            return response_model.model_validate_json(repaired.text)

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        temperature: float,
    ) -> Any:
        return await self._client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                response_mime_type="application/json",
                response_json_schema=response_model.model_json_schema(),
            ),
        )
