import pytest

from celeste.cognition.models import (
    Certainty,
    EntityMention,
    EntityReference,
    EventCandidate,
    EventParticipant,
    ReferenceKind,
    TurnUnderstanding,
)
from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.engine import ConversationEngine
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity
from celeste.memory.fake_entity_repository import FakeEntityRepository
from celeste.memory.entity_resolver import EntityResolver
from celeste.providers.fake import FakeLLMProvider
from celeste.cognition.models import EntityType
from celeste.memory.entity_learner import EntityLearner


def build_engine(
    understanding: TurnUnderstanding,
) -> tuple[ConversationEngine, WorkingMemory]:
    laura = StoredEntity(
        id="person_laura_tiendanimal",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        attributes={
            "works_at": "Tiendanimal",
        },
    )

    repository = FakeEntityRepository(
        entities=[laura],
    )

    working_memory = WorkingMemory()

    entity_resolver = EntityResolver(
        repository,
        user_entity_id="person_user",
    )

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(
            FakeLLMProvider(understanding)
        ),
        entity_resolver=entity_resolver,
        working_memory=working_memory,
        context_resolver=ContextResolver(
            working_memory
        ),
    )

    return engine, working_memory


@pytest.mark.asyncio
async def test_process_returns_understanding():
    expected = TurnUnderstanding(
        overall_confidence=0.98,
    )

    engine, working_memory = build_engine(expected)

    result = await engine.process(
        "Hola Celeste."
    )

    assert result.message == "Hola Celeste."
    assert result.understanding == expected

    assert len(working_memory.turns) == 1
    assert working_memory.turns[0].content == "Hola Celeste."


@pytest.mark.asyncio
async def test_process_resolves_and_remembers_entity():
    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Laura",
                reference=EntityReference(
                    name="Laura",
                    qualifiers={
                        "works_at": "Tiendanimal",
                    },
                ),
            )
        ]
    )

    engine, working_memory = build_engine(
        understanding
    )

    result = await engine.process(
        "He estado con Laura, la de Tiendanimal."
    )

    assert len(result.resolved_references) == 1

    resolution = result.resolved_references[0].resolution

    assert resolution.entity is not None
    assert resolution.entity.id == "person_laura_tiendanimal"

    assert len(working_memory.recent_entities) == 1
    assert (
        working_memory.recent_entities[0].entity.id
        == "person_laura_tiendanimal"
    )


@pytest.mark.asyncio
async def test_same_entity_is_remembered_once_per_turn():
    laura_reference = EntityReference(
        name="Laura",
        qualifiers={
            "works_at": "Tiendanimal",
        },
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Laura",
                reference=laura_reference,
            ),
            EntityMention(
                surface_text="Laura",
                reference=laura_reference,
            ),
        ]
    )

    engine, working_memory = build_engine(
        understanding
    )

    await engine.process(
        "Laura, la de Tiendanimal, me escribió."
    )

    assert len(working_memory.recent_entities) == 1
    assert (
        working_memory.recent_entities[0].mention_count
        == 1
    )


@pytest.mark.asyncio
async def test_process_rejects_empty_message():
    engine, _ = build_engine(
        TurnUnderstanding()
    )

    with pytest.raises(ValueError):
        await engine.process("   ")

@pytest.mark.asyncio
async def test_contextual_pronoun_resolves_to_recent_person():
    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
    )

    repository = FakeEntityRepository(
        entities=[laura],
    )

    working_memory = WorkingMemory()
    working_memory.mention_entity(laura)

    understanding = TurnUnderstanding(
        events=[
            EventCandidate(
                event_type="message_received",
                participants=[
                    EventParticipant(
                        entity=EntityReference(
                            name="ella",
                            reference_kind=ReferenceKind.CONTEXTUAL_PERSON,
                        ),
                        role="sender",
                    )
                ],
                certainty=Certainty.ASSERTED,
            )
        ]
    )

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(
            FakeLLMProvider(understanding)
        ),
        entity_resolver=EntityResolver(
            repository,
            user_entity_id="person_user",
        ),
        working_memory=working_memory,
        context_resolver=ContextResolver(
            working_memory
        ),
    )

    result = await engine.process(
        "Luego ella me escribió."
    )

    resolved = [
        item.resolution
        for item in result.resolved_references
        if item.resolution.entity is not None
    ]

    assert any(
        item.entity.id == "person_laura"
        for item in resolved
    )

@pytest.mark.asyncio
async def test_contextual_pronoun_stays_ambiguous_with_two_people():
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

    repository = FakeEntityRepository(
        entities=[laura, marta],
    )

    working_memory = WorkingMemory()

    working_memory.mention_entity(laura)
    working_memory.mention_entity(marta)

    understanding = TurnUnderstanding(
        events=[
            EventCandidate(
                event_type="left",
                participants=[
                    EventParticipant(
                        entity=EntityReference(
                            name="ella",
                            reference_kind=ReferenceKind.CONTEXTUAL_PERSON,
                        ),
                        role="subject",
                    )
                ],
                certainty=Certainty.ASSERTED,
            )
        ]
    )

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(
            FakeLLMProvider(understanding)
        ),
        entity_resolver=EntityResolver(
            repository,
            user_entity_id="person_user",
        ),
        working_memory=working_memory,
        context_resolver=ContextResolver(
            working_memory
        ),
    )

    result = await engine.process(
        "Después ella se fue."
    )

    ambiguous = [
        item.resolution
        for item in result.resolved_references
        if item.resolution.ambiguous
    ]

    assert ambiguous

@pytest.mark.asyncio
async def test_engine_learns_unknown_explicit_entity():
    repository = FakeEntityRepository(
        entities=[],
        relations=[],
    )

    working_memory = WorkingMemory()

    alicante_reference = EntityReference(
        name="Alicante",
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Alicante",
                type_hint=EntityType.PLACE,
                reference=alicante_reference,
            )
        ]
    )

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(
            FakeLLMProvider(understanding)
        ),
        entity_resolver=EntityResolver(
            repository,
            user_entity_id="person_user",
        ),
        working_memory=working_memory,
        context_resolver=ContextResolver(
            working_memory
        ),
        entity_learner=EntityLearner(
            repository
        ),
    )

    result = await engine.process(
        "Alicante es una ciudad preciosa."
    )

    assert len(result.entity_learning) == 1

    learning = result.entity_learning[0]

    assert learning.created is True
    assert learning.entity is not None
    assert learning.entity.kind == EntityKind.PLACE
    assert learning.entity.canonical_name == "Alicante"

    stored = await repository.find_by_name(
        "Alicante"
    )

    assert len(stored) == 1