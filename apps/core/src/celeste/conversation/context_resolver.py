from __future__ import annotations

from pydantic import BaseModel, Field

from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import StoredEntity


class ContextEntityResolution(BaseModel):
    entity: StoredEntity | None = None

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    strategy: str

    ambiguous: bool = False


class ContextResolver:
    def __init__(
        self,
        working_memory: WorkingMemory,
    ) -> None:
        self._working_memory = working_memory

    def resolve_recent_person(
        self,
    ) -> ContextEntityResolution:
        people = [
            recent
            for recent in self._working_memory.recent_entities
            if recent.entity.kind.value == "person"
        ]

        if not people:
            return ContextEntityResolution(
                confidence=0.0,
                strategy="no_recent_person",
            )

        if len(people) == 1:
            return ContextEntityResolution(
                entity=people[0].entity,
                confidence=0.9,
                strategy="single_recent_person",
            )

        first = people[0]
        second = people[1]

        if (
            first.salience > second.salience
            and first.mention_count > second.mention_count
        ):
            return ContextEntityResolution(
                entity=first.entity,
                confidence=0.75,
                strategy="dominant_recent_person",
            )

        return ContextEntityResolution(
            confidence=0.0,
            strategy="multiple_recent_people",
            ambiguous=True,
        )