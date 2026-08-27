import pytest

from pydantic import ValidationError

from celeste.cognition.interpretation import (
    Polarity,
    PropositionMode,
    ReferenceStatus,
    SituationKind,
    TransitionKind,
)

from celeste.cognition.interpretation_normalizer import (
    InterpretationNormalizationError,
    normalize_interpretation,
)

from celeste.cognition.raw_interpretation import (
    RawSituation,
    RawSituationKind,
)

from celeste.cognition.raw_interpretation import (
    RawAttribution,
    RawDiscourseMeaning,
    RawEntity,
    RawEvent,
    RawInterpretation,
    RawParticipant,
    RawPolarity,
    RawProposition,
    RawPropositionMode,
    RawReference,
    RawRevision,
    RawSemanticRelation,
    RawState,
    RawTransition,
)


def test_raw_entity_becomes_entity_and_mention():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="p1",
                mention="Laura",
                canonical_name="Laura",
                semantic_type="person",
            )
        ]
    )

    result = normalize_interpretation(raw)

    assert len(result.entities) == 1
    assert len(result.mentions) == 1

    assert (
        result.entities[0].entity_id
        == "entity_p1"
    )

    assert (
        result.mentions[0].entity_id
        == "entity_p1"
    )


def test_raw_event_becomes_semantic_event():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="p1",
                mention="Laura",
                semantic_type="person",
            )
        ],
        situations=[
            RawEvent(
                temp_id="s1",
                semantic_type="come",
                participants=[
                    RawParticipant(
                        entity_temp_id="p1",
                        role="actor",
                    )
                ],
            )
        ],
    )

    result = normalize_interpretation(raw)

    event = result.situations[0]

    assert (
        event.kind
        == SituationKind.EVENT
    )

    assert (
        event.semantic_id
        == "event_s1"
    )

    assert (
        event.participants[0].entity_id
        == "entity_p1"
    )

def test_raw_belief_targets_normalized_state():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="user",
                mention="yo",
                semantic_type="person",
                identity_hint="user",
            ),
            RawEntity(
                temp_id="marta",
                mention="Marta",
                semantic_type="person",
            ),
        ],
        situations=[
            RawState(
                temp_id="anger",
                semantic_type="emotional_state",
                participants=[
                    RawParticipant(
                        entity_temp_id="marta",
                        role="experiencer",
                    )
                ],
                value="angry",
            )
        ],
        propositions=[
            RawProposition(
                temp_id="belief",
                mode=RawPropositionMode.BELIEF,
                holder_entity_temp_id="user",
                target_id="anger",
            )
        ],
    )

    result = normalize_interpretation(raw)

    proposition = result.propositions[0]

    assert proposition.mode == PropositionMode.BELIEF
    assert proposition.holder_entity_id == "entity_user"

    assert result.situations == []

    assert proposition.content.kind == "situation"

    assert (
        proposition.content.situation.semantic_id
        == "state_anger"
    )

    assert (
        proposition.content.situation.semantic_type
        == "emotional_state"
    )

def test_raw_negated_intention_preserves_polarity():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="user",
                mention="yo",
                semantic_type="person",
            )
        ],
        situations=[
            RawTransition(
                temp_id="leave_job",
                semantic_state="employment",
                transition="end",
                participants=[
                    RawParticipant(
                        entity_temp_id="user",
                        role="employee",
                    )
                ],
            )
        ],
        propositions=[
            RawProposition(
                temp_id="intention",
                mode=RawPropositionMode.INTENTION,
                holder_entity_temp_id="user",
                target_id="leave_job",
                polarity=RawPolarity.NEGATIVE,
            )
        ],
    )

    result = normalize_interpretation(raw)

    proposition = result.propositions[0]

    assert proposition.mode == PropositionMode.INTENTION
    assert proposition.polarity == Polarity.NEGATIVE

    assert result.situations == []

    assert proposition.content.kind == "situation"

    assert (
        proposition.content.situation.transition
        == TransitionKind.END
    )

def test_raw_attribution_targets_normalized_node():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="laura",
                mention="Laura",
                semantic_type="person",
            )
        ],
        situations=[
            RawEvent(
                temp_id="rain",
                semantic_type="rain",
            )
        ],
        attributions=[
            RawAttribution(
                temp_id="report",
                source_entity_temp_id="laura",
                relation="reports",
                target_id="rain",
            )
        ],
    )

    result = normalize_interpretation(raw)

    assert (
        result.attributions[0]
        .source_entity_id
        == "entity_laura"
    )

    assert (
        result.attributions[0]
        .target_id
        == "event_rain"
    )


def test_raw_reference_with_two_candidates_becomes_ambiguous():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="laura",
                mention="Laura",
                semantic_type="person",
            ),
            RawEntity(
                temp_id="marta",
                mention="Marta",
                semantic_type="person",
            ),
        ],
        references=[
            RawReference(
                temp_id="ella",
                text="ella",
                candidate_entity_temp_ids=[
                    "laura",
                    "marta",
                ],
            )
        ],
    )

    result = normalize_interpretation(raw)

    assert (
        result.references[0].status
        == ReferenceStatus.AMBIGUOUS
    )


def test_raw_resolved_reference_becomes_resolved():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="laura",
                mention="Laura",
                semantic_type="person",
            ),
            RawEntity(
                temp_id="marta",
                mention="Marta",
                semantic_type="person",
            ),
        ],
        references=[
            RawReference(
                temp_id="ella",
                text="ella",
                candidate_entity_temp_ids=[
                    "laura",
                    "marta",
                ],
                resolved_entity_temp_id="marta",
            )
        ],
    )

    result = normalize_interpretation(raw)

    assert (
        result.references[0].status
        == ReferenceStatus.RESOLVED
    )

    assert (
        result.references[0]
        .resolved_entity_id
        == "entity_marta"
    )


def test_raw_correction_maps_both_semantic_nodes():
    raw = RawInterpretation(
        situations=[
            RawState(
                temp_id="madrid",
                semantic_type="destination",
                value="Madrid",
            ),
            RawState(
                temp_id="getafe",
                semantic_type="destination",
                value="Getafe",
            ),
        ],
        revisions=[
            RawRevision(
                temp_id="correction",
                revision="correction",
                target_id="madrid",
                replacement_id="getafe",
            )
        ],
    )

    result = normalize_interpretation(raw)

    revision = result.revisions[0]

    assert (
        revision.target_id
        == "state_madrid"
    )

    assert (
        revision.replacement_id
        == "state_getafe"
    )


def test_raw_semantic_relation_maps_ids():
    raw = RawInterpretation(
        situations=[
            RawEvent(
                temp_id="rain",
                semantic_type="rain",
            ),
            RawEvent(
                temp_id="stay_home",
                semantic_type="stay_home",
            ),
        ],
        semantic_relations=[
            RawSemanticRelation(
                source_id="rain",
                relation="condition",
                target_id="stay_home",
            )
        ],
    )

    result = normalize_interpretation(raw)

    relation = (
        result.semantic_relations[0]
    )

    assert relation.source_id == "event_rain"

    assert (
        relation.target_id
        == "event_stay_home"
    )


def test_duplicate_raw_semantic_ids_are_rejected():
    with pytest.raises(
        ValidationError,
        match="Duplicate raw temp_id",
    ):
        RawInterpretation(
            situations=[
                RawEvent(
                    temp_id="same",
                    semantic_type="rain",
                ),
                RawState(
                    temp_id="same",
                    semantic_type="weather",
                ),
            ]
        )


def test_raw_temp_id_is_unique_across_reference_and_situation():
    with pytest.raises(
        ValidationError,
        match="Duplicate raw temp_id 'same'",
    ):
        RawInterpretation(
            references=[
                RawReference(
                    temp_id="same",
                    text="ella",
                )
            ],
            situations=[
                RawEvent(
                    temp_id="same",
                    semantic_type="leave",
                )
            ],
        )


def test_raw_temp_id_is_unique_across_situation_and_proposition():
    with pytest.raises(
        ValidationError,
        match="Duplicate raw temp_id 'same'",
    ):
        RawInterpretation(
            entities=[
                RawEntity(
                    temp_id="user",
                    mention="yo",
                    semantic_type="person",
                )
            ],
            situations=[
                RawEvent(
                    temp_id="same",
                    semantic_type="leave",
                )
            ],
            propositions=[
                RawProposition(
                    temp_id="same",
                    mode=RawPropositionMode.DESIRE,
                    holder_entity_temp_id="user",
                    target_id="same",
                )
            ],
        )


def test_raw_temp_id_is_unique_for_revisions_too():
    with pytest.raises(
        ValidationError,
        match="Duplicate raw temp_id 'event1'",
    ):
        RawInterpretation(
            situations=[
                RawEvent(
                    temp_id="event1",
                    semantic_type="leave",
                )
            ],
            revisions=[
                RawRevision(
                    temp_id="event1",
                    revision="retraction",
                    target_id="event1",
                )
            ],
        )

def test_raw_implicit_user_is_created_when_referenced():
    raw = RawInterpretation(
        situations=[
            RawEvent(
                temp_id="leave",
                semantic_type="leave",
                participants=[
                    RawParticipant(
                        entity_temp_id="user",
                        role="actor",
                    )
                ],
            )
        ]
    )

    assert len(raw.entities) == 1

    assert (
        raw.entities[0].temp_id
        == "user"
    )

    assert (
        raw.entities[0].identity_hint
        == "user"
    )

    result = normalize_interpretation(raw)

    assert (
        result.entities[0].entity_id
        == "entity_user"
    )

def test_raw_ambiguous_reference_can_be_situation_participant():
    raw = RawInterpretation(
        entities=[
            RawEntity(
                temp_id="laura",
                mention="Laura",
                semantic_type="person",
            ),
            RawEntity(
                temp_id="marta",
                mention="Marta",
                semantic_type="person",
            ),
        ],
        references=[
            RawReference(
                temp_id="ella",
                text="ella",
                candidate_entity_temp_ids=[
                    "laura",
                    "marta",
                ],
            )
        ],
        situations=[
            RawEvent(
                temp_id="leave",
                semantic_type="leave",
                participants=[
                    RawParticipant(
                        reference_temp_id="ella",
                        role="actor",
                    )
                ],
            )
        ],
    )

    result = normalize_interpretation(raw)

    participant = (
        result.situations[0]
        .participants[0]
    )

    assert participant.entity_id is None

    assert (
        participant.reference_id
        == "reference_ella"
    )

    assert (
        result.references[0].status
        == ReferenceStatus.AMBIGUOUS
    )

def test_raw_participant_reference_field_is_repaired_when_id_is_entity():
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                }
            ],
            "situations": [
                {
                    "temp_id": "talk",
                    "kind": "event",
                    "semantic_type": "talk",
                    "participants": [
                        {
                            "reference_temp_id": "laura",
                            "role": "actor",
                        }
                    ],
                }
            ],
        }
    )

    participant = (
        raw.situations[0]
        .participants[0]
    )

    assert (
        participant.entity_temp_id
        == "laura"
    )

    assert (
        participant.reference_temp_id
        is None
    )

def test_raw_participant_entity_field_is_repaired_when_id_is_reference():
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "ella",
                    "candidate_entity_temp_ids": [
                        "laura",
                        "marta",
                    ],
                }
            ],
            "situations": [
                {
                    "temp_id": "leave",
                    "kind": "event",
                    "semantic_type": "leave",
                    "participants": [
                        {
                            "entity_temp_id": "ref1",
                            "role": "actor",
                        }
                    ],
                }
            ],
        }
    )

    participant = (
        raw.situations[0]
        .participants[0]
    )

    assert (
        participant.reference_temp_id
        == "ref1"
    )

    assert (
        participant.entity_temp_id
        is None
    )

def test_incomplete_raw_transition_is_degraded_to_event():
    raw = RawInterpretation(
        situations=[
            RawSituation(
                temp_id="leave",
                kind=RawSituationKind.TRANSITION,
                semantic_type="leave_job",
            )
        ]
    )

    assert (
        raw.situations[0].kind
        == RawSituationKind.EVENT
    )

    result = normalize_interpretation(raw)

    assert (
        result.situations[0].kind
        == SituationKind.EVENT
    )

    assert (
        result.situations[0].semantic_type
        == "leave_job"
    )
