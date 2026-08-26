from celeste.cognition.models import EntityReference
from celeste.cognition.reference_matching import references_match


def test_name_and_surface_text_match():
    left = EntityReference(
        name="Alicante"
    )

    right = EntityReference(
        surface_text="Alicante"
    )

    assert references_match(
        left,
        right,
    )


def test_matching_is_case_insensitive():
    left = EntityReference(
        name="ALICANTE"
    )

    right = EntityReference(
        surface_text="alicante"
    )

    assert references_match(
        left,
        right,
    )


def test_different_entities_do_not_match():
    left = EntityReference(
        name="Alicante"
    )

    right = EntityReference(
        name="Madrid"
    )

    assert not references_match(
        left,
        right,
    )