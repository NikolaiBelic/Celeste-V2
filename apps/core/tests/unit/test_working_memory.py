import pytest

from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity


def test_working_memory_keeps_recent_turns():
    memory = WorkingMemory(
        max_turns=2,
    )

    memory.add_turn(
        role="user",
        content="Hola",
    )

    memory.add_turn(
        role="assistant",
        content="Hola.",
    )

    memory.add_turn(
        role="user",
        content="¿Qué tal?",
    )

    assert len(memory.turns) == 2

    assert memory.turns[0].content == "Hola."
    assert memory.turns[1].content == "¿Qué tal?"


def test_empty_turn_is_rejected():
    memory = WorkingMemory()

    with pytest.raises(ValueError):
        memory.add_turn(
            role="user",
            content="   ",
        )


def test_entity_mentions_are_not_duplicated():
    memory = WorkingMemory()

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    memory.mention_entity(laura)
    memory.mention_entity(laura)

    assert len(memory.recent_entities) == 1

    assert (
        memory.recent_entities[0].mention_count
        == 2
    )


def test_topic_can_be_updated():
    memory = WorkingMemory()

    memory.set_topic("Celeste V2")

    assert memory.current_topic == "Celeste V2"

    memory.set_topic(None)

    assert memory.current_topic is None


def test_clear_removes_working_state():
    memory = WorkingMemory()

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    memory.add_turn(
        role="user",
        content="Estoy hablando de Laura.",
    )

    memory.mention_entity(laura)
    memory.set_topic("Laura")

    memory.clear()

    assert memory.turns == []
    assert memory.recent_entities == []
    assert memory.current_topic is None