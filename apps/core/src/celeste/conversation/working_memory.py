from __future__ import annotations

from collections import deque
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from celeste.memory.entities import StoredEntity


class RecentEntity(BaseModel):
    entity: StoredEntity

    last_mentioned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    mention_count: int = 1

    salience: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class WorkingTurn(BaseModel):
    role: str
    content: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class WorkingMemory:
    def __init__(
        self,
        *,
        max_turns: int = 20,
        max_recent_entities: int = 10,
    ) -> None:
        self.max_turns = max_turns
        self.max_recent_entities = max_recent_entities

        self._turns: deque[WorkingTurn] = deque(
            maxlen=max_turns
        )

        self._recent_entities: dict[str, RecentEntity] = {}

        self.current_topic: str | None = None

    @property
    def turns(self) -> list[WorkingTurn]:
        return list(self._turns)

    @property
    def recent_entities(self) -> list[RecentEntity]:
        return sorted(
            self._recent_entities.values(),
            key=lambda item: item.last_mentioned_at,
            reverse=True,
        )

    def add_turn(
        self,
        *,
        role: str,
        content: str,
    ) -> None:
        if not content.strip():
            raise ValueError("Turn content cannot be empty")

        self._turns.append(
            WorkingTurn(
                role=role,
                content=content,
            )
        )

    def mention_entity(
        self,
        entity: StoredEntity,
        *,
        salience: float = 1.0,
    ) -> None:
        existing = self._recent_entities.get(entity.id)

        if existing is not None:
            existing.last_mentioned_at = datetime.now(UTC)
            existing.mention_count += 1
            existing.salience = max(
                existing.salience,
                salience,
            )
        else:
            self._recent_entities[entity.id] = RecentEntity(
                entity=entity,
                salience=salience,
            )

        self._trim_entities()

    def set_topic(
        self,
        topic: str | None,
    ) -> None:
        if topic is not None:
            topic = topic.strip()

            if not topic:
                topic = None

        self.current_topic = topic

    def clear(self) -> None:
        self._turns.clear()
        self._recent_entities.clear()
        self.current_topic = None

    def _trim_entities(self) -> None:
        if len(self._recent_entities) <= self.max_recent_entities:
            return

        ranked = sorted(
            self._recent_entities.values(),
            key=lambda item: (
                item.salience,
                item.last_mentioned_at,
            ),
            reverse=True,
        )

        keep_ids = {
            item.entity.id
            for item in ranked[: self.max_recent_entities]
        }

        self._recent_entities = {
            entity_id: item
            for entity_id, item in self._recent_entities.items()
            if entity_id in keep_ids
        }