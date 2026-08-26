from __future__ import annotations

from celeste.cognition.models import EntityReference


def reference_text(
    reference: EntityReference,
) -> str | None:
    return (
        reference.name
        or reference.surface_text
    )


def references_match(
    left: EntityReference,
    right: EntityReference,
) -> bool:
    if left is right:
        return True

    if (
        left.known_entity_id is not None
        and right.known_entity_id is not None
    ):
        return left.known_entity_id == right.known_entity_id

    left_text = reference_text(left)
    right_text = reference_text(right)

    if left_text is None or right_text is None:
        return False

    if left_text.casefold() != right_text.casefold():
        return False

    if (
        left.contextual_role is not None
        and right.contextual_role is not None
        and left.contextual_role.casefold()
        != right.contextual_role.casefold()
    ):
        return False

    return True