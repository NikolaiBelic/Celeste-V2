from __future__ import annotations

from dataclasses import dataclass, field

from celeste.cognition.models import (
    EntityReference,
    TurnUnderstanding,
)
from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import ResolutionResult, StoredEntity
from celeste.memory.entity_resolver import EntityResolver


@dataclass
class ResolvedReference:
    reference: EntityReference
    resolution: ResolutionResult


@dataclass
class ConversationTurnResult:
    message: str
    understanding: TurnUnderstanding

    resolved_references: list[ResolvedReference] = field(
        default_factory=list
    )


class ConversationEngine:
    def __init__(
        self,
        *,
        understanding_engine: UnderstandingEngine,
        entity_resolver: EntityResolver,
        working_memory: WorkingMemory,
        context_resolver: ContextResolver,
    ) -> None:
        self._understanding_engine = understanding_engine
        self._entity_resolver = entity_resolver
        self._working_memory = working_memory
        self._context_resolver = context_resolver

    def _is_contextual_person_reference(
        self,
        reference: EntityReference,
    ) -> bool:
        candidates = {
            "ella",
            "él",
            "el",
            "she",
            "he",
            "her",
            "him",
        }

        values = {
            (reference.name or "").casefold(),
            (reference.surface_text or "").casefold(),
        }

        return bool(values & candidates)

    async def process(
        self,
        message: str,
    ) -> ConversationTurnResult:
        if not message.strip():
            raise ValueError("Message cannot be empty")

        understanding = await self._understanding_engine.understand(
            message
        )

        references = self._collect_references(understanding)

        resolved_references: list[ResolvedReference] = []
        mentioned_entities: dict[str, StoredEntity] = {}

        for reference in references:
            if self._is_contextual_person_reference(reference):
                contextual = (
                    self._context_resolver.resolve_recent_person()
                )

                if contextual.entity is not None:
                    resolution = ResolutionResult(
                        entity=contextual.entity,
                        confidence=contextual.confidence,
                        strategy=contextual.strategy,
                        ambiguous=contextual.ambiguous,
                    )
                else:
                    resolution = ResolutionResult(
                        confidence=contextual.confidence,
                        strategy=contextual.strategy,
                        ambiguous=contextual.ambiguous,
                    )

            else:
                resolution = await self._entity_resolver.resolve(
                    reference
                )

            resolved_references.append(
                ResolvedReference(
                    reference=reference,
                    resolution=resolution,
                )
            )

            if resolution.entity is not None:
                mentioned_entities[resolution.entity.id] = (
                    resolution.entity
                )

        self._working_memory.add_turn(
            role="user",
            content=message,
        )

        for entity in mentioned_entities.values():
            self._working_memory.mention_entity(entity)

        return ConversationTurnResult(
            message=message,
            understanding=understanding,
            resolved_references=resolved_references,
        )

    @staticmethod
    def _collect_references(
        understanding: TurnUnderstanding,
    ) -> list[EntityReference]:
        references: list[EntityReference] = []

        references.extend(
            entity.reference
            for entity in understanding.entities
        )

        references.extend(
            understanding.references
        )

        for claim in understanding.claims:
            references.append(claim.subject)

            if claim.object.entity is not None:
                references.append(claim.object.entity)

        for event in understanding.events:
            references.extend(
                participant.entity
                for participant in event.participants
            )

        for correction in understanding.corrections:
            references.append(
                correction.previous.subject
            )

            if correction.previous.object_entity is not None:
                references.append(
                    correction.previous.object_entity
                )

            references.append(
                correction.replacement.subject
            )

            if correction.replacement.object_entity is not None:
                references.append(
                    correction.replacement.object_entity
                )

        return references

    