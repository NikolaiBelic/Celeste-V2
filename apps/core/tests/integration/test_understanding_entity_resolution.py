import pytest

from celeste.memory.entities import (
    EntityKind,
    EntityRelation,
    StoredEntity,
)
from celeste.memory.entity_resolver import EntityResolver
from celeste.memory.fake_entity_repository import FakeEntityRepository
from celeste.cognition.understanding import UnderstandingEngine
from celeste.providers.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_understanding_and_resolver_disambiguate_same_name():
    user = StoredEntity(
        id="person_user",
        kind=EntityKind.PERSON,
        canonical_name="User",
    )

    partner_laura = StoredEntity(
        id="person_laura_partner",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        attributes={
            "works_at": "Farmacia",
        },
    )

    tiendanimal_laura = StoredEntity(
        id="person_laura_tiendanimal",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        attributes={
            "works_at": "Tiendanimal",
        },
    )

    repository = FakeEntityRepository(
        entities=[
            user,
            partner_laura,
            tiendanimal_laura,
        ],
        relations=[
            EntityRelation(
                subject_id="person_user",
                predicate="current_romantic_partner",
                object_id="person_laura_partner",
            )
        ],
    )

    resolver = EntityResolver(
        repository,
        user_entity_id="person_user",
    )

    provider = OllamaProvider(
        model="qwen3.5:9b",
        think=False,
        temperature=0.0,
    )

    understanding_engine = UnderstandingEngine(provider)

    understanding = await understanding_engine.understand(
        "Laura, la que trabaja en Tiendanimal, me ha escrito."
    )

    print()
    print("UNDERSTANDING")
    print(understanding.model_dump_json(indent=2))

    references = []

    references.extend(
        entity.reference
        for entity in understanding.entities
    )

    for event in understanding.events:
        references.extend(
            participant.entity
            for participant in event.participants
        )

    for claim in understanding.claims:
        references.append(claim.subject)

        if claim.object_entity is not None:
            references.append(claim.object_entity)

    laura_references = [
        reference
        for reference in references
        if reference.name
        and reference.name.casefold() == "laura"
    ]

    assert laura_references, (
        "Qwen understood the turn but did not produce "
        "a structured reference to Laura."
    )

    resolved = [
        await resolver.resolve(reference)
        for reference in laura_references
    ]

    print()
    print("RESOLUTIONS")

    for result in resolved:
        print(result.model_dump_json(indent=2))

    assert any(
        result.entity is not None
        and result.entity.id == "person_laura_tiendanimal"
        for result in resolved
    )