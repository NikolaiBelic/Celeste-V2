from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class EntityKind(StrEnum):
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"
    PROJECT = "project"
    OBJECT = "object"
    CONCEPT = "concept"
    OTHER = "other"


class StoredEntity(BaseModel):
    id: str
    kind: EntityKind
    canonical_name: str
    aliases: set[str] = Field(default_factory=set)
    attributes: dict[str, object] = Field(default_factory=dict)


class EntityRelation(BaseModel):
    subject_id: str
    predicate: str
    object_id: str
    active: bool = True


class ResolutionResult(BaseModel):
    entity: StoredEntity | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    strategy: str
    ambiguous: bool = False