from __future__ import annotations

from abc import ABC, abstractmethod

from celeste.memory.models import (
    MemoryCorrection,
    MemoryEvent,
    MemoryRecord,
)


class MemoryRepository(ABC):
    @abstractmethod
    async def add_record(
        self,
        record: MemoryRecord,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_record(
        self,
        record: MemoryRecord,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_record(
        self,
        record_id: str,
    ) -> MemoryRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def find_active_records(
        self,
        *,
        subject_id: str,
        predicate: str,
    ) -> list[MemoryRecord]:
        raise NotImplementedError

    @abstractmethod
    async def add_event(
        self,
        event: MemoryEvent,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def add_correction(
        self,
        correction: MemoryCorrection,
    ) -> None:
        raise NotImplementedError