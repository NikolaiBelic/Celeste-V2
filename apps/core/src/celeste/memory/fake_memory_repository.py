from __future__ import annotations

from celeste.memory.models import (
    MemoryCorrection,
    MemoryEvent,
    MemoryRecord,
    MemoryRecordStatus,
)
from celeste.memory.repository import MemoryRepository


class FakeMemoryRepository(MemoryRepository):
    def __init__(self) -> None:
        self.records: dict[str, MemoryRecord] = {}
        self.events: dict[str, MemoryEvent] = {}
        self.corrections: dict[str, MemoryCorrection] = {}

    async def add_record(
        self,
        record: MemoryRecord,
    ) -> None:
        self.records[record.id] = record

    async def update_record(
        self,
        record: MemoryRecord,
    ) -> None:
        self.records[record.id] = record

    async def get_record(
        self,
        record_id: str,
    ) -> MemoryRecord | None:
        return self.records.get(record_id)

    async def find_active_records(
        self,
        *,
        subject_id: str,
        predicate: str,
    ) -> list[MemoryRecord]:
        return [
            record
            for record in self.records.values()
            if record.subject_id == subject_id
            and record.predicate == predicate
            and record.status == MemoryRecordStatus.ACTIVE
        ]

    async def add_event(
        self,
        event: MemoryEvent,
    ) -> None:
        self.events[event.id] = event

    async def add_correction(
        self,
        correction: MemoryCorrection,
    ) -> None:
        self.corrections[correction.id] = correction