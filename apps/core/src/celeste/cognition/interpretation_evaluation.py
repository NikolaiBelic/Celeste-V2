from __future__ import annotations

from typing import Any

from celeste.cognition.raw_interpretation import RawInterpretation


def evaluate_graph(
    raw: RawInterpretation,
    expected: dict[str, Any],
) -> list[str]:
    failures: list[str] = []

    def entity_matches_expected(
        entity,
        expected_name: str,
    ) -> bool:
        expected_value = expected_name.casefold()

        values = {
            value.casefold()
            for value in (
                entity.temp_id,
                entity.mention,
                entity.canonical_name,
                entity.identity_hint,
            )
            if value
        }

        return expected_value in values

    def participant_matches(
        participant,
        expected_entity: str,
    ) -> bool:
        if participant.entity_temp_id is None:
            return False

        entity = next(
            (
                item
                for item in raw.entities
                if item.temp_id
                == participant.entity_temp_id
            ),
            None,
        )

        if entity is None:
            return False

        return entity_matches_expected(
            entity,
            expected_entity,
        )

    def participants_match(
        situation,
        expected_participants: dict[str, str],
    ) -> bool:
        for role, expected_entity in expected_participants.items():
            matching_role_participants = [
                participant
                for participant in situation.participants
                if participant.role.casefold()
                == role.casefold()
            ]

            if not matching_role_participants:
                return False

            if not any(
                participant_matches(
                    participant,
                    expected_entity,
                )
                for participant in matching_role_participants
            ):
                return False

        return True

    def situation_matches(
        situation,
        expectation: dict[str, Any] | None,
    ) -> bool:
        if expectation is None:
            return True

        semantic_type = expectation.get(
            "semantic_type"
        )

        if (
            semantic_type is not None
            and (
                situation.semantic_type is None
                or situation.semantic_type.casefold()
                != semantic_type.casefold()
            )
        ):
            return False

        expected_participants = expectation.get(
            "participants",
            {},
        )

        if (
            expected_participants
            and not participants_match(
                situation,
                expected_participants,
            )
        ):
            return False

        return True

    for expected_situation in expected.get(
        "situations",
        [],
    ):
        semantic_type = expected_situation.get(
            "semantic_type"
        )

        candidates = [
            situation
            for situation in raw.situations
            if (
                semantic_type is None
                or (
                    situation.semantic_type is not None
                    and situation.semantic_type.casefold()
                    == semantic_type.casefold()
                )
            )
        ]

        if not candidates:
            failures.append(
                "graph.situations: no situation matches "
                f"semantic_type={semantic_type!r}"
            )
            continue

        expected_participants = expected_situation.get(
            "participants",
            {},
        )

        if (
            expected_participants
            and not any(
                participants_match(
                    situation,
                    expected_participants,
                )
                for situation in candidates
            )
        ):
            failures.append(
                f"graph.situations: situation "
                f"{semantic_type!r} does not contain "
                f"participants "
                f"{expected_participants!r}"
            )

    for expected_proposition in expected.get(
        "propositions",
        [],
    ):
        mode = expected_proposition.get("mode")
        holder = expected_proposition.get("holder")
        target = expected_proposition.get(
            "target_situation",
            {},
        )
        target_semantic_type = target.get(
            "semantic_type"
        )

        matched = False

        for proposition in raw.propositions:
            if (
                mode is not None
                and str(proposition.mode).casefold()
                != mode.casefold()
            ):
                continue

            if holder is not None:
                if (
                    proposition.holder_entity_temp_id
                    is None
                ):
                    continue

                holder_entity = next(
                    (
                        entity
                        for entity in raw.entities
                        if entity.temp_id
                        == proposition.holder_entity_temp_id
                    ),
                    None,
                )

                if (
                    holder_entity is None
                    or not entity_matches_expected(
                        holder_entity,
                        holder,
                    )
                ):
                    continue

            if target_semantic_type is not None:
                target_situation = next(
                    (
                        situation
                        for situation in raw.situations
                        if situation.temp_id
                        == proposition.target_id
                    ),
                    None,
                )

                if (
                    target_situation is None
                    or target_situation.semantic_type
                    is None
                    or target_situation.semantic_type.casefold()
                    != target_semantic_type.casefold()
                ):
                    continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.propositions: no proposition "
                "matches "
                f"mode={mode!r}, holder={holder!r}, "
                "target_situation="
                f"{target_semantic_type!r}"
            )

    for expected_relation in expected.get(
        "semantic_relations",
        [],
    ):
        relation = expected_relation.get("relation")
        source_type = expected_relation.get(
            "source_situation"
        )
        target_type = expected_relation.get(
            "target_situation"
        )

        matched = False

        for semantic_relation in raw.semantic_relations:
            if (
                relation is not None
                and str(
                    semantic_relation.relation
                ).casefold()
                != relation.casefold()
            ):
                continue

            source = next(
                (
                    situation
                    for situation in raw.situations
                    if situation.temp_id
                    == semantic_relation.source_id
                ),
                None,
            )
            target = next(
                (
                    situation
                    for situation in raw.situations
                    if situation.temp_id
                    == semantic_relation.target_id
                ),
                None,
            )

            if (
                source_type is not None
                and (
                    source is None
                    or source.semantic_type is None
                    or source.semantic_type.casefold()
                    != source_type.casefold()
                )
            ):
                continue

            if (
                target_type is not None
                and (
                    target is None
                    or target.semantic_type is None
                    or target.semantic_type.casefold()
                    != target_type.casefold()
                )
            ):
                continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.semantic_relations: no relation "
                "matches "
                f"relation={relation!r}, "
                f"source={source_type!r}, "
                f"target={target_type!r}"
            )

    for expected_attribution in expected.get(
        "attributions",
        [],
    ):
        relation = expected_attribution.get(
            "relation"
        )
        source_entity = expected_attribution.get(
            "source_entity"
        )
        target_situation = expected_attribution.get(
            "target_situation"
        )
        target_proposition = expected_attribution.get(
            "target_proposition"
        )

        matched = False

        for attribution in raw.attributions:
            if (
                relation is not None
                and str(
                    attribution.relation
                ).casefold()
                != relation.casefold()
            ):
                continue

            if source_entity is not None:
                actual_source = next(
                    (
                        entity
                        for entity in raw.entities
                        if entity.temp_id
                        == attribution.source_entity_temp_id
                    ),
                    None,
                )

                if (
                    actual_source is None
                    or not entity_matches_expected(
                        actual_source,
                        source_entity,
                    )
                ):
                    continue

            if target_situation is not None:
                situation = next(
                    (
                        item
                        for item in raw.situations
                        if item.temp_id
                        == attribution.target_id
                    ),
                    None,
                )

                if (
                    situation is None
                    or situation.semantic_type is None
                    or situation.semantic_type.casefold()
                    != target_situation.casefold()
                ):
                    continue

            if target_proposition is not None:
                proposition = next(
                    (
                        item
                        for item in raw.propositions
                        if item.temp_id
                        == attribution.target_id
                    ),
                    None,
                )

                if (
                    proposition is None
                    or str(
                        proposition.mode
                    ).casefold()
                    != target_proposition.casefold()
                ):
                    continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.attributions: no attribution "
                "matches "
                f"relation={relation!r}, "
                f"source_entity={source_entity!r}, "
                f"target_situation={target_situation!r}, "
                "target_proposition="
                f"{target_proposition!r}"
            )

    for expected_revision in expected.get(
        "revisions",
        [],
    ):
        revision_type = expected_revision.get(
            "revision"
        )
        target_situation = expected_revision.get(
            "target_situation"
        )
        replacement_situation = expected_revision.get(
            "replacement_situation"
        )

        matched = False

        for revision in raw.revisions:
            if (
                revision_type is not None
                and str(
                    revision.revision
                ).casefold()
                != revision_type.casefold()
            ):
                continue

            if target_situation is not None:
                target = next(
                    (
                        item
                        for item in raw.situations
                        if item.temp_id
                        == revision.target_id
                    ),
                    None,
                )

                if (
                    target is None
                    or target.semantic_type is None
                    or target.semantic_type.casefold()
                    != target_situation.casefold()
                ):
                    continue

            if replacement_situation is not None:
                if revision.replacement_id is None:
                    continue

                replacement = next(
                    (
                        item
                        for item in raw.situations
                        if item.temp_id
                        == revision.replacement_id
                    ),
                    None,
                )

                if (
                    replacement is None
                    or replacement.semantic_type is None
                    or replacement.semantic_type.casefold()
                    != replacement_situation.casefold()
                ):
                    continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.revisions: no revision matches "
                f"revision={revision_type!r}, "
                "target_situation="
                f"{target_situation!r}, "
                "replacement_situation="
                f"{replacement_situation!r}"
            )

    for expected_reference in expected.get(
        "references",
        [],
    ):
        text = expected_reference.get("text")
        candidates = expected_reference.get(
            "candidates"
        )
        resolved_entity = expected_reference.get(
            "resolved_entity"
        )
        used_in_situation = expected_reference.get(
            "used_in_situation"
        )

        matched = False

        for reference in raw.references:
            if (
                text is not None
                and reference.text.casefold()
                != text.casefold()
            ):
                continue

            if candidates is not None:
                candidate_entities = [
                    entity
                    for entity in raw.entities
                    if entity.temp_id
                    in reference.candidate_entity_temp_ids
                ]

                if (
                    len(candidate_entities)
                    != len(candidates)
                ):
                    continue

                if not all(
                    any(
                        entity_matches_expected(
                            entity,
                            expected_candidate,
                        )
                        for entity
                        in candidate_entities
                    )
                    for expected_candidate
                    in candidates
                ):
                    continue

            if resolved_entity is not None:
                if (
                    reference.resolved_entity_temp_id
                    is None
                ):
                    continue

                resolved = next(
                    (
                        entity
                        for entity in raw.entities
                        if entity.temp_id
                        == reference.resolved_entity_temp_id
                    ),
                    None,
                )

                if (
                    resolved is None
                    or not entity_matches_expected(
                        resolved,
                        resolved_entity,
                    )
                ):
                    continue

            if used_in_situation is not None:
                semantic_type = used_in_situation.get(
                    "semantic_type"
                )
                role = used_in_situation.get("role")

                reference_is_used = False

                for situation in raw.situations:
                    if (
                        semantic_type is not None
                        and (
                            situation.semantic_type
                            is None
                            or situation.semantic_type.casefold()
                            != semantic_type.casefold()
                        )
                    ):
                        continue

                    for participant in (
                        situation.participants
                    ):
                        if (
                            participant.reference_temp_id
                            != reference.temp_id
                        ):
                            continue

                        if (
                            role is not None
                            and participant.role.casefold()
                            != role.casefold()
                        ):
                            continue

                        reference_is_used = True
                        break

                    if reference_is_used:
                        break

                if not reference_is_used:
                    continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.references: no reference matches "
                f"text={text!r}, "
                f"candidates={candidates!r}, "
                "resolved_entity="
                f"{resolved_entity!r}, "
                "used_in_situation="
                f"{used_in_situation!r}"
            )

    for expected_link in expected.get(
        "semantic_content_links",
        [],
    ):
        source_expectation = expected_link.get(
            "source_situation"
        )
        target_expectation = expected_link.get(
            "target_situation"
        )

        matched = False

        for link in raw.semantic_content_links:
            source = next(
                (
                    situation
                    for situation in raw.situations
                    if situation.temp_id
                    == link.source_id
                ),
                None,
            )

            target = next(
                (
                    situation
                    for situation in raw.situations
                    if situation.temp_id
                    == link.target_id
                ),
                None,
            )

            if source is None or target is None:
                continue

            if not situation_matches(
                source,
                source_expectation,
            ):
                continue

            if not situation_matches(
                target,
                target_expectation,
            ):
                continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.semantic_content_links: no "
                "semantic content link matches "
                "source_situation="
                f"{source_expectation!r}, "
                "target_situation="
                f"{target_expectation!r}"
            )

    for expected_scope in expected.get(
        "scope_operators",
        [],
    ):
        operator = expected_scope.get("operator")
        target_situation = expected_scope.get(
            "target_situation"
        )

        matched = False

        for scope in raw.scope_operators:
            if (
                operator is not None
                and str(scope.operator).casefold()
                != operator.casefold()
            ):
                continue

            if target_situation is not None:
                situation = next(
                    (
                        item
                        for item in raw.situations
                        if item.temp_id
                        == scope.target_id
                    ),
                    None,
                )

                if (
                    situation is None
                    or not situation_matches(
                        situation,
                        target_situation,
                    )
                ):
                    continue

            matched = True
            break

        if not matched:
            failures.append(
                "graph.scope_operators: no scope "
                "operator matches "
                f"operator={operator!r}, "
                "target_situation="
                f"{target_situation!r}"
            )

    return failures