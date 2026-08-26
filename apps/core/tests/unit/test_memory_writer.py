import pytest

from celeste.cognition.models import (
    Claim,
    EntityClaimObject,
    EntityReference,
    TurnUnderstanding,
    ValueClaimObject,
)
from celeste.memory.entities import (
    EntityKind,
    ResolutionResult,
    StoredEntity,
)
from celeste.memory.fake_memory_repository import (
    FakeMemoryRepository,
)
from celeste.memory.reconciler import MemoryReconciler
from celeste.memory.writer import (
    MemoryWriter,
    ResolvedMemoryReference,
)


@pytest.mark.asyncio
async def test_writer_persists_resolved_claim():
    repository = FakeMemoryRepository()

    writer = MemoryWriter(
        MemoryReconciler(repository)
    )

    laura_reference = EntityReference(
        name="Laura"
    )

    understanding = TurnUnderstanding(
        claims=[
            Claim(
                subject=laura_reference,
                predicate="works_at",
                object=ValueClaimObject(
                    value="Tiendanimal"
                ),
            )
        ]
    )

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    result = await writer.write(
        understanding=understanding,
        resolved_references=[
            ResolvedMemoryReference(
                reference=laura_reference,
                resolution=ResolutionResult(
                    entity=laura,
                    confidence=0.98,
                    strategy="canonical_name",
                    ambiguous=False,
                ),
            )
        ],
    )

    assert len(result.reconciliations) == 1
    assert len(result.skipped_claims) == 0

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="works_at",
    )

    assert len(active) == 1
    assert active[0].value == "Tiendanimal"


@pytest.mark.asyncio
async def test_writer_does_not_store_unresolved_subject():
    repository = FakeMemoryRepository()

    writer = MemoryWriter(
        MemoryReconciler(repository)
    )

    unknown_reference = EntityReference(
        name="Laura"
    )

    claim = Claim(
        subject=unknown_reference,
        predicate="works_at",
        object=ValueClaimObject(
            value="Tiendanimal"
        ),
    )

    understanding = TurnUnderstanding(
        claims=[claim]
    )

    result = await writer.write(
        understanding=understanding,
        resolved_references=[],
    )

    assert len(result.reconciliations) == 0
    assert result.skipped_claims == [claim]
    assert len(repository.records) == 0


@pytest.mark.asyncio
async def test_writer_resolves_entity_object():
    repository = FakeMemoryRepository()

    writer = MemoryWriter(
        MemoryReconciler(repository)
    )

    laura_reference = EntityReference(
        name="Laura"
    )

    company_reference = EntityReference(
        name="Tiendanimal"
    )

    understanding = TurnUnderstanding(
        claims=[
            Claim(
                subject=laura_reference,
                predicate="works_at",
                object=EntityClaimObject(
                    entity=company_reference
                ),
            )
        ]
    )

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    company = StoredEntity(
        id="org_tiendanimal",
        kind=EntityKind.ORGANIZATION,
        canonical_name="Tiendanimal",
    )

    result = await writer.write(
        understanding=understanding,
        resolved_references=[
            ResolvedMemoryReference(
                reference=laura_reference,
                resolution=ResolutionResult(
                    entity=laura,
                    confidence=0.98,
                    strategy="canonical_name",
                    ambiguous=False,
                ),
            ),
            ResolvedMemoryReference(
                reference=company_reference,
                resolution=ResolutionResult(
                    entity=company,
                    confidence=0.98,
                    strategy="canonical_name",
                    ambiguous=False,
                ),
            ),
        ],
    )

    assert len(result.reconciliations) == 1

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="works_at",
    )

    assert len(active) == 1
    assert (
        active[0].object_entity_id
        == "org_tiendanimal"
    )