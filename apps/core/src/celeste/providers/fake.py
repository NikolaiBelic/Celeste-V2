from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

from celeste.providers.base import LLMProvider


T = TypeVar("T", bound=BaseModel)


class FakeLLMProvider(LLMProvider):
    def __init__(self, response: BaseModel) -> None:
        self.response = response
        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt

        if not isinstance(self.response, response_model):
            raise TypeError(
                f"Expected {response_model.__name__}, "
                f"got {type(self.response).__name__}"
            )

        return self.response
