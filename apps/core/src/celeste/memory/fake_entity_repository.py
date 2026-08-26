from __future__ import annotations

from celeste.memory.entities import EntityRelation, StoredEntity
from celeste.memory.entity_repository import EntityRepository


class FakeEntityRepository(EntityRepository):
    def __init__(
        self,
        *,
        entities: list[StoredEntity] | None = None,
        relations: list[EntityRelation] | None = None,
    ) -> None:
        self.entities = {
            entity.id: entity
            for entity in (entities or [])
        }

        self.relations = relations or []

    async def add(
        self,
        entity: StoredEntity,
    ) -> StoredEntity:
        self.entities[entity.id] = entity
        return entity

    async def get_by_id(
        self,
        entity_id: str,
    ) -> StoredEntity | None:
        return self.entities.get(entity_id)

    async def find_by_name(
        self,
        name: str,
    ) -> list[StoredEntity]:
        normalized = name.casefold()

        return [
            entity
            for entity in self.entities.values()
            if entity.canonical_name.casefold() == normalized
        ]

    async def find_by_alias(
        self,
        alias: str,
    ) -> list[StoredEntity]:
        normalized = alias.casefold()

        return [
            entity
            for entity in self.entities.values()
            if any(
                candidate.casefold() == normalized
                for candidate in entity.aliases
            )
        ]

    async def find_relation_objects(
        self,
        *,
        subject_id: str,
        predicate: str,
        active_only: bool = True,
    ) -> list[StoredEntity]:
        result: list[StoredEntity] = []

        for relation in self.relations:
            if relation.subject_id != subject_id:
                continue

            if relation.predicate != predicate:
                continue

            if active_only and not relation.active:
                continue

            entity = self.entities.get(relation.object_id)

            if entity is not None:
                result.append(entity)

        return result