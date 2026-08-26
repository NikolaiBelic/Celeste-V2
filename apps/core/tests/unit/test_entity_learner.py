import pytest

from celeste.cognition.models import (
    EntityReference,
    EntityType,
    ReferenceKind,
)
from celeste.memory.entities import (
    EntityKind,
    StoredEntity,
)
from celeste.memory.entity_learner import EntityLearner
from celeste.memory.fake_entity_repository import FakeEntityRepository


@pytest.mark.asyncio
async def test_creates_new_explicit_place():
    repository = FakeEntityRepository(
        entities=[],
        relations=[],
    )

    learner = EntityLearner(repository)

    result = await learner.learn(
        reference=EntityReference(
            name="Alicante",
            reference_kind=ReferenceKind.EXPLICIT_ENTITY,
        ),
        type_hint=EntityType.PLACE,
    )

    assert result.created is True
    assert result.entity is not None
    assert result.entity.canonical_name == "Alicante"
    assert result.entity.kind == EntityKind.PLACE


@pytest.mark.asyncio
async def test_existing_entity_is_reused():
    alicante = StoredEntity(
        id="place_alicante",
        kind=EntityKind.PLACE,
        canonical_name="Alicante",
    )

    repository = FakeEntityRepository(
        entities=[alicante],
        relations=[],
    )

    learner = EntityLearner(repository)

    result = await learner.learn(
        reference=EntityReference(name="Alicante"),
        type_hint=EntityType.PLACE,
    )

    assert result.created is False
    assert result.entity is alicante
    assert result.reason == "already_exists"


@pytest.mark.asyncio
async def test_unknown_type_is_not_created():
    repository = FakeEntityRepository(
        entities=[],
        relations=[],
    )

    learner = EntityLearner(repository)

    result = await learner.learn(
        reference=EntityReference(name="Alicante"),
        type_hint=EntityType.UNKNOWN,
    )

    assert result.created is False
    assert result.entity is None
    assert result.reason == "unsupported_or_unknown_type"


@pytest.mark.asyncio
async def test_contextual_reference_is_not_created():
    repository = FakeEntityRepository(
        entities=[],
        relations=[],
    )

    learner = EntityLearner(repository)

    result = await learner.learn(
        reference=EntityReference(
            surface_text="ella",
            reference_kind=ReferenceKind.CONTEXTUAL_PERSON,
        ),
        type_hint=EntityType.PERSON,
    )

    assert result.created is False
    assert result.entity is None
    assert result.reason == "reference_not_explicit"