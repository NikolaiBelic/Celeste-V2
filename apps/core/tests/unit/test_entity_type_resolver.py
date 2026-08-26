from celeste.cognition.entity_type_resolver import (
    EntityTypeResolver,
)
from celeste.cognition.models import (
    Claim,
    EntityClaimObject,
    EntityMention,
    EntityReference,
    EntityType,
    TurnUnderstanding,
)


def test_preserves_known_type_hint():
    alicante = EntityReference(
        name="Alicante"
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Alicante",
                type_hint=EntityType.PLACE,
                reference=alicante,
                confidence=0.95,
            )
        ]
    )

    resolver = EntityTypeResolver()

    results = resolver.resolve(
        understanding
    )

    assert len(results) == 1
    assert results[0].entity_type == EntityType.PLACE
    assert results[0].reason == "explicit_type_hint"


def test_infers_place_from_lives_in():
    mention_reference = EntityReference(
        name="Alicante"
    )

    claim_reference = EntityReference(
        surface_text="Alicante"
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Alicante",
                type_hint=EntityType.UNKNOWN,
                reference=mention_reference,
            )
        ],
        claims=[
            Claim(
                subject=EntityReference(
                    surface_text="Laura"
                ),
                predicate="lives_in",
                object=EntityClaimObject(
                    entity=claim_reference
                ),
                confidence=0.95,
            )
        ],
    )

    resolver = EntityTypeResolver()

    results = resolver.resolve(
        understanding
    )

    assert len(results) == 1
    assert results[0].entity_type == EntityType.PLACE
    assert results[0].reason == "object_of_lives_in"


def test_infers_organization_from_works_at():
    mention_reference = EntityReference(
        name="Tiendanimal"
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Tiendanimal",
                type_hint=EntityType.UNKNOWN,
                reference=mention_reference,
            )
        ],
        claims=[
            Claim(
                subject=EntityReference(
                    surface_text="Laura"
                ),
                predicate="works_at",
                object=EntityClaimObject(
                    entity=EntityReference(
                        surface_text="Tiendanimal"
                    )
                ),
                confidence=0.95,
            )
        ],
    )

    resolver = EntityTypeResolver()

    results = resolver.resolve(
        understanding
    )

    assert results[0].entity_type == EntityType.ORGANIZATION
    assert results[0].reason == "object_of_works_at"


def test_unknown_stays_unknown_without_evidence():
    reference = EntityReference(
        name="Cronos"
    )

    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="Cronos",
                type_hint=EntityType.UNKNOWN,
                reference=reference,
            )
        ]
    )

    resolver = EntityTypeResolver()

    results = resolver.resolve(
        understanding
    )

    assert results[0].entity_type == EntityType.UNKNOWN
    assert (
        results[0].reason
        == "insufficient_semantic_evidence"
    )


def test_entity_matching_is_case_insensitive():
    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="alicante",
                type_hint=EntityType.UNKNOWN,
                reference=EntityReference(
                    name="alicante"
                ),
            )
        ],
        claims=[
            Claim(
                subject=EntityReference(
                    surface_text="Laura"
                ),
                predicate="lives_in",
                object=EntityClaimObject(
                    entity=EntityReference(
                        surface_text="Alicante"
                    )
                ),
            )
        ],
    )

    resolver = EntityTypeResolver()

    results = resolver.resolve(
        understanding
    )

    assert results[0].entity_type == EntityType.PLACE