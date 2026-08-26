from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import uuid4

from celeste.memory.models import (
    MemoryCorrection,
    MemoryRecord,
    MemoryRecordKind,
    MemoryRecordStatus,
)
from celeste.memory.repository import MemoryRepository


class ReconciliationAction(str, Enum):
    ADDED = "added"
    UNCHANGED = "unchanged"
    SUPERSEDED = "superseded"
    CORRECTED = "corrected"


@dataclass
class ReconciliationResult:
    action: ReconciliationAction

    current_record: MemoryRecord

    previous_record: MemoryRecord | None = None
    correction: MemoryCorrection | None = None


class MemoryReconciler:
    def __init__(
        self,
        repository: MemoryRepository,
    ) -> None:
        self._repository = repository

    async def reconcile_fact(
        self,
        *,
        subject_id: str,
        predicate: str,
        object_entity_id: str | None = None,
        value: object | None = None,
        source_turn_id: str | None = None,
        confidence: float = 1.0,
        is_correction: bool = False,
    ) -> ReconciliationResult:
        if object_entity_id is None and value is None:
            raise ValueError(
                "A memory fact requires object_entity_id or value"
            )

        active_records = (
            await self._repository.find_active_records(
                subject_id=subject_id,
                predicate=predicate,
            )
        )

        matching = next(
            (
                record
                for record in active_records
                if self._same_value(
                    record,
                    object_entity_id=object_entity_id,
                    value=value,
                )
            ),
            None,
        )

        if matching is not None:
            return ReconciliationResult(
                action=ReconciliationAction.UNCHANGED,
                current_record=matching,
            )

        new_record = MemoryRecord(
            id=self._new_id("memory"),
            kind=MemoryRecordKind.FACT,
            subject_id=subject_id,
            predicate=predicate,
            object_entity_id=object_entity_id,
            value=value,
            source_turn_id=source_turn_id,
            confidence=confidence,
        )

        if not active_records:
            await self._repository.add_record(
                new_record
            )

            return ReconciliationResult(
                action=ReconciliationAction.ADDED,
                current_record=new_record,
            )

        previous = active_records[0]

        if is_correction:
            previous.status = MemoryRecordStatus.RETRACTED

            await self._repository.update_record(
                previous
            )

            await self._repository.add_record(
                new_record
            )

            correction = MemoryCorrection(
                id=self._new_id("correction"),
                target_record_id=previous.id,
                replacement_record_id=new_record.id,
                source_turn_id=source_turn_id,
                reason="Previous information was corrected.",
            )

            await self._repository.add_correction(
                correction
            )

            return ReconciliationResult(
                action=ReconciliationAction.CORRECTED,
                current_record=new_record,
                previous_record=previous,
                correction=correction,
            )

        previous.status = MemoryRecordStatus.SUPERSEDED

        await self._repository.update_record(
            previous
        )

        await self._repository.add_record(
            new_record
        )

        return ReconciliationResult(
            action=ReconciliationAction.SUPERSEDED,
            current_record=new_record,
            previous_record=previous,
        )

    @staticmethod
    def _same_value(
        record: MemoryRecord,
        *,
        object_entity_id: str | None,
        value: object | None,
    ) -> bool:
        return (
            record.object_entity_id == object_entity_id
            and record.value == value
        )

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex}"