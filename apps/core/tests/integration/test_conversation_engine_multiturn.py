import pytest

from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.engine import ConversationEngine
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity
from celeste.memory.entity_resolver import EntityResolver
from celeste.memory.fake_entity_repository import FakeEntityRepository
from celeste.providers.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_real_multiturn_conversation_keeps_person_context():
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

    repository = FakeEntityRepository(
        entities=[
            user,
            laura,
        ],
        relations=[],
    )

    working_memory = WorkingMemory()

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(
            OllamaProvider(
                model="qwen3.5:9b",
                think=False,
                temperature=0.0,
            )
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

    first = await engine.process(
        "He estado con Laura, la que trabaja en Tiendanimal."
    )

    print()
    print("FIRST TURN")
    print(first.understanding.model_dump_json(indent=2))

    assert any(
        item.resolution.entity is not None
        and item.resolution.entity.id
        == "person_laura_tiendanimal"
        for item in first.resolved_references
    )

    second = await engine.process(
        "Luego ella me escribió."
    )

    print()
    print("SECOND TURN")
    print(second.understanding.model_dump_json(indent=2))

    print()
    print("RESOLVED REFERENCES")

    for item in second.resolved_references:
        print(
            item.reference.model_dump_json(indent=2)
        )
        print(
            item.resolution.model_dump_json(indent=2)
        )

    assert any(
        item.resolution.entity is not None
        and item.resolution.entity.id
        == "person_laura_tiendanimal"
        for item in second.resolved_references
    )

    assert len(working_memory.turns) == 2