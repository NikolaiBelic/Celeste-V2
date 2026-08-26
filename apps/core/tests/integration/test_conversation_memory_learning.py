import pytest

from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.context_resolver import ContextResolver
from celeste.conversation.engine import ConversationEngine
from celeste.conversation.working_memory import WorkingMemory
from celeste.memory.entities import EntityKind, StoredEntity
from celeste.memory.entity_resolver import EntityResolver
from celeste.memory.fake_entity_repository import FakeEntityRepository
from celeste.memory.fake_memory_repository import FakeMemoryRepository
from celeste.memory.reconciler import MemoryReconciler
from celeste.memory.writer import MemoryWriter
from celeste.providers.ollama import OllamaProvider


@pytest.mark.asyncio
async def test_real_conversation_persists_fact():
    user = StoredEntity(
        id="person_user",
        kind=EntityKind.PERSON,
        canonical_name="User",
    )

    laura = StoredEntity(
        id="person_laura",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        attributes={
            "works_at": "Tiendanimal",
        },
    )

    entity_repository = FakeEntityRepository(
        entities=[
            user,
            laura,
        ],
        relations=[],
    )

    memory_repository = FakeMemoryRepository()
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
            entity_repository,
            user_entity_id="person_user",
        ),
        working_memory=working_memory,
        context_resolver=ContextResolver(
            working_memory
        ),
        memory_writer=MemoryWriter(
            MemoryReconciler(
                memory_repository
            )
        ),
    )

    result = await engine.process(
        "Laura, la que trabaja en Tiendanimal, vive en Alicante."
    )

    print()
    print("UNDERSTANDING")
    print(
        result.understanding.model_dump_json(
            indent=2
        )
    )

    print()
    print("MEMORY WRITE")
    print(result.memory_write)

    active = await memory_repository.find_active_records(
        subject_id="person_laura",
        predicate="lives_in",
    )

    assert len(active) == 1

    assert (
        active[0].value == "Alicante"
        or active[0].object_entity_id is not None
    )