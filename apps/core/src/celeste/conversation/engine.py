from __future__ import annotations

from dataclasses import dataclass

from celeste.cognition.models import TurnUnderstanding
from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.memory.entity_resolver import EntityResolver
from celeste.conversation.working_memory import WorkingMemory


@dataclass
class ConversationTurnResult:
    message: str
    understanding: TurnUnderstanding


class ConversationEngine:
    def __init__(
        self,
        *,
        understanding_engine: UnderstandingEngine,
        entity_resolver: EntityResolver,
        working_memory: WorkingMemory,
        context_resolver: ContextResolver,
    ) -> None:
        self._understanding_engine = understanding_engine
        self._entity_resolver = entity_resolver
        self._working_memory = working_memory
        self._context_resolver = context_resolver

    async def process(
        self,
        message: str,
    ) -> ConversationTurnResult:
        if not message.strip():
            raise ValueError("Message cannot be empty")

        understanding = await self._understanding_engine.understand(
            message
        )

        return ConversationTurnResult(
            message=message,
            understanding=understanding,
        )