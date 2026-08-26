from __future__ import annotations

from abc import ABC, abstractmethod

from celeste.memory.entities import EntityRelation, StoredEntity


class EntityRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self,
        entity_id: str,
    ) -> StoredEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def find_by_name(
        self,
        name: str,
    ) -> list[StoredEntity]:
        raise NotImplementedError

    @abstractmethod
    async def find_by_alias(
        self,
        alias: str,
    ) -> list[StoredEntity]:
        raise NotImplementedError

    @abstractmethod
    async def find_relation_objects(
        self,
        *,
        subject_id: str,
        predicate: str,
        active_only: bool = True,
    ) -> list[StoredEntity]:
        raise NotImplementedError

    @abstractmethod
    async def add(
        self,
        entity: StoredEntity,
    ) -> StoredEntity:
        raise NotImplementedError