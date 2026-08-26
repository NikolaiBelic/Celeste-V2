from __future__ import annotations

from dataclasses import dataclass

from celeste.cognition.models import (
    EntityMention,
    EntityReference,
    EntityType,
    TurnUnderstanding,
)


@dataclass
class EntityTypeResolution:
    mention: EntityMention
    entity_type: EntityType
    confidence: float
    reason: str


class EntityTypeResolver:
    """
    Infers entity types from the structured semantics of a turn.

    This resolver does not inspect natural-language wording directly.
    It relies on canonical predicates already extracted by the
    UnderstandingEngine.
    """

    _OBJECT_TYPE_BY_PREDICATE: dict[str, EntityType] = {
        "lives_in": EntityType.PLACE,
        "born_in": EntityType.PLACE,
        "located_in": EntityType.PLACE,
        "works_at": EntityType.ORGANIZATION,
        "studies_at": EntityType.ORGANIZATION,
    }

    def resolve(
        self,
        understanding: TurnUnderstanding,
    ) -> list[EntityTypeResolution]:
        results: list[EntityTypeResolution] = []

        for mention in understanding.entities:
            results.append(
                self._resolve_mention(
                    mention=mention,
                    understanding=understanding,
                )
            )

        return results

    def _resolve_mention(
        self,
        *,
        mention: EntityMention,
        understanding: TurnUnderstanding,
    ) -> EntityTypeResolution:
        if mention.type_hint != EntityType.UNKNOWN:
            return EntityTypeResolution(
                mention=mention,
                entity_type=mention.type_hint,
                confidence=mention.confidence,
                reason="explicit_type_hint",
            )

        for claim in understanding.claims:
            object_reference = claim.object.entity

            if object_reference is None:
                continue

            if not self._same_entity(
                mention.reference,
                object_reference,
            ):
                continue

            inferred_type = self._OBJECT_TYPE_BY_PREDICATE.get(
                claim.predicate.casefold()
            )

            if inferred_type is None:
                continue

            return EntityTypeResolution(
                mention=mention,
                entity_type=inferred_type,
                confidence=min(
                    mention.confidence,
                    claim.confidence,
                ),
                reason=(
                    f"object_of_{claim.predicate.casefold()}"
                ),
            )

        return EntityTypeResolution(
            mention=mention,
            entity_type=EntityType.UNKNOWN,
            confidence=mention.confidence,
            reason="insufficient_semantic_evidence",
        )

    @classmethod
    def _same_entity(
        cls,
        left: EntityReference,
        right: EntityReference,
    ) -> bool:
        left_name = cls._reference_text(left)
        right_name = cls._reference_text(right)

        if left_name is None or right_name is None:
            return False

        return left_name.casefold() == right_name.casefold()

    @staticmethod
    def _reference_text(
        reference: EntityReference,
    ) -> str | None:
        return (
            reference.name
            or reference.surface_text
        )