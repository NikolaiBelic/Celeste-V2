from __future__ import annotations

from dataclasses import dataclass, field
from celeste.cognition.reference_matching import references_match

from celeste.cognition.models import (
    Claim,
    TurnUnderstanding,
)
from celeste.memory.entities import ResolutionResult
from celeste.memory.reconciler import (
    MemoryReconciler,
    ReconciliationResult,
)


@dataclass
class ResolvedMemoryReference:
    reference: object
    resolution: ResolutionResult


@dataclass
class MemoryWriteResult:
    reconciliations: list[ReconciliationResult] = field(
        default_factory=list
    )

    skipped_claims: list[Claim] = field(
        default_factory=list
    )


class MemoryWriter:
    def __init__(
        self,
        reconciler: MemoryReconciler,
    ) -> None:
        self._reconciler = reconciler

    async def write(
        self,
        *,
        understanding: TurnUnderstanding,
        resolved_references: list[ResolvedMemoryReference],
        source_turn_id: str | None = None,
    ) -> MemoryWriteResult:
        result = MemoryWriteResult()

        for claim in understanding.claims:
            subject_id = self._resolve_entity_id(
                claim.subject,
                resolved_references,
            )

            if subject_id is None:
                result.skipped_claims.append(claim)
                continue

            object_entity_id: str | None = None
            value: object | None = None

            if claim.object.entity is not None:
                object_reference = claim.object.entity

                object_entity_id = self._resolve_entity_id(
                    object_reference,
                    resolved_references,
                )

                if object_entity_id is None:
                    literal_fallback = (
                        object_reference.name
                        or object_reference.surface_text
                    )

                    if (
                        literal_fallback
                        and object_reference.reference_kind.value
                        == "explicit_entity"
                    ):
                        value = literal_fallback
                    else:
                        result.skipped_claims.append(claim)
                        continue

            else:
                value = claim.object.value

            reconciliation = (
                await self._reconciler.reconcile_fact(
                    subject_id=subject_id,
                    predicate=claim.predicate,
                    object_entity_id=object_entity_id,
                    value=value,
                    source_turn_id=source_turn_id,
                    confidence=claim.confidence,
                )
            )

            result.reconciliations.append(
                reconciliation
            )

        return result

    def _resolve_entity_id(
        self,
        reference,
        resolved_references,
    ) -> str | None:
        for resolved in resolved_references:
            if references_match(
                resolved.reference,
                reference,
            ):
                if resolved.resolution.entity is not None:
                    return resolved.resolution.entity.id

        return None