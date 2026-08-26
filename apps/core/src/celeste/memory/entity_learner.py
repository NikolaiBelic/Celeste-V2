from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from celeste.cognition.models import (
    EntityReference,
    EntityType,
    ReferenceKind,
)
from celeste.memory.entities import (
    EntityKind,
    StoredEntity,
)
from celeste.memory.entity_repository import EntityRepository


@dataclass
class EntityLearningResult:
    entity: StoredEntity | None
    created: bool
    reason: str


class EntityLearner:
    def __init__(
        self,
        repository: EntityRepository,
    ) -> None:
        self._repository = repository

    async def learn(
        self,
        *,
        reference: EntityReference,
        type_hint: EntityType,
    ) -> EntityLearningResult:
        if reference.reference_kind != ReferenceKind.EXPLICIT_ENTITY:
            return EntityLearningResult(
                entity=None,
                created=False,
                reason="reference_not_explicit",
            )

        name = reference.name or reference.surface_text

        if not name:
            return EntityLearningResult(
                entity=None,
                created=False,
                reason="missing_name",
            )

        existing = await self._repository.find_by_name(name)

        if existing:
            if len(existing) == 1:
                return EntityLearningResult(
                    entity=existing[0],
                    created=False,
                    reason="already_exists",
                )

            return EntityLearningResult(
                entity=None,
                created=False,
                reason="ambiguous_existing_entities",
            )

        kind = self._map_kind(type_hint)

        if kind is None:
            return EntityLearningResult(
                entity=None,
                created=False,
                reason="unsupported_or_unknown_type",
            )

        entity = StoredEntity(
            id=f"{kind.value}_{uuid4().hex}",
            kind=kind,
            canonical_name=name,
        )

        await self._repository.add(entity)

        return EntityLearningResult(
            entity=entity,
            created=True,
            reason="created",
        )

    @staticmethod
    def _map_kind(
        type_hint: EntityType,
    ) -> EntityKind | None:
        mapping = {
            EntityType.PERSON: EntityKind.PERSON,
            EntityType.PLACE: EntityKind.PLACE,
            EntityType.ORGANIZATION: EntityKind.ORGANIZATION,
        }

        return mapping.get(type_hint)