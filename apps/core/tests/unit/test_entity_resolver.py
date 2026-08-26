import pytest

from celeste.cognition.models import EntityReference
from celeste.memory.entities import (
    EntityKind,
    EntityRelation,
    StoredEntity,
)
from celeste.memory.entity_resolver import EntityResolver
from celeste.memory.fake_entity_repository import FakeEntityRepository


@pytest.fixture
def resolver() -> EntityResolver:
    user = StoredEntity(
        id="person_user",
        kind=EntityKind.PERSON,
        canonical_name="User",
    )

    partner_laura = StoredEntity(
        id="person_laura_partner",
        kind=EntityKind.PERSON,
        canonical_name="Laura",
        aliases={"Lau"},
        attributes={
            "works_at": "Farmacia",
        },
    )

    shop_laura = StoredEntity(
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
            shop_laura,
        ],
        relations=[
            EntityRelation(
                subject_id="person_user",
                predicate="current_romantic_partner",
                object_id="person_laura_partner",
            )
        ],
    )

    return EntityResolver(
        repository,
        user_entity_id="person_user",
    )


@pytest.mark.asyncio
async def test_resolves_user(resolver: EntityResolver):
    result = await resolver.resolve(
        EntityReference(contextual_role="user")
    )

    assert result.entity is not None
    assert result.entity.id == "person_user"


@pytest.mark.asyncio
async def test_same_name_without_context_is_ambiguous(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(name="Laura")
    )

    assert result.entity is None
    assert result.ambiguous is True


@pytest.mark.asyncio
async def test_resolves_partner_by_relationship(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(
            name="Laura",
            contextual_role="current_romantic_partner",
        )
    )

    assert result.entity is not None
    assert result.entity.id == "person_laura_partner"


@pytest.mark.asyncio
async def test_resolves_laura_by_workplace(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(
            name="Laura",
            qualifiers={
                "works_at": "Tiendanimal",
            },
        )
    )

    assert result.entity is not None
    assert result.entity.id == "person_laura_tiendanimal"


@pytest.mark.asyncio
async def test_resolves_partner_alias(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(name="Lau")
    )

    assert result.entity is not None
    assert result.entity.id == "person_laura_partner"


@pytest.mark.asyncio
async def test_wrong_qualifier_does_not_guess(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(
            name="Laura",
            qualifiers={
                "works_at": "Google",
            },
        )
    )

    assert result.entity is None
    assert result.strategy == "qualifier_mismatch"


@pytest.mark.asyncio
async def test_unknown_entity_is_not_invented(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(name="Pepito")
    )

    assert result.entity is None
    assert result.strategy == "unresolved"

@pytest.mark.asyncio
async def test_resolves_explicit_surface_text(
    resolver: EntityResolver,
):
    result = await resolver.resolve(
        EntityReference(
            surface_text="Lau",
        )
    )

    assert result.entity is not None
    assert result.entity.id == "person_laura_partner"