from pydantic import ValidationError
import pytest

from celeste.cognition.interpretation import (
    AlternativeGroup,
    Attribution,
    AttributionType,
    Certainty,
    CommunicativeAct,
    Comparison,
    ComparisonOperator,
    DiscourseMeaning,
    DiscourseReference,
    DiscourseRevision,
    EllipsisResolution,
    Entity,
    EntityMention,
    EntityReferenceValue,
    Event,
    Evidence,
    EvidenceModality,
    EvidenceRelation,
    EvidenceRelationType,
    Interpretation,
    InterpretationAlternative,
    Participant,
    Polarity,
    Proposition,
    PropositionMode,
    PropositionReferenceContent,
    Quantifier,
    QuantifierType,
    RealityStatus,
    ReferenceStatus,
    RelationContent,
    RevisionType,
    ScopeOperator,
    ScopeOperatorType,
    SemanticRelation,
    SemanticRelationType,
    SituationContent,
    SituationKind,
    State,
    TemporalMeaning,
    TimeFrame,
    Transition,
    TransitionKind,
)


def person(
    entity_id: str,
    name: str | None = None,
    *,
    identity_hint: str | None = None,
) -> Entity:
    return Entity(
        entity_id=entity_id,
        canonical_name=name,
        semantic_type="person",
        identity_hint=identity_hint,
    )


def place(entity_id: str, name: str) -> Entity:
    return Entity(
        entity_id=entity_id,
        canonical_name=name,
        semantic_type="place",
    )


def thing(
    entity_id: str,
    *,
    semantic_type: str,
    name: str | None = None,
) -> Entity:
    return Entity(
        entity_id=entity_id,
        canonical_name=name,
        semantic_type=semantic_type,
    )


def ref(entity_id: str) -> EntityReferenceValue:
    return EntityReferenceValue(entity_id=entity_id)


def make_user() -> Entity:
    return person(
        "entity_user",
        identity_hint="user",
    )


# 1
def test_anonymous_entity_can_exist():
    dog = thing(
        "entity_dog",
        semantic_type="animal",
    )
    mention = EntityMention(
        mention_id="mention_dog_1",
        text="un perro",
        entity_id="entity_dog",
    )

    interpretation = Interpretation(
        entities=[dog],
        mentions=[mention],
    )

    assert interpretation.entities[0].canonical_name is None
    assert interpretation.mentions[0].text == "un perro"


# 2
def test_multiple_mentions_can_point_to_same_entity():
    laura = person("entity_laura", "Laura")

    interpretation = Interpretation(
        entities=[laura],
        mentions=[
            EntityMention(
                mention_id="mention_laura_1",
                text="Laura",
                entity_id="entity_laura",
            ),
            EntityMention(
                mention_id="mention_laura_2",
                text="Laura",
                entity_id="entity_laura",
            ),
        ],
    )

    assert len(interpretation.entities) == 1
    assert len(interpretation.mentions) == 2


# 3
def test_unresolved_mention_does_not_create_entity():
    interpretation = Interpretation(
        mentions=[
            EntityMention(
                mention_id="mention_someone_1",
                text="alguien",
                entity_id=None,
            )
        ]
    )

    assert interpretation.entities == []


# 4
def test_mention_cannot_point_to_missing_entity():
    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            mentions=[
                EntityMention(
                    mention_id="mention_laura_1",
                    text="Laura",
                    entity_id="entity_laura",
                )
            ]
        )


# 5
def test_entity_ids_must_be_unique():
    with pytest.raises(ValidationError, match="Duplicate entity_id"):
        Interpretation(
            entities=[
                person("entity_person", "Laura"),
                person("entity_person", "Marta"),
            ]
        )


# 6
def test_mention_ids_must_be_unique():
    laura = person("entity_laura", "Laura")

    with pytest.raises(ValidationError, match="Duplicate mention_id"):
        Interpretation(
            entities=[laura],
            mentions=[
                EntityMention(
                    mention_id="mention_1",
                    text="Laura",
                    entity_id="entity_laura",
                ),
                EntityMention(
                    mention_id="mention_1",
                    text="ella",
                    entity_id="entity_laura",
                ),
            ],
        )


# 7
def test_breakup_can_be_represented_as_transition():
    user = make_user()
    laura = person("entity_laura", "Laura")

    transition = Transition(
        semantic_id="breakup_1",
        transition=TransitionKind.END,
        semantic_state="romantic_relationship",
        participants=[
            Participant(
                entity_id=user.entity_id,
                role="partner",
            ),
            Participant(
                entity_id=laura.entity_id,
                role="partner",
            ),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
            expression="he dejado",
        ),
    )

    interpretation = Interpretation(
        entities=[user, laura],
        situations=[transition],
    )

    assert interpretation.situations[0].kind == SituationKind.TRANSITION
    assert interpretation.situations[0].transition == TransitionKind.END


# 8
def test_participant_must_reference_existing_entity():
    event = Event(
        semantic_id="event_1",
        semantic_type="visit",
        participants=[
            Participant(
                entity_id="missing_person",
                role="visitor",
            )
        ],
    )

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(situations=[event])


# 9
def test_intention_can_contain_transition_without_completing_it():
    user = make_user()
    laura = person("entity_laura", "Laura")

    possible_breakup = Transition(
        semantic_id="possible_breakup_1",
        transition=TransitionKind.END,
        semantic_state="romantic_relationship",
        participants=[
            Participant(entity_id=user.entity_id, role="partner"),
            Participant(entity_id=laura.entity_id, role="partner"),
        ],
        temporal=TemporalMeaning(frame=TimeFrame.FUTURE),
    )

    proposition = Proposition(
        semantic_id="intention_1",
        mode=PropositionMode.INTENTION,
        holder_entity_id=user.entity_id,
        content=SituationContent(
            situation=possible_breakup,
        ),
    )

    interpretation = Interpretation(
        entities=[user, laura],
        propositions=[proposition],
    )

    assert interpretation.situations == []
    assert interpretation.propositions[0].mode == PropositionMode.INTENTION


# 10
def test_argument_can_be_event_without_relationship_change():
    user = make_user()
    mother = person("entity_mother")

    event = Event(
        semantic_id="argument_1",
        semantic_type="interpersonal_conflict",
        participants=[
            Participant(entity_id=user.entity_id, role="participant"),
            Participant(entity_id=mother.entity_id, role="participant"),
        ],
    )

    interpretation = Interpretation(
        entities=[user, mother],
        situations=[event],
    )

    assert len(interpretation.situations) == 1


# 11
def test_hypothesis_does_not_become_external_fact():
    user = make_user()
    marta = person("entity_marta", "Marta")

    anger = State(
        semantic_id="anger_1",
        semantic_type="emotional_state",
        participants=[
            Participant(entity_id=marta.entity_id, role="experiencer"),
            Participant(entity_id=user.entity_id, role="target"),
        ],
        value="angry",
        certainty=Certainty.UNCERTAIN,
    )

    proposition = Proposition(
        semantic_id="hypothesis_1",
        mode=PropositionMode.HYPOTHESIS,
        holder_entity_id=user.entity_id,
        content=SituationContent(situation=anger),
        certainty=Certainty.UNCERTAIN,
    )

    interpretation = Interpretation(
        entities=[user, marta],
        propositions=[proposition],
    )

    assert interpretation.situations == []


# 12
def test_holder_must_reference_existing_entity():
    proposition = Proposition(
        semantic_id="belief_1",
        mode=PropositionMode.BELIEF,
        holder_entity_id="missing_user",
        content=RelationContent(
            subject_entity_id="missing_user",
            predicate="likes",
            object=True,
        ),
    )

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(propositions=[proposition])


# 13
def test_negation_is_separate_from_certainty():
    user = make_user()
    coffee = thing(
        "entity_coffee",
        semantic_type="thing",
        name="café",
    )

    preference = Proposition(
        semantic_id="preference_1",
        mode=PropositionMode.PREFERENCE,
        holder_entity_id=user.entity_id,
        content=RelationContent(
            subject_entity_id=user.entity_id,
            predicate="likes",
            object=ref(coffee.entity_id),
            polarity=Polarity.NEGATIVE,
        ),
        certainty=Certainty.ASSERTED,
    )

    interpretation = Interpretation(
        entities=[user, coffee],
        propositions=[preference],
    )

    assert interpretation.propositions[0].certainty == Certainty.ASSERTED
    assert (
        interpretation.propositions[0].content.polarity
        == Polarity.NEGATIVE
    )


# 14
def test_semantic_value_entity_reference_must_exist():
    user = make_user()

    state = State(
        semantic_id="residence_1",
        semantic_type="residence",
        participants=[
            Participant(entity_id=user.entity_id, role="resident"),
        ],
        value=ref("missing_place"),
    )

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            entities=[user],
            situations=[state],
        )


# 15
def test_desire_does_not_create_real_world_state():
    user = make_user()
    dog = thing("entity_dog", semantic_type="animal")

    desired_state = State(
        semantic_id="ownership_1",
        semantic_type="ownership",
        participants=[
            Participant(entity_id=user.entity_id, role="owner"),
            Participant(entity_id=dog.entity_id, role="owned"),
        ],
    )

    desire = Proposition(
        semantic_id="desire_1",
        mode=PropositionMode.DESIRE,
        holder_entity_id=user.entity_id,
        content=SituationContent(situation=desired_state),
    )

    interpretation = Interpretation(
        entities=[user, dog],
        propositions=[desire],
    )

    assert interpretation.situations == []


# 16
def test_real_move_can_preserve_previous_and_new_state():
    laura = person("entity_laura", "Laura")
    madrid = place("entity_madrid", "Madrid")
    getafe = place("entity_getafe", "Getafe")

    move = Transition(
        semantic_id="move_1",
        transition=TransitionKind.CHANGE,
        semantic_state="residence",
        participants=[
            Participant(entity_id=laura.entity_id, role="resident"),
        ],
        previous_value=ref(madrid.entity_id),
        new_value=ref(getafe.entity_id),
    )

    interpretation = Interpretation(
        entities=[laura, madrid, getafe],
        situations=[move],
    )

    assert move.previous_value.entity_id == "entity_madrid"
    assert move.new_value.entity_id == "entity_getafe"


# 17
def test_reconciliation_can_resume_previous_state():
    user = make_user()
    laura = person("entity_laura", "Laura")

    reconciliation = Transition(
        semantic_id="reconciliation_1",
        transition=TransitionKind.RESUME,
        semantic_state="romantic_relationship",
        participants=[
            Participant(entity_id=user.entity_id, role="partner"),
            Participant(entity_id=laura.entity_id, role="partner"),
        ],
    )

    Interpretation(
        entities=[user, laura],
        situations=[reconciliation],
    )

    assert reconciliation.transition == TransitionKind.RESUME


# 18
def test_possibility_about_future_event_is_not_external_event():
    user = make_user()
    laura = person("entity_laura", "Laura")

    visit = Event(
        semantic_id="visit_1",
        semantic_type="visit",
        participants=[
            Participant(entity_id=laura.entity_id, role="visitor"),
        ],
        temporal=TemporalMeaning(frame=TimeFrame.FUTURE),
        certainty=Certainty.UNCERTAIN,
    )

    possibility = Proposition(
        semantic_id="possibility_1",
        mode=PropositionMode.POSSIBILITY,
        holder_entity_id=user.entity_id,
        content=SituationContent(situation=visit),
        certainty=Certainty.UNCERTAIN,
    )

    interpretation = Interpretation(
        entities=[user, laura],
        propositions=[possibility],
    )

    assert interpretation.situations == []


# 19
def test_question_is_distinct_from_assertion():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[CommunicativeAct.ASK],
            literal_meaning="Laura viene mañana",
        )
    )

    assert CommunicativeAct.ASK in interpretation.discourse.acts
    assert CommunicativeAct.ASSERT not in interpretation.discourse.acts


# 20
def test_request_is_distinct_from_assertion():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[CommunicativeAct.REQUEST],
        )
    )

    assert interpretation.discourse.acts == [CommunicativeAct.REQUEST]


# 21
def test_ambiguous_social_statement_can_keep_alternative():
    interpretation = Interpretation(
        alternatives=[
            InterpretationAlternative(
                description="The user may have romantic interest in Marta.",
                confidence=0.30,
            )
        ]
    )

    assert len(interpretation.alternatives) == 1


# 22
def test_alternative_interpretation_is_not_external_fact():
    interpretation = Interpretation(
        alternatives=[
            InterpretationAlternative(
                description="Marta may be a romantic interest.",
                confidence=0.25,
            )
        ]
    )

    assert interpretation.propositions == []
    assert interpretation.situations == []


# 23
def test_literal_and_intended_meaning_can_differ():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[CommunicativeAct.EXPRESS],
            literal_meaning="Estoy muerto de sueño.",
            intended_meaning="Estoy muy cansado.",
            intended_meaning_confidence=0.98,
        )
    )

    assert (
        interpretation.discourse.literal_meaning
        != interpretation.discourse.intended_meaning
    )


# 24
def test_meanings_can_be_connected_by_reason():
    user = make_user()
    mother = person("entity_mother")

    argument = Event(
        semantic_id="argument_1",
        semantic_type="interpersonal_conflict",
        participants=[
            Participant(entity_id=user.entity_id, role="participant"),
            Participant(entity_id=mother.entity_id, role="participant"),
        ],
    )

    desire = Proposition(
        semantic_id="mother_desire_1",
        mode=PropositionMode.DESIRE,
        holder_entity_id=mother.entity_id,
        content=RelationContent(
            subject_entity_id=user.entity_id,
            predicate="leave_job",
            object=True,
        ),
    )

    relation = SemanticRelation(
        source_id="argument_1",
        relation=SemanticRelationType.REASON,
        target_id="mother_desire_1",
    )

    interpretation = Interpretation(
        entities=[user, mother],
        situations=[argument],
        propositions=[desire],
        semantic_relations=[relation],
    )

    assert interpretation.semantic_relations[0].relation == SemanticRelationType.REASON


# 25
def test_negated_intention_is_not_completed_transition():
    user = make_user()

    leave_job = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(entity_id=user.entity_id, role="employee"),
        ],
    )

    intention = Proposition(
        semantic_id="user_intention_1",
        mode=PropositionMode.INTENTION,
        holder_entity_id=user.entity_id,
        content=SituationContent(situation=leave_job),
        polarity=Polarity.NEGATIVE,
    )

    interpretation = Interpretation(
        entities=[user],
        propositions=[intention],
    )

    assert interpretation.situations == []
    assert interpretation.propositions[0].polarity == Polarity.NEGATIVE


# 26
def test_contrast_can_connect_two_mental_attitudes():
    user = make_user()
    mother = person("entity_mother")

    change = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(entity_id=user.entity_id, role="employee"),
        ],
    )

    mother_desire = Proposition(
        semantic_id="mother_desire_1",
        mode=PropositionMode.DESIRE,
        holder_entity_id=mother.entity_id,
        content=SituationContent(situation=change),
    )

    user_intention = Proposition(
        semantic_id="user_intention_1",
        mode=PropositionMode.INTENTION,
        holder_entity_id=user.entity_id,
        content=PropositionReferenceContent(
            target_id="leave_job_1",
        ),
        polarity=Polarity.NEGATIVE,
    )

    contrast = SemanticRelation(
        source_id="mother_desire_1",
        relation=SemanticRelationType.CONTRAST,
        target_id="user_intention_1",
    )

    interpretation = Interpretation(
        entities=[user, mother],
        propositions=[mother_desire, user_intention],
        semantic_relations=[contrast],
    )

    assert interpretation.semantic_relations[0].relation == SemanticRelationType.CONTRAST


# 27
def test_condition_can_connect_possible_meanings():
    user = make_user()

    rain = Event(
        semantic_id="rain_1",
        semantic_type="rain",
        certainty=Certainty.UNCERTAIN,
    )

    not_going = Event(
        semantic_id="not_go_1",
        semantic_type="go",
        participants=[
            Participant(entity_id=user.entity_id, role="traveler"),
        ],
        polarity=Polarity.NEGATIVE,
        certainty=Certainty.UNCERTAIN,
    )

    condition = SemanticRelation(
        source_id="rain_1",
        relation=SemanticRelationType.CONDITION,
        target_id="not_go_1",
    )

    interpretation = Interpretation(
        entities=[user],
        situations=[rain, not_going],
        semantic_relations=[condition],
    )

    assert interpretation.semantic_relations[0].relation == SemanticRelationType.CONDITION


# 28
def test_semantic_relation_cannot_reference_missing_node():
    with pytest.raises(ValidationError, match="unknown semantic_id"):
        Interpretation(
            semantic_relations=[
                SemanticRelation(
                    source_id="ghost_1",
                    relation=SemanticRelationType.CAUSE,
                    target_id="ghost_2",
                )
            ]
        )


# 29
def test_top_level_semantic_node_ids_must_be_unique():
    with pytest.raises(ValidationError, match="duplicate semantic_id"):
        Interpretation(
            situations=[
                Event(
                    semantic_id="same_1",
                    semantic_type="rain",
                ),
                State(
                    semantic_id="same_1",
                    semantic_type="weather",
                ),
            ]
        )


# 30
def test_reported_information_is_attributed_to_source():
    father = person("entity_father", "Fernando")

    rain = Event(
        semantic_id="rain_1",
        semantic_type="rain",
    )

    attribution = Attribution(
        semantic_id="father_report_1",
        source_entity_id=father.entity_id,
        relation=AttributionType.ASSERTS,
        target_id="rain_1",
    )

    interpretation = Interpretation(
        entities=[father],
        situations=[rain],
        attributions=[attribution],
    )

    assert interpretation.attributions[0].source_entity_id == father.entity_id


# 31
def test_attribution_source_must_exist():
    rain = Event(
        semantic_id="rain_1",
        semantic_type="rain",
    )

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            situations=[rain],
            attributions=[
                Attribution(
                    semantic_id="report_1",
                    source_entity_id="missing_person",
                    relation=AttributionType.REPORTS,
                    target_id="rain_1",
                )
            ],
        )


# 32
def test_reported_claim_does_not_become_speakers_own_belief():
    marta = person("entity_marta", "Marta")
    laura = person("entity_laura", "Laura")
    user = make_user()

    anger = State(
        semantic_id="user_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value="angry",
    )

    belief = Proposition(
        semantic_id="marta_belief_1",
        mode=PropositionMode.BELIEF,
        holder_entity_id=marta.entity_id,
        content=SituationContent(situation=anger),
    )

    interpretation = Interpretation(
        entities=[user, marta, laura],
        propositions=[belief],
        attributions=[
            Attribution(
                semantic_id="laura_report_1",
                source_entity_id=laura.entity_id,
                relation=AttributionType.REPORTS,
                target_id="marta_belief_1",
            )
        ],
    )

    assert interpretation.propositions[0].holder_entity_id == "entity_marta"


# 33
def test_negation_can_apply_to_reporting_act():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")

    angry = State(
        semantic_id="marta_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(entity_id=marta.entity_id, role="experiencer"),
        ],
    )

    report = Attribution(
        semantic_id="laura_report_1",
        source_entity_id=laura.entity_id,
        relation=AttributionType.REPORTS,
        target_id="marta_angry_1",
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        situations=[angry],
        attributions=[report],
        scope_operators=[
            ScopeOperator(
                operator_id="negation_1",
                operator=ScopeOperatorType.NEGATION,
                target_id="laura_report_1",
            )
        ],
    )

    assert interpretation.scope_operators[0].target_id == "laura_report_1"


# 34
def test_negation_inside_reported_content_has_different_scope():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")

    angry = State(
        semantic_id="marta_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(entity_id=marta.entity_id, role="experiencer"),
        ],
    )

    report = Attribution(
        semantic_id="laura_report_1",
        source_entity_id=laura.entity_id,
        relation=AttributionType.REPORTS,
        target_id="marta_angry_1",
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        situations=[angry],
        attributions=[report],
        scope_operators=[
            ScopeOperator(
                operator_id="negation_1",
                operator=ScopeOperatorType.NEGATION,
                target_id="marta_angry_1",
            )
        ],
    )

    assert interpretation.scope_operators[0].target_id == "marta_angry_1"


# 35
def test_double_negation_preserves_scopes():
    user = make_user()
    laura = person("entity_laura", "Laura")

    come = Event(
        semantic_id="laura_comes_1",
        semantic_type="come",
        participants=[
            Participant(entity_id=laura.entity_id, role="actor"),
        ],
    )

    belief = Proposition(
        semantic_id="belief_1",
        mode=PropositionMode.BELIEF,
        holder_entity_id=user.entity_id,
        content=PropositionReferenceContent(
            target_id="laura_comes_1",
        ),
    )

    interpretation = Interpretation(
        entities=[user, laura],
        situations=[come],
        propositions=[belief],
        scope_operators=[
            ScopeOperator(
                operator_id="inner_negation",
                operator=ScopeOperatorType.NEGATION,
                target_id="laura_comes_1",
            ),
            ScopeOperator(
                operator_id="outer_negation",
                operator=ScopeOperatorType.NEGATION,
                target_id="belief_1",
            ),
        ],
    )

    assert {
        item.target_id
        for item in interpretation.scope_operators
    } == {"laura_comes_1", "belief_1"}


# 36
def test_nested_mental_attitudes_preserve_holders():
    user = make_user()
    marta = person("entity_marta", "Marta")
    fernando = person("entity_fernando", "Fernando")

    leaving = Event(
        semantic_id="user_leaving_1",
        semantic_type="leave",
        participants=[
            Participant(entity_id=user.entity_id, role="actor"),
        ],
    )

    fernando_knows = Proposition(
        semantic_id="fernando_knows_1",
        mode=PropositionMode.KNOWLEDGE,
        holder_entity_id=fernando.entity_id,
        content=PropositionReferenceContent(
            target_id="user_leaving_1",
        ),
    )

    marta_believes = Proposition(
        semantic_id="marta_believes_1",
        mode=PropositionMode.BELIEF,
        holder_entity_id=marta.entity_id,
        content=PropositionReferenceContent(
            target_id="fernando_knows_1",
        ),
    )

    interpretation = Interpretation(
        entities=[user, marta, fernando],
        situations=[leaving],
        propositions=[fernando_knows, marta_believes],
    )

    assert interpretation.propositions[0].holder_entity_id == "entity_fernando"
    assert interpretation.propositions[1].holder_entity_id == "entity_marta"


# 37
def test_audio_can_be_preserved_as_interpretive_evidence():
    user = make_user()

    interpretation = Interpretation(
        entities=[user],
        evidence=[
            Evidence(
                evidence_id="audio_1",
                modality=EvidenceModality.AUDIO,
                signal_type="prosody",
                value="low_energy_voice",
                source_entity_id=user.entity_id,
            )
        ],
    )

    assert interpretation.evidence[0].modality == EvidenceModality.AUDIO


# 38
def test_audio_signal_does_not_automatically_become_emotional_fact():
    user = make_user()

    interpretation = Interpretation(
        entities=[user],
        evidence=[
            Evidence(
                evidence_id="audio_1",
                modality=EvidenceModality.AUDIO,
                signal_type="prosody",
                value="possible_distress",
                source_entity_id=user.entity_id,
            )
        ],
        alternatives=[
            InterpretationAlternative(
                description="The speaker may be experiencing distress.",
                confidence=0.65,
                evidence=["audio_1"],
            )
        ],
    )

    assert interpretation.situations == []


# 39
def test_evidence_source_must_exist():
    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            evidence=[
                Evidence(
                    evidence_id="audio_1",
                    modality=EvidenceModality.AUDIO,
                    signal_type="prosody",
                    value="low_energy_voice",
                    source_entity_id="missing_user",
                )
            ]
        )


# 40
def test_evidence_can_qualify_semantic_content():
    user = make_user()

    state = State(
        semantic_id="okay_1",
        semantic_type="wellbeing",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value="okay",
    )

    interpretation = Interpretation(
        entities=[user],
        situations=[state],
        evidence=[
            Evidence(
                evidence_id="audio_1",
                modality=EvidenceModality.AUDIO,
                signal_type="prosody",
                value="possible_distress",
                source_entity_id=user.entity_id,
            )
        ],
        evidence_relations=[
            EvidenceRelation(
                evidence_id="audio_1",
                relation=EvidenceRelationType.QUALIFIES,
                target_id="okay_1",
            )
        ],
    )

    assert interpretation.evidence_relations[0].target_id == "okay_1"


# 41
def test_evidence_relation_requires_existing_evidence():
    user = make_user()
    state = State(
        semantic_id="okay_1",
        semantic_type="wellbeing",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
    )

    with pytest.raises(ValidationError, match="unknown evidence_id"):
        Interpretation(
            entities=[user],
            situations=[state],
            evidence_relations=[
                EvidenceRelation(
                    evidence_id="missing_audio",
                    relation=EvidenceRelationType.QUALIFIES,
                    target_id="okay_1",
                )
            ],
        )


# 42
def test_explicit_or_preserves_alternative_group():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")

    laura_comes = Event(
        semantic_id="laura_comes_1",
        semantic_type="come",
        participants=[
            Participant(entity_id=laura.entity_id, role="actor"),
        ],
    )

    marta_comes = Event(
        semantic_id="marta_comes_1",
        semantic_type="come",
        participants=[
            Participant(entity_id=marta.entity_id, role="actor"),
        ],
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        situations=[laura_comes, marta_comes],
        alternative_groups=[
            AlternativeGroup(
                semantic_id="alternatives_1",
                member_ids=[
                    "laura_comes_1",
                    "marta_comes_1",
                ],
                exclusive=None,
            )
        ],
    )

    assert interpretation.alternative_groups[0].exclusive is None


# 43
def test_alternative_group_members_must_exist():
    event = Event(
        semantic_id="event_1",
        semantic_type="visit",
    )

    with pytest.raises(ValidationError, match="unknown semantic_id"):
        Interpretation(
            situations=[event],
            alternative_groups=[
                AlternativeGroup(
                    semantic_id="alternatives_1",
                    member_ids=[
                        "event_1",
                        "missing_event",
                    ],
                )
            ],
        )


# 44
def test_nobody_can_be_represented_without_inventing_person():
    arrival = Event(
        semantic_id="arrival_1",
        semantic_type="come",
    )

    interpretation = Interpretation(
        situations=[arrival],
        quantifiers=[
            Quantifier(
                operator_id="none_1",
                quantifier=QuantifierType.NONE,
                target_id="arrival_1",
                role="actor",
                domain="people",
            )
        ],
    )

    assert interpretation.entities == []


# 45
def test_all_except_one_preserves_exception_entity_reference():
    fernando = person("entity_fernando", "Fernando")

    agreement = State(
        semantic_id="agreement_1",
        semantic_type="agreement",
        value=True,
    )

    interpretation = Interpretation(
        entities=[fernando],
        situations=[agreement],
        quantifiers=[
            Quantifier(
                operator_id="all_except_1",
                quantifier=QuantifierType.ALL,
                target_id="agreement_1",
                role="participant",
                domain="contextually_relevant_people",
                exception_entity_ids=[
                    fernando.entity_id,
                ],
            )
        ],
    )

    assert (
        interpretation.quantifiers[0].exception_entity_ids
        == ["entity_fernando"]
    )


# 46
def test_quantifier_exception_entity_must_exist():
    state = State(
        semantic_id="agreement_1",
        semantic_type="agreement",
    )

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            situations=[state],
            quantifiers=[
                Quantifier(
                    operator_id="all_except_1",
                    quantifier=QuantifierType.ALL,
                    target_id="agreement_1",
                    exception_entity_ids=["missing_person"],
                )
            ],
        )


# 47
def test_comparison_keeps_dimension_and_degree_separate():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")

    comparison = Comparison(
        semantic_id="height_comparison_1",
        left=ref(laura.entity_id),
        dimension="height",
        operator=ComparisonOperator.GREATER_THAN,
        right=ref(marta.entity_id),
        degree="considerably",
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        comparisons=[comparison],
    )

    assert interpretation.comparisons[0].dimension == "height"
    assert interpretation.comparisons[0].degree == "considerably"


# 48
def test_comparison_entity_reference_must_exist():
    laura = person("entity_laura", "Laura")

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            entities=[laura],
            comparisons=[
                Comparison(
                    semantic_id="comparison_1",
                    left=ref(laura.entity_id),
                    dimension="height",
                    operator=ComparisonOperator.GREATER_THAN,
                    right=ref("missing_marta"),
                )
            ],
        )


# 49
def test_stopping_state_can_presuppose_previous_state():
    user = make_user()

    previous = State(
        semantic_id="previous_smoking_1",
        semantic_type="smoking",
        participants=[
            Participant(entity_id=user.entity_id, role="actor"),
        ],
        value=True,
        certainty=Certainty.INFERRED,
    )

    stopped = Transition(
        semantic_id="stop_smoking_1",
        transition=TransitionKind.END,
        semantic_state="smoking",
        participants=[
            Participant(entity_id=user.entity_id, role="actor"),
        ],
    )

    interpretation = Interpretation(
        entities=[user],
        situations=[previous, stopped],
        semantic_relations=[
            SemanticRelation(
                source_id="stop_smoking_1",
                relation=SemanticRelationType.PRESUPPOSES,
                target_id="previous_smoking_1",
            )
        ],
    )

    assert previous.certainty == Certainty.INFERRED


# 50
def test_factive_emotion_can_presuppose_event():
    user = make_user()

    going = Event(
        semantic_id="went_1",
        semantic_type="go",
        participants=[
            Participant(entity_id=user.entity_id, role="actor"),
        ],
        certainty=Certainty.INFERRED,
    )

    regret = State(
        semantic_id="regret_1",
        semantic_type="regret",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value=True,
    )

    interpretation = Interpretation(
        entities=[user],
        situations=[going, regret],
        semantic_relations=[
            SemanticRelation(
                source_id="regret_1",
                relation=SemanticRelationType.PRESUPPOSES,
                target_id="went_1",
            )
        ],
    )

    assert interpretation.semantic_relations[0].target_id == "went_1"


# 51
def test_counterfactual_does_not_become_actual_world_fact():
    user = make_user()
    job = thing("entity_job", semantic_type="job")
    madrid = place("entity_madrid", "Madrid")

    accepted_job = Event(
        semantic_id="accept_job_1",
        semantic_type="accept_job",
        participants=[
            Participant(entity_id=user.entity_id, role="actor"),
            Participant(entity_id=job.entity_id, role="object"),
        ],
        reality=RealityStatus.COUNTERFACTUAL,
    )

    live_madrid = State(
        semantic_id="live_madrid_1",
        semantic_type="residence",
        participants=[
            Participant(entity_id=user.entity_id, role="resident"),
        ],
        value=ref(madrid.entity_id),
        reality=RealityStatus.COUNTERFACTUAL,
    )

    interpretation = Interpretation(
        entities=[user, job, madrid],
        situations=[accepted_job, live_madrid],
        semantic_relations=[
            SemanticRelation(
                source_id="accept_job_1",
                relation=SemanticRelationType.CONDITION,
                target_id="live_madrid_1",
            )
        ],
    )

    assert all(
        situation.reality == RealityStatus.COUNTERFACTUAL
        for situation in interpretation.situations
    )


# 52
def test_figurative_expression_does_not_create_literal_death():
    user = make_user()

    fatigue = State(
        semantic_id="fatigue_1",
        semantic_type="fatigue",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value="very_tired",
    )

    interpretation = Interpretation(
        entities=[user],
        discourse=DiscourseMeaning(
            acts=[CommunicativeAct.EXPRESS],
            literal_meaning="Estoy muerto de sueño.",
            intended_meaning="Estoy muy cansado.",
            intended_meaning_confidence=0.98,
        ),
        situations=[fatigue],
    )

    assert all(
        situation.semantic_type != "death"
        for situation in interpretation.situations
    )


# 53
def test_same_turn_correction_can_replace_previous_content():
    user = make_user()
    madrid = place("entity_madrid", "Madrid")
    getafe = place("entity_getafe", "Getafe")

    first = State(
        semantic_id="destination_madrid_1",
        semantic_type="destination",
        participants=[
            Participant(entity_id=user.entity_id, role="traveler"),
        ],
        value=ref(madrid.entity_id),
    )

    corrected = State(
        semantic_id="destination_getafe_1",
        semantic_type="destination",
        participants=[
            Participant(entity_id=user.entity_id, role="traveler"),
        ],
        value=ref(getafe.entity_id),
    )

    interpretation = Interpretation(
        entities=[user, madrid, getafe],
        situations=[first, corrected],
        revisions=[
            DiscourseRevision(
                revision_id="correction_1",
                revision=RevisionType.CORRECTION,
                target_id="destination_madrid_1",
                replacement_id="destination_getafe_1",
            )
        ],
    )

    assert interpretation.revisions[0].replacement_id == "destination_getafe_1"


# 54
def test_same_turn_intention_can_be_retracted():
    user = make_user()

    leave_job = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(entity_id=user.entity_id, role="employee"),
        ],
    )

    intention = Proposition(
        semantic_id="leave_job_intention_1",
        mode=PropositionMode.INTENTION,
        holder_entity_id=user.entity_id,
        content=SituationContent(situation=leave_job),
    )

    interpretation = Interpretation(
        entities=[user],
        propositions=[intention],
        revisions=[
            DiscourseRevision(
                revision_id="retraction_1",
                revision=RevisionType.RETRACTION,
                target_id="leave_job_intention_1",
            )
        ],
    )

    assert interpretation.revisions[0].revision == RevisionType.RETRACTION


# 55
def test_reformulation_can_preserve_same_underlying_domain():
    user = make_user()

    tired = State(
        semantic_id="tired_1",
        semantic_type="fatigue",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value="tired",
    )

    exhausted = State(
        semantic_id="exhausted_1",
        semantic_type="fatigue",
        participants=[
            Participant(entity_id=user.entity_id, role="experiencer"),
        ],
        value="very_tired",
    )

    interpretation = Interpretation(
        entities=[user],
        situations=[tired, exhausted],
        revisions=[
            DiscourseRevision(
                revision_id="reformulation_1",
                revision=RevisionType.REFORMULATION,
                target_id="tired_1",
                replacement_id="exhausted_1",
            )
        ],
    )

    assert interpretation.revisions[0].revision == RevisionType.REFORMULATION


# 56
def test_internal_contradiction_can_be_preserved():
    laura = person("entity_laura", "Laura")

    positive = State(
        semantic_id="laura_home_positive_1",
        semantic_type="location",
        participants=[
            Participant(entity_id=laura.entity_id, role="located_entity"),
        ],
        value="home",
    )

    negative = State(
        semantic_id="laura_home_negative_1",
        semantic_type="location",
        participants=[
            Participant(entity_id=laura.entity_id, role="located_entity"),
        ],
        value="home",
        polarity=Polarity.NEGATIVE,
    )

    interpretation = Interpretation(
        entities=[laura],
        situations=[positive, negative],
        semantic_relations=[
            SemanticRelation(
                source_id="laura_home_positive_1",
                relation=SemanticRelationType.CONTRADICTS,
                target_id="laura_home_negative_1",
            )
        ],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.CONTRADICTS
    )


# 57
def test_ellipsis_can_inherit_previous_event_structure():
    fernando = person("entity_fernando", "Fernando")
    marta = person("entity_marta", "Marta")
    bar = place("entity_bar", "bar")

    fernando_goes = Event(
        semantic_id="fernando_goes_1",
        semantic_type="go",
        participants=[
            Participant(entity_id=fernando.entity_id, role="traveler"),
            Participant(entity_id=bar.entity_id, role="destination"),
        ],
    )

    marta_goes = Event(
        semantic_id="marta_goes_1",
        semantic_type="go",
        participants=[
            Participant(entity_id=marta.entity_id, role="traveler"),
            Participant(entity_id=bar.entity_id, role="destination"),
        ],
    )

    interpretation = Interpretation(
        entities=[fernando, marta, bar],
        situations=[fernando_goes, marta_goes],
        ellipsis_resolutions=[
            EllipsisResolution(
                ellipsis_id="ellipsis_1",
                text="también",
                antecedent_ids=["fernando_goes_1"],
                resolved_semantic_id="marta_goes_1",
                status=ReferenceStatus.RESOLVED,
            )
        ],
    )

    assert (
        interpretation.ellipsis_resolutions[0].resolved_semantic_id
        == "marta_goes_1"
    )


# 58
def test_ellipsis_can_remain_unresolved():
    interpretation = Interpretation(
        ellipsis_resolutions=[
            EllipsisResolution(
                ellipsis_id="ellipsis_1",
                text="también",
                status=ReferenceStatus.UNRESOLVED,
            )
        ]
    )

    assert (
        interpretation.ellipsis_resolutions[0].resolved_semantic_id
        is None
    )


# 59
def test_revision_cannot_reference_missing_semantic_node():
    with pytest.raises(ValidationError, match="unknown semantic_id"):
        Interpretation(
            revisions=[
                DiscourseRevision(
                    revision_id="bad_revision_1",
                    revision=RevisionType.CORRECTION,
                    target_id="missing_content",
                )
            ]
        )


# 60
def test_resolved_reference_points_to_candidate_entity():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")

    interpretation = Interpretation(
        entities=[laura, marta],
        references=[
            DiscourseReference(
                reference_id="reference_ella_1",
                text="ella",
                candidate_entity_ids=[
                    laura.entity_id,
                    marta.entity_id,
                ],
                resolved_entity_id=marta.entity_id,
                status=ReferenceStatus.RESOLVED,
            )
        ],
    )

    assert interpretation.references[0].resolved_entity_id == marta.entity_id


# 61
def test_resolved_reference_requires_resolved_entity():
    laura = person("entity_laura", "Laura")

    with pytest.raises(ValidationError, match="requires resolved_entity_id"):
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[laura.entity_id],
                    status=ReferenceStatus.RESOLVED,
                )
            ],
        )


# 62
def test_resolved_reference_must_choose_candidate():
    laura = person("entity_laura", "Laura")
    marta = person("entity_marta", "Marta")
    fernando = person("entity_fernando", "Fernando")

    with pytest.raises(
        ValidationError,
        match="must resolve to one of its candidates",
    ):
        Interpretation(
            entities=[laura, marta, fernando],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        laura.entity_id,
                        marta.entity_id,
                    ],
                    resolved_entity_id=fernando.entity_id,
                    status=ReferenceStatus.RESOLVED,
                )
            ],
        )


# 63
def test_ambiguous_reference_requires_multiple_candidates():
    laura = person("entity_laura", "Laura")

    with pytest.raises(
        ValidationError,
        match="requires at least two candidates",
    ):
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[laura.entity_id],
                    status=ReferenceStatus.AMBIGUOUS,
                )
            ],
        )


# 64
def test_reference_candidates_must_exist():
    laura = person("entity_laura", "Laura")

    with pytest.raises(ValidationError, match="unknown entity_id"):
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        laura.entity_id,
                        "missing_marta",
                    ],
                    status=ReferenceStatus.AMBIGUOUS,
                )
            ],
        )


# 65
def test_pronoun_mention_and_reference_can_share_resolved_entity():
    laura = person("entity_laura", "Laura")

    interpretation = Interpretation(
        entities=[laura],
        mentions=[
            EntityMention(
                mention_id="mention_laura_1",
                text="Laura",
                entity_id=laura.entity_id,
            ),
            EntityMention(
                mention_id="mention_ella_1",
                text="ella",
                entity_id=laura.entity_id,
            ),
        ],
        references=[
            DiscourseReference(
                reference_id="reference_ella_1",
                text="ella",
                candidate_entity_ids=[laura.entity_id],
                resolved_entity_id=laura.entity_id,
                status=ReferenceStatus.RESOLVED,
            )
        ],
    )

    assert interpretation.mentions[1].entity_id == laura.entity_id
