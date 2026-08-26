from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class Certainty(str, Enum):
    ASSERTED = "asserted"
    INFERRED = "inferred"
    UNCERTAIN = "uncertain"
    DENIED = "denied"


class SpeechActType(str, Enum):
    INFORM = "inform"
    ASK = "ask"
    REQUEST = "request"
    CORRECT = "correct"
    CONFIRM = "confirm"
    DENY = "deny"
    SPECULATE = "speculate"
    REFLECT = "reflect"
    JOKE = "joke"
    GREET = "greet"


class EntityType(str, Enum):
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"
    PROJECT = "project"
    DEVICE = "device"
    PET = "pet"
    VEHICLE = "vehicle"
    DOCUMENT = "document"
    GAME = "game"
    CONCEPT = "concept"
    UNKNOWN = "unknown"


class TemporalKind(str, Enum):
    CURRENT = "current"
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    RANGE = "range"
    EVENT_RELATIVE = "event_relative"
    UNKNOWN = "unknown"


class MemoryCandidateType(str, Enum):
    CLAIM = "claim"
    EVENT = "event"
    CORRECTION = "correction"
    ENTITY = "entity"


class PersistenceHint(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EntityReference(BaseModel):
    known_entity_id: UUID | None = None
    name: str | None = None
    contextual_role: str | None = None
    surface_text: str | None = None
    qualifiers: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def ensure_reference_exists(self) -> EntityReference:
        if not any(
            (
                self.known_entity_id,
                self.name,
                self.contextual_role,
                self.surface_text,
            )
        ):
            raise ValueError(
                "EntityReference requires at least one identifying reference"
            )
        return self


class EntityMention(BaseModel):
    surface_text: str
    type_hint: EntityType = EntityType.UNKNOWN
    resolved: bool = False
    reference: EntityReference | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TemporalExpression(BaseModel):
    surface_text: str | None = None
    kind: TemporalKind
    absolute_datetime: datetime | None = None
    relative_value: str | None = None
    anchor_description: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Claim(BaseModel):
    subject: EntityReference
    predicate: str

    object_entity: EntityReference | None = None
    value: Any | None = None

    polarity: Literal["positive", "negative"] = "positive"
    certainty: Certainty
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    temporal: TemporalExpression | None = None

    @model_validator(mode="after")
    def ensure_object_or_value(self) -> Claim:
        if self.object_entity is None and self.value is None:
            raise ValueError(
                "Claim requires either object_entity or value"
            )
        return self


class EventParticipant(BaseModel):
    entity: EntityReference
    role: str


class EventCandidate(BaseModel):
    event_type: str = Field(
    description=(
        "A real-world event or state transition. "
        "Do not use this field for corrections to information."
        )
    )
    participants: list[EventParticipant] = Field(min_length=1)

    temporal: TemporalExpression | None = None

    state_domain: str | None = None
    state_change: str | None = None

    attributes: dict[str, Any] = Field(default_factory=dict)

    certainty: Certainty
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    importance_hint: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class ClaimDescriptor(BaseModel):
    subject: EntityReference

    predicate: str = Field(
        description=(
            "Semantic property or relationship being described, "
            "for example lives_in, works_at or owns."
        )
    )

    object_entity: EntityReference | None = None
    value: Any | None = None


class CorrectionCandidate(BaseModel):
    previous: ClaimDescriptor = Field(
        description=(
            "The previous information that the user explicitly says "
            "was incorrect."
        )
    )

    replacement: ClaimDescriptor | None = Field(
        default=None,
        description=(
            "The corrected information, if the user provides it."
        ),
    )

    correction_type: Literal[
        "replace",
        "retract",
        "clarify",
    ]

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class ReferenceResolution(BaseModel):
    surface_text: str
    reference: EntityReference
    resolution_basis: Literal[
        "explicit_name",
        "conversation_context",
        "world_state",
        "recent_entity",
        "semantic_context",
        "unresolved",
    ]

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SpeechAct(BaseModel):
    type: SpeechActType
    text_span: str | None = None
    target: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class MemoryCandidate(BaseModel):
    type: MemoryCandidateType
    source_index: int = Field(ge=0)
    persistence_hint: PersistenceHint
    reason: str | None = None


class Uncertainty(BaseModel):
    target: str
    reason: str
    severity: Literal["low", "medium", "high"]
    clarification_recommended: bool = False


class TurnUnderstanding(BaseModel):
    speech_acts: list[SpeechAct] = Field(default_factory=list)
    entities: list[EntityMention] = Field(default_factory=list)
    references: list[ReferenceResolution] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    events: list[EventCandidate] = Field(default_factory=list)
    corrections: list[CorrectionCandidate] = Field(
    default_factory=list,
    description=(
        "Explicit corrections to previously communicated information. "
        "Corrections are NOT real-world events."
        ),
    )
    memory_candidates: list[MemoryCandidate] = Field(default_factory=list)
    uncertainties: list[Uncertainty] = Field(default_factory=list)

    requires_context_resolution: bool = False
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
