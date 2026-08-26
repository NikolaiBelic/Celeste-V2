import pytest

from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity
from celeste.memory.entity_resolver import EntityResolver
from celeste.memory.fake_entity_repository import FakeEntityRepository
from celeste.providers.ollama import OllamaProvider


@pytest.fixture
def conversation_components():
    user = StoredEntity(
        id="person_user",
        kind=EntityKind.PERSON,
        canonical_name="User",
    )

    laura = StoredEntity(
        id="person_laura_tiendanimal",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        attributes={
            "works_at": "Tiendanimal",
        },
    )

    marta = StoredEntity(
        id="person_marta",
        kind=EntityKind.PERSON,
        canonical_name="Marta",
    )

    repository = FakeEntityRepository(
        entities=[
            user,
            laura,
            marta,
        ],
        relations=[],
    )

    entity_resolver = EntityResolver(
        repository,
        user_entity_id="person_user",
    )

    working_memory = WorkingMemory()

    context_resolver = ContextResolver(
        working_memory
    )

    provider = OllamaProvider(
        model="qwen3.5:9b",
        think=False,
        temperature=0.0,
    )

    understanding_engine = UnderstandingEngine(
        provider
    )

    return (
        understanding_engine,
        entity_resolver,
        working_memory,
        context_resolver,
    )


@pytest.mark.asyncio
async def test_pronoun_resolves_to_single_recent_person(
    conversation_components,
):
    (
        understanding_engine,
        entity_resolver,
        working_memory,
        context_resolver,
    ) = conversation_components

    first_turn = await understanding_engine.understand(
        "He estado con Laura, la que trabaja en Tiendanimal."
    )

    print()
    print("FIRST TURN")
    print(first_turn.model_dump_json(indent=2))

    laura_reference = next(
        (
            entity.reference
            for entity in first_turn.entities
            if entity.reference.name
            and entity.reference.name.casefold() == "laura"
        ),
        None,
    )

    assert laura_reference is not None

    resolved_laura = await entity_resolver.resolve(
        laura_reference
    )

    assert resolved_laura.entity is not None
    assert (
        resolved_laura.entity.id
        == "person_laura_tiendanimal"
    )

    working_memory.mention_entity(
        resolved_laura.entity
    )

    second_turn = await understanding_engine.understand(
        "Luego ella me escribió."
    )

    print()
    print("SECOND TURN")
    print(second_turn.model_dump_json(indent=2))

    contextual_resolution = (
        context_resolver.resolve_recent_person()
    )

    print()
    print("CONTEXT RESOLUTION")
    print(
        contextual_resolution.model_dump_json(
            indent=2
        )
    )

    assert contextual_resolution.entity is not None
    assert (
        contextual_resolution.entity.id
        == "person_laura_tiendanimal"
    )
    assert contextual_resolution.ambiguous is False


def test_pronoun_stays_ambiguous_with_two_recent_people(
    conversation_components,
):
    (
        _,
        _,
        working_memory,
        context_resolver,
    ) = conversation_components

    laura = StoredEntity(
        id="person_laura_tiendanimal",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    marta = StoredEntity(
        id="person_marta",
        kind=EntityKind.PERSON,
        canonical_name="Marta",
    )

    working_memory.mention_entity(laura)
    working_memory.mention_entity(marta)

    result = context_resolver.resolve_recent_person()

    assert result.entity is None
    assert result.ambiguous is True
    assert result.strategy == "multiple_recent_people"