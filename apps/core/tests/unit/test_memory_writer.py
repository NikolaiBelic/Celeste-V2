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

@pytest.mark.asyncio
async def test_writer_falls_back_to_literal_for_unknown_object_entity():
    repository = FakeMemoryRepository()

    writer = MemoryWriter(
        MemoryReconciler(repository)
    )

    laura_reference = EntityReference(
        surface_text="Laura"
    )

    alicante_reference = EntityReference(
        surface_text="Alicante"
    )

    understanding = TurnUnderstanding(
        claims=[
            Claim(
                subject=laura_reference,
                predicate="lives_in",
                object=EntityClaimObject(
                    entity=alicante_reference
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
            ),
            ResolvedMemoryReference(
                reference=alicante_reference,
                resolution=ResolutionResult(
                    confidence=0.0,
                    strategy="unresolved",
                    ambiguous=False,
                ),
            ),
        ],
    )

    assert len(result.reconciliations) == 1
    assert result.skipped_claims == []

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="lives_in",
    )

    assert len(active) == 1
    assert active[0].value == "Alicante"

@pytest.mark.asyncio
async def test_writer_uses_later_resolved_equivalent_reference():
    repository = FakeMemoryRepository()

    writer = MemoryWriter(
        MemoryReconciler(repository)
    )

    claim_subject = EntityReference(
        surface_text="Laura"
    )

    claim_object = EntityReference(
        surface_text="Alicante"
    )

    learned_reference = EntityReference(
        name="Alicante"
    )

    laura_reference = EntityReference(
        name="Laura"
    )

    understanding = TurnUnderstanding(
        claims=[
            Claim(
                subject=claim_subject,
                predicate="lives_in",
                object=EntityClaimObject(
                    entity=claim_object
                ),
            )
        ]
    )

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    alicante = StoredEntity(
        id="place_alicante",
        kind=EntityKind.PLACE,
        canonical_name="Alicante",
    )

    await writer.write(
        understanding=understanding,
        resolved_references=[
            ResolvedMemoryReference(
                reference=laura_reference,
                resolution=ResolutionResult(
                    entity=laura,
                    confidence=1.0,
                    strategy="canonical_name",
                    ambiguous=False,
                ),
            ),
            ResolvedMemoryReference(
                reference=claim_object,
                resolution=ResolutionResult(
                    confidence=0.0,
                    strategy="unresolved",
                    ambiguous=False,
                ),
            ),
            ResolvedMemoryReference(
                reference=learned_reference,
                resolution=ResolutionResult(
                    entity=alicante,
                    confidence=0.95,
                    strategy="learned_entity",
                    ambiguous=False,
                ),
            ),
        ],
    )

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="lives_in",
    )

    assert len(active) == 1
    assert active[0].object_entity_id == "place_alicante"
    assert active[0].value is None