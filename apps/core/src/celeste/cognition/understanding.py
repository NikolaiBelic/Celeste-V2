from __future__ import annotations

from celeste.cognition.models import TurnUnderstanding
from celeste.providers.base import LLMProvider


UNDERSTANDING_SYSTEM_PROMPT = """
You are the semantic understanding component of Celeste.

Your job is to convert natural human language into structured meaning.

Do not answer the user.
Do not modify memory.
Do not invent database identifiers.
Do not assume uncertain information is factual.

Extract only meaning supported by the message and supplied context.
"""


class UnderstandingEngine:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def understand(
        self,
        message: str,
        *,
        context: str | None = None,
    ) -> TurnUnderstanding:
        if not message.strip():
            raise ValueError("Message cannot be empty")

        user_prompt = self._build_prompt(
            message=message,
            context=context,
        )

        return await self._provider.generate_structured(
            system_prompt=UNDERSTANDING_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=TurnUnderstanding,
        )

    @staticmethod
    def _build_prompt(
        *,
        message: str,
        context: str | None,
    ) -> str:
        if context:
            return (
                f"CONTEXT:\n{context}\n\n"
                f"USER MESSAGE:\n{message}"
            )

        return f"USER MESSAGE:\n{message}"
