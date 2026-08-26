from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity


def test_resolves_single_recent_person():
    memory = WorkingMemory()

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    memory.mention_entity(laura)

    resolver = ContextResolver(memory)

    result = resolver.resolve_recent_person()

    assert result.entity is not None
    assert result.entity.id == "person_laura"
    assert result.ambiguous is False


def test_multiple_people_are_not_guessed():
    memory = WorkingMemory()

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    marta = StoredEntity(
        id="person_marta",
        kind=EntityKind.PERSON,
        canonical_name="Marta",
    )

    memory.mention_entity(laura)
    memory.mention_entity(marta)

    resolver = ContextResolver(memory)

    result = resolver.resolve_recent_person()

    assert result.entity is None
    assert result.ambiguous is True


def test_dominant_recent_person_can_be_resolved():
    memory = WorkingMemory()

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    marta = StoredEntity(
        id="person_marta",
        kind=EntityKind.PERSON,
        canonical_name="Marta",
    )

    memory.mention_entity(
        marta,
        salience=0.4,
    )

    memory.mention_entity(
        laura,
        salience=0.9,
    )

    memory.mention_entity(
        laura,
        salience=0.9,
    )

    resolver = ContextResolver(memory)

    result = resolver.resolve_recent_person()

    assert result.entity is not None
    assert result.entity.id == "person_laura"
    assert result.strategy == "dominant_recent_person"