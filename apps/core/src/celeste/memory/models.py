from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryRecordKind(str, Enum):
    FACT = "fact"
    RELATION = "relation"
    EVENT = "event"


class MemoryRecordStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    RETRACTED = "retracted"


class MemorySourceKind(str, Enum):
    USER = "user"
    INFERENCE = "inference"
    SYSTEM = "system"


class MemoryRecord(BaseModel):
    id: str

    kind: MemoryRecordKind

    subject_id: str
    predicate: str

    object_entity_id: str | None = None
    value: Any | None = None

    valid_from: datetime | None = None
    valid_until: datetime | None = None

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    status: MemoryRecordStatus = MemoryRecordStatus.ACTIVE

    source_kind: MemorySourceKind = MemorySourceKind.USER
    source_turn_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class MemoryEvent(BaseModel):
    id: str

    event_type: str

    participant_ids: list[str] = Field(default_factory=list)

    occurred_at: datetime | None = None

    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    attributes: dict[str, Any] = Field(default_factory=dict)

    source_turn_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class MemoryCorrection(BaseModel):
    id: str

    target_record_id: str

    replacement_record_id: str | None = None

    reason: str | None = None

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    source_turn_id: str | None = None