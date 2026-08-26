from celeste.cognition.interpretation import (
    Certainty,
    CommunicativeAct,
    DiscourseMeaning,
    EntityMention,
    Event,
    Interpretation,
    InterpretationAlternative,
    Participant,
    Polarity,
    Proposition,
    PropositionMode,
    RelationContent,
    SemanticRelation,
    SemanticRelationType,
    SituationContent,
    SituationKind,
    State,
    TemporalMeaning,
    TimeFrame,
    Transition,
    TransitionKind,
    Attribution,
    AttributionType,
    Evidence,
    EvidenceModality,
    EvidenceRelation,
    EvidenceRelationType,
    PropositionReferenceContent,
    ScopeOperator,
    ScopeOperatorType,
    AlternativeGroup,
    Comparison,
    ComparisonOperator,
    Quantifier,
    QuantifierType,
    RealityStatus,
    DiscourseReference,
    ReferenceStatus,
    DiscourseRevision,
    EllipsisResolution,
    RevisionType,
)

from pydantic import ValidationError


def make_user() -> EntityMention:
    return EntityMention(
        semantic_id="entity_user",
        text="yo",
        identity_hint="user",
        semantic_type="person",
    )

def test_anonymous_entity_can_exist():
    dog = EntityMention(
        semantic_id="entity_dog",
        text="un perro",
        semantic_type="animal",
    )

    assert dog.text == "un perro"
    assert dog.canonical_name is None
    assert dog.identity_hint is None


def test_breakup_can_be_represented_as_transition():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    transition = Transition(
        semantic_id="breakup_1",
        transition=TransitionKind.END,
        semantic_state="romantic_relationship",
        participants=[
            Participant(
                entity=user,
                role="partner",
            ),
            Participant(
                entity=laura,
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

    situation = interpretation.situations[0]

    assert situation.kind == SituationKind.TRANSITION
    assert situation.transition == TransitionKind.END
    assert (
        situation.semantic_state
        == "romantic_relationship"
    )


def test_intention_can_contain_transition_without_completing_it():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    possible_breakup = Transition(
        semantic_id="possible_breakup_1",
        transition=TransitionKind.END,
        semantic_state="romantic_relationship",
        participants=[
            Participant(
                entity=user,
                role="partner",
            ),
            Participant(
                entity=laura,
                role="partner",
            ),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
        ),
    )

    proposition = Proposition(
        semantic_id="intention_1",
        mode=PropositionMode.INTENTION,
        holder=user,
        content=SituationContent(
            situation=possible_breakup,
        ),
    )

    interpretation = Interpretation(
        entities=[user, laura],
        propositions=[proposition],
    )

    assert interpretation.situations == []

    assert (
        interpretation.propositions[0].mode
        == PropositionMode.INTENTION
    )

    assert (
        interpretation
        .propositions[0]
        .content
        .situation
        .transition
        == TransitionKind.END
    )


def test_argument_can_be_event_without_relationship_change():
    user = make_user()

    mother = EntityMention(
        semantic_id="entity_mother",
        text="mi madre",
        semantic_type="person",
        qualifiers={
            "relation_to_user": "mother",
        },
    )

    event = Event(
        semantic_id="argument_1",
        semantic_type="interpersonal_conflict",
        participants=[
            Participant(
                entity=user,
                role="participant",
            ),
            Participant(
                entity=mother,
                role="participant",
            ),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
    )

    interpretation = Interpretation(
        entities=[user, mother],
        situations=[event],
    )

    assert len(interpretation.situations) == 1

    assert (
        interpretation.situations[0].kind
        == SituationKind.EVENT
    )


def test_hypothesis_does_not_become_external_fact():
    user = make_user()

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    anger = State(
        semantic_id="anger_1",
        semantic_type="emotional_state",
        participants=[
            Participant(
                entity=marta,
                role="experiencer",
            ),
            Participant(
                entity=user,
                role="target",
            ),
        ],
        value="angry",
        certainty=Certainty.UNCERTAIN,
    )

    proposition = Proposition(
        semantic_id="hypothesis_1",
        mode=PropositionMode.HYPOTHESIS,
        holder=user,
        content=SituationContent(
            situation=anger,
        ),
        certainty=Certainty.UNCERTAIN,
    )

    interpretation = Interpretation(
        entities=[user, marta],
        propositions=[proposition],
    )

    assert interpretation.situations == []

    assert (
        interpretation.propositions[0].mode
        == PropositionMode.HYPOTHESIS
    )


def test_negation_is_separate_from_certainty():
    user = make_user()

    coffee = EntityMention(
        semantic_id="entity_coffee",
        text="el café",
        semantic_type="thing",
    )

    preference = RelationContent(
        subject=user,
        predicate="likes",
        object=coffee,
        polarity=Polarity.NEGATIVE,
    )

    proposition = Proposition(
        semantic_id="preference_1",
        mode=PropositionMode.PREFERENCE,
        holder=user,
        content=preference,
        certainty=Certainty.ASSERTED,
    )

    assert proposition.certainty == Certainty.ASSERTED

    assert (
        proposition.content.polarity
        == Polarity.NEGATIVE
    )


def test_desire_does_not_create_real_world_state():
    user = make_user()

    dog = EntityMention(
        semantic_id="entity_dog",
        text="un perro",
        semantic_type="animal",
    )

    desired_state = State(
        semantic_id="ownership_1",
        semantic_type="ownership",
        participants=[
            Participant(
                entity=user,
                role="owner",
            ),
            Participant(
                entity=dog,
                role="owned",
            ),
        ],
    )

    proposition = Proposition(
        semantic_id="desire_1",
        mode=PropositionMode.DESIRE,
        holder=user,
        content=SituationContent(
            situation=desired_state,
        ),
    )

    interpretation = Interpretation(
        entities=[user, dog],
        propositions=[proposition],
    )

    assert interpretation.situations == []


def test_real_move_can_preserve_previous_and_new_state():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    madrid = EntityMention(
        semantic_id="entity_madrid",
        text="Madrid",
        canonical_name="Madrid",
        semantic_type="place",
    )

    getafe = EntityMention(
        semantic_id="entity_getafe",
        text="Getafe",
        canonical_name="Getafe",
        semantic_type="place",
    )

    move = Transition(
        semantic_id="move_1",
        transition=TransitionKind.CHANGE,
        semantic_state="residence",
        participants=[
            Participant(
                entity=laura,
                role="resident",
            ),
        ],
        previous_value=madrid,
        new_value=getafe,
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
    )

    assert move.previous_value == madrid
    assert move.new_value == getafe


def test_reconciliation_can_resume_previous_state():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    reconciliation = Transition(
        semantic_id="reconciliation_1",
        transition=TransitionKind.RESUME,
        semantic_state="romantic_relationship",
        participants=[
            Participant(
                entity=user,
                role="partner",
            ),
            Participant(
                entity=laura,
                role="partner",
            ),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PRESENT,
            expression="hemos vuelto",
        ),
    )

    assert (
        reconciliation.transition
        == TransitionKind.RESUME
    )


def test_possibility_about_future_event_is_not_event():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    visit = Event(
        semantic_id="visit_1",
        semantic_type="visit",
        participants=[
            Participant(
                entity=laura,
                role="visitor",
            ),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
            expression="mañana",
        ),
        certainty=Certainty.UNCERTAIN,
    )

    possibility = Proposition(
        semantic_id="possibility_1",
        mode=PropositionMode.POSSIBILITY,
        holder=user,
        content=SituationContent(
            situation=visit,
        ),
        certainty=Certainty.UNCERTAIN,
    )

    interpretation = Interpretation(
        entities=[user, laura],
        propositions=[possibility],
    )

    assert interpretation.situations == []


def test_question_is_distinct_from_assertion():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[
                CommunicativeAct.ASK,
            ],
            literal_meaning="Laura viene mañana",
        )
    )

    assert (
        CommunicativeAct.ASK
        in interpretation.discourse.acts
    )

    assert (
        CommunicativeAct.ASSERT
        not in interpretation.discourse.acts
    )


def test_request_is_distinct_from_assertion():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[
                CommunicativeAct.REQUEST,
            ],
            intended_meaning=(
                "Notify the user if Laura comes tomorrow."
            ),
        )
    )

    assert (
        interpretation.discourse.acts
        == [CommunicativeAct.REQUEST]
    )


def test_ambiguous_social_statement_can_keep_alternative():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[
                CommunicativeAct.ASSERT,
            ]
        ),
        alternatives=[
            InterpretationAlternative(
                description=(
                    "The user may have romantic interest "
                    "in Marta."
                ),
                confidence=0.30,
                evidence=[
                    "The user reports seeing Marta frequently."
                ],
            )
        ],
    )

    assert len(interpretation.alternatives) == 1

    assert (
        interpretation.alternatives[0].confidence
        == 0.30
    )


def test_alternative_interpretation_is_not_external_fact():
    alternative = InterpretationAlternative(
        description=(
            "Marta may be a romantic interest."
        ),
        confidence=0.25,
    )

    interpretation = Interpretation(
        alternatives=[alternative]
    )

    assert interpretation.propositions == []
    assert interpretation.situations == []


def test_literal_and_intended_meaning_can_differ():
    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[
                CommunicativeAct.EXPRESS,
            ],
            literal_meaning=(
                "I love waking up at six in the morning."
            ),
            intended_meaning=(
                "The speaker dislikes waking up "
                "at six in the morning."
            ),
            intended_meaning_confidence=0.70,
        )
    )

    assert (
        interpretation.discourse.literal_meaning
        != interpretation.discourse.intended_meaning
    )


def test_meanings_can_be_connected_by_cause():
    user = make_user()

    mother = EntityMention(
        semantic_id="entity_mother",
        text="mi madre",
        semantic_type="person",
    )

    argument = Event(
        semantic_id="argument_1",
        semantic_type="interpersonal_conflict",
        participants=[
            Participant(entity=user, role="participant"),
            Participant(entity=mother, role="participant"),
        ],
    )

    reason = Proposition(
        semantic_id="mother_desire_1",
        mode=PropositionMode.DESIRE,
        holder=mother,
        content=RelationContent(
            subject=user,
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
        situations=[argument],
        propositions=[reason],
        semantic_relations=[relation],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.REASON
    )


def test_negated_intention_is_not_completed_transition():
    user = make_user()

    leave_job = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(
                entity=user,
                role="employee",
            )
        ],
    )

    intention = Proposition(
        semantic_id="user_intention_1",
        mode=PropositionMode.INTENTION,
        holder=user,
        content=SituationContent(
            situation=leave_job,
        ),
        polarity=Polarity.NEGATIVE,
    )

    interpretation = Interpretation(
        propositions=[intention]
    )

    assert interpretation.situations == []

    assert (
        interpretation.propositions[0].polarity
        == Polarity.NEGATIVE
    )


def test_contrast_can_connect_two_mental_attitudes():
    user = make_user()

    mother = EntityMention(
        semantic_id="entity_mother",
        text="mi madre",
        semantic_type="person",
    )

    desired_change = Transition(
        semantic_id="desired_leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(
                entity=user,
                role="employee",
            )
        ],
    )

    mother_desire = Proposition(
        semantic_id="mother_desire_1",
        mode=PropositionMode.DESIRE,
        holder=mother,
        content=SituationContent(
            situation=desired_change,
        ),
    )

    user_intention = Proposition(
        semantic_id="user_intention_1",
        mode=PropositionMode.INTENTION,
        holder=user,
        content=SituationContent(
            situation=desired_change,
        ),
        polarity=Polarity.NEGATIVE,
    )

    contrast = SemanticRelation(
        source_id="mother_desire_1",
        relation=SemanticRelationType.CONTRAST,
        target_id="user_intention_1",
    )

    interpretation = Interpretation(
        propositions=[
            mother_desire,
            user_intention,
        ],
        semantic_relations=[contrast],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.CONTRAST
    )


def test_condition_can_connect_possible_meanings():
    user = make_user()

    rain = Event(
        semantic_id="rain_1",
        semantic_type="rain",
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
            expression="mañana",
        ),
        certainty=Certainty.UNCERTAIN,
    )

    not_going = Event(
        semantic_id="not_go_1",
        semantic_type="go",
        participants=[
            Participant(
                entity=user,
                role="traveler",
            )
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
        ),
        polarity=Polarity.NEGATIVE,
        certainty=Certainty.UNCERTAIN,
    )

    condition = SemanticRelation(
        source_id="rain_1",
        relation=SemanticRelationType.CONDITION,
        target_id="not_go_1",
    )

    interpretation = Interpretation(
    situations=[
        rain,
        not_going,
    ],
    semantic_relations=[condition],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.CONDITION
    )


def test_single_turn_can_contain_multiple_semantic_layers():
    user = make_user()

    mother = EntityMention(
        semantic_id="entity_mother",
        text="mi madre",
        semantic_type="person",
    )

    argument = Event(
        semantic_id="argument_1",
        semantic_type="interpersonal_conflict",
        participants=[
            Participant(entity=user, role="participant"),
            Participant(entity=mother, role="participant"),
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
    )

    leave_job = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(
                entity=user,
                role="employee",
            )
        ],
    )

    mother_desire = Proposition(
        semantic_id="mother_desire_1",
        mode=PropositionMode.DESIRE,
        holder=mother,
        content=SituationContent(
            situation=leave_job,
        ),
    )

    user_intention = Proposition(
        semantic_id="user_intention_1",
        mode=PropositionMode.INTENTION,
        holder=user,
        content=SituationContent(
            situation=leave_job,
        ),
        polarity=Polarity.NEGATIVE,
    )

    interpretation = Interpretation(
        entities=[user, mother],
        situations=[argument],
        propositions=[
            mother_desire,
            user_intention,
        ],
        semantic_relations=[
            SemanticRelation(
                source_id="argument_1",
                relation=SemanticRelationType.REASON,
                target_id="mother_desire_1",
            ),
            SemanticRelation(
                source_id="mother_desire_1",
                relation=SemanticRelationType.CONTRAST,
                target_id="user_intention_1",
            ),
        ],
    )

    assert len(interpretation.situations) == 1
    assert len(interpretation.propositions) == 2
    assert len(interpretation.semantic_relations) == 2

def test_reported_information_is_attributed_to_its_source():
    user = make_user()

    father = EntityMention(
        semantic_id="entity_father",
        text="mi padre",
        canonical_name="Fernando",
        semantic_type="person",
    )

    rain = Event(
        semantic_id="rain_1",
        semantic_type="rain",
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
            expression="mañana",
        ),
    )

    interpretation = Interpretation(
        entities=[user, father],
        situations=[rain],
        attributions=[
            Attribution(
                semantic_id="father_assertion_1",
                source=father,
                relation=AttributionType.ASSERTS,
                target_id="rain_1",
            )
        ],
    )

    assert (
        interpretation.attributions[0].source.canonical_name
        == "Fernando"
    )

    assert (
        interpretation.attributions[0].relation
        == AttributionType.ASSERTS
    )


def test_reported_claim_does_not_become_speakers_own_belief():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    anger = State(
        semantic_id="user_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="angry",
    )

    marta_belief = Proposition(
        semantic_id="marta_belief_1",
        mode=PropositionMode.BELIEF,
        holder=marta,
        content=SituationContent(
            situation=anger,
        ),
    )

    interpretation = Interpretation(
        propositions=[marta_belief],
        attributions=[
            Attribution(
                semantic_id="laura_report_1",
                source=laura,
                relation=AttributionType.REPORTS,
                target_id="marta_belief_1",
            )
        ],
    )

    assert (
        interpretation.propositions[0].holder
        == marta
    )

    assert (
        interpretation.attributions[0].source
        == laura
    )


def test_audio_can_be_preserved_as_interpretive_evidence():
    speaker = make_user()

    audio = Evidence(
        evidence_id="audio_1",
        modality=EvidenceModality.AUDIO,
        signal_type="prosody",
        value="low_energy_voice",
        source=speaker,
        confidence=0.82,
    )

    interpretation = Interpretation(
        evidence=[audio]
    )

    assert (
        interpretation.evidence[0].modality
        == EvidenceModality.AUDIO
    )


def test_audio_signal_does_not_automatically_become_emotional_fact():
    user = make_user()

    audio = Evidence(
        evidence_id="audio_1",
        modality=EvidenceModality.AUDIO,
        signal_type="prosody",
        value="possible_distress",
        source=user,
        confidence=0.65,
    )

    interpretation = Interpretation(
        evidence=[audio],
        alternatives=[
            InterpretationAlternative(
                description=(
                    "The speaker may be experiencing distress."
                ),
                confidence=0.65,
                evidence=["audio_1"],
            )
        ],
    )

    assert interpretation.situations == []
    assert interpretation.propositions == []
    assert len(interpretation.alternatives) == 1


def test_evidence_can_qualify_semantic_content():
    user = make_user()

    okay_state = State(
        semantic_id="okay_1",
        semantic_type="wellbeing",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="okay",
    )

    audio = Evidence(
        evidence_id="audio_1",
        modality=EvidenceModality.AUDIO,
        signal_type="prosody",
        value="possible_distress",
        source=user,
        confidence=0.70,
    )

    relation = EvidenceRelation(
        evidence_id="audio_1",
        relation=EvidenceRelationType.QUALIFIES,
        target_id="okay_1",
        confidence=0.70,
    )

    interpretation = Interpretation(
        situations=[okay_state],
        evidence=[audio],
        evidence_relations=[relation],
    )

    assert (
        interpretation.evidence_relations[0].relation
        == EvidenceRelationType.QUALIFIES
    )


def test_different_modalities_can_contribute_to_same_interpretation():
    user = make_user()

    interpretation = Interpretation(
        evidence=[
            Evidence(
                evidence_id="text_1",
                modality=EvidenceModality.TEXT,
                signal_type="utterance",
                value="Estoy bien",
                source=user,
            ),
            Evidence(
                evidence_id="audio_1",
                modality=EvidenceModality.AUDIO,
                signal_type="prosody",
                value="low_energy_voice",
                source=user,
                confidence=0.75,
            ),
        ],
    )

    modalities = {
        evidence.modality
        for evidence in interpretation.evidence
    }

    assert EvidenceModality.TEXT in modalities
    assert EvidenceModality.AUDIO in modalities

def test_negation_can_apply_to_reporting_act():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    angry = State(
        semantic_id="marta_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(
                entity=marta,
                role="experiencer",
            )
        ],
        value="angry",
    )

    report = Attribution(
        semantic_id="laura_report_1",
        source=laura,
        relation=AttributionType.REPORTS,
        target_id="marta_angry_1",
    )

    negation = ScopeOperator(
        operator_id="negation_1",
        operator=ScopeOperatorType.NEGATION,
        target_id="laura_report_1",
    )

    interpretation = Interpretation(
        situations=[angry],
        attributions=[report],
        scope_operators=[negation],
    )

    assert (
        interpretation.scope_operators[0].target_id
        == "laura_report_1"
    )

def test_negation_inside_reported_content_has_different_scope():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    angry = State(
        semantic_id="marta_angry_1",
        semantic_type="emotional_state",
        participants=[
            Participant(
                entity=marta,
                role="experiencer",
            )
        ],
        value="angry",
    )

    report = Attribution(
        semantic_id="laura_report_1",
        source=laura,
        relation=AttributionType.REPORTS,
        target_id="marta_angry_1",
    )

    negation = ScopeOperator(
        operator_id="negation_1",
        operator=ScopeOperatorType.NEGATION,
        target_id="marta_angry_1",
    )

    interpretation = Interpretation(
        situations=[angry],
        attributions=[report],
        scope_operators=[negation],
    )

    assert (
        interpretation.scope_operators[0].target_id
        == "marta_angry_1"
    )

    assert (
        interpretation.scope_operators[0].target_id
        != interpretation.attributions[0].semantic_id
    )

def test_double_negation_preserves_its_scopes():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    come = Event(
        semantic_id="laura_comes_1",
        semantic_type="come",
        participants=[
            Participant(
                entity=laura,
                role="actor",
            )
        ],
    )

    belief = Proposition(
        semantic_id="belief_1",
        mode=PropositionMode.BELIEF,
        holder=user,
        content=PropositionReferenceContent(
            target_id="laura_comes_1",
        ),
    )

    inner_negation = ScopeOperator(
        operator_id="inner_negation",
        operator=ScopeOperatorType.NEGATION,
        target_id="laura_comes_1",
    )

    outer_negation = ScopeOperator(
        operator_id="outer_negation",
        operator=ScopeOperatorType.NEGATION,
        target_id="belief_1",
    )

    interpretation = Interpretation(
        situations=[come],
        propositions=[belief],
        scope_operators=[
            inner_negation,
            outer_negation,
        ],
    )

    targets = {
        operator.target_id
        for operator in interpretation.scope_operators
    }

    assert targets == {
        "laura_comes_1",
        "belief_1",
    }

def test_nested_mental_attitudes_preserve_each_holder():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    fernando = EntityMention(
        semantic_id="entity_fernando",
        text="Fernando",
        canonical_name="Fernando",
        semantic_type="person",
    )

    leaving = Event(
        semantic_id="user_leaving_1",
        semantic_type="leave",
        participants=[
            Participant(
                entity=user,
                role="actor",
            )
        ],
    )

    fernando_knows = Proposition(
        semantic_id="fernando_knows_1",
        mode=PropositionMode.KNOWLEDGE,
        holder=fernando,
        content=PropositionReferenceContent(
            target_id="user_leaving_1",
        ),
    )

    marta_believes = Proposition(
        semantic_id="marta_believes_1",
        mode=PropositionMode.BELIEF,
        holder=marta,
        content=PropositionReferenceContent(
            target_id="fernando_knows_1",
        ),
    )

    laura_reports = Attribution(
        semantic_id="laura_reports_1",
        source=laura,
        relation=AttributionType.REPORTS,
        target_id="marta_believes_1",
    )

    interpretation = Interpretation(
        situations=[leaving],
        propositions=[
            fernando_knows,
            marta_believes,
        ],
        attributions=[laura_reports],
    )

    assert (
        interpretation.propositions[0].holder
        == fernando
    )

    assert (
        interpretation.propositions[1].holder
        == marta
    )

    assert (
        interpretation.attributions[0].source
        == laura
    )

def test_exclusivity_can_apply_to_specific_attribution():
    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    leaving = Event(
        semantic_id="laura_left_1",
        semantic_type="leave",
        participants=[
            Participant(
                entity=laura,
                role="actor",
            )
        ],
    )

    report = Attribution(
        semantic_id="marta_report_1",
        source=marta,
        relation=AttributionType.REPORTS,
        target_id="laura_left_1",
    )

    exclusivity = ScopeOperator(
        operator_id="only_1",
        operator=ScopeOperatorType.EXCLUSIVITY,
        target_id="marta_report_1",
    )

    interpretation = Interpretation(
        situations=[leaving],
        attributions=[report],
        scope_operators=[exclusivity],
    )

    assert (
        interpretation.scope_operators[0].operator
        == ScopeOperatorType.EXCLUSIVITY
    )

def test_current_information_can_correct_previous_belief():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    madrid = EntityMention(
        semantic_id="entity_madrid",
        text="Madrid",
        canonical_name="Madrid",
        semantic_type="place",
    )

    getafe = EntityMention(
        semantic_id="entity_getafe",
        text="Getafe",
        canonical_name="Getafe",
        semantic_type="place",
    )

    believed_residence = State(
        semantic_id="believed_residence_1",
        semantic_type="residence",
        participants=[
            Participant(
                entity=laura,
                role="resident",
            )
        ],
        value=madrid,
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
    )

    old_belief = Proposition(
        semantic_id="old_belief_1",
        mode=PropositionMode.BELIEF,
        holder=user,
        content=SituationContent(
            situation=believed_residence,
        ),
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
    )

    current_residence = State(
        semantic_id="current_residence_1",
        semantic_type="residence",
        participants=[
            Participant(
                entity=laura,
                role="resident",
            )
        ],
        value=getafe,
        temporal=TemporalMeaning(
            frame=TimeFrame.PRESENT,
        ),
    )

    correction = SemanticRelation(
        source_id="current_residence_1",
        relation=SemanticRelationType.CORRECTS,
        target_id="old_belief_1",
    )

    interpretation = Interpretation(
        entities=[
            user,
            laura,
            madrid,
            getafe,
        ],
        propositions=[old_belief],
        situations=[current_residence],
        semantic_relations=[correction],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.CORRECTS
    )

def test_explicit_or_is_not_interpreted_as_both_events():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    laura_comes = Event(
        semantic_id="laura_comes_1",
        semantic_type="come",
        participants=[
            Participant(
                entity=laura,
                role="actor",
            )
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
            expression="mañana",
        ),
        certainty=Certainty.UNCERTAIN,
    )

    marta_comes = Event(
        semantic_id="marta_comes_1",
        semantic_type="come",
        participants=[
            Participant(
                entity=marta,
                role="actor",
            )
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.FUTURE,
            expression="mañana",
        ),
        certainty=Certainty.UNCERTAIN,
    )

    alternatives = AlternativeGroup(
        semantic_id="visitor_alternatives_1",
        member_ids=[
            "laura_comes_1",
            "marta_comes_1",
        ],
        exclusive=None,
    )

    interpretation = Interpretation(
        situations=[
            laura_comes,
            marta_comes,
        ],
        alternative_groups=[alternatives],
    )

    assert (
        interpretation.alternative_groups[0].member_ids
        == ["laura_comes_1", "marta_comes_1"]
    )

    assert (
        interpretation.alternative_groups[0].exclusive
        is None
    )


def test_nobody_can_be_represented_without_inventing_a_person():
    arrival = Event(
        semantic_id="arrival_1",
        semantic_type="come",
    )

    nobody = Quantifier(
        operator_id="none_1",
        quantifier=QuantifierType.NONE,
        target_id="arrival_1",
        role="actor",
        domain="people",
    )

    interpretation = Interpretation(
        situations=[arrival],
        quantifiers=[nobody],
    )

    assert interpretation.entities == []

    assert (
        interpretation.quantifiers[0].quantifier
        == QuantifierType.NONE
    )


def test_all_except_one_preserves_exception():
    fernando = EntityMention(
        semantic_id="entity_fernando",
        text="Fernando",
        canonical_name="Fernando",
        semantic_type="person",
    )

    agreement = State(
        semantic_id="agreement_1",
        semantic_type="agreement",
        value=True,
    )

    everyone_except_fernando = Quantifier(
        operator_id="all_except_1",
        quantifier=QuantifierType.ALL,
        target_id="agreement_1",
        role="participant",
        domain="contextually_relevant_people",
        exceptions=[fernando],
    )

    interpretation = Interpretation(
        entities=[fernando],
        situations=[agreement],
        quantifiers=[everyone_except_fernando],
    )

    assert (
        interpretation.quantifiers[0].exceptions[0]
        == fernando
    )


def test_comparison_keeps_dimension_and_degree_separate():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    comparison = Comparison(
        semantic_id="height_comparison_1",
        left=laura,
        dimension="height",
        operator=ComparisonOperator.GREATER_THAN,
        right=marta,
        degree="considerably",
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        comparisons=[comparison],
    )

    assert (
        interpretation.comparisons[0].dimension
        == "height"
    )

    assert (
        interpretation.comparisons[0].operator
        == ComparisonOperator.GREATER_THAN
    )

    assert (
        interpretation.comparisons[0].degree
        == "considerably"
    )


def test_stopping_a_state_can_presuppose_previous_state():
    user = make_user()

    previous_smoking = State(
        semantic_id="previous_smoking_1",
        semantic_type="smoking",
        participants=[
            Participant(
                entity=user,
                role="actor",
            )
        ],
        value=True,
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
        certainty=Certainty.INFERRED,
    )

    stopped_smoking = Transition(
        semantic_id="stop_smoking_1",
        transition=TransitionKind.END,
        semantic_state="smoking",
        participants=[
            Participant(
                entity=user,
                role="actor",
            )
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
            expression="he dejado de fumar",
        ),
    )

    presupposition = SemanticRelation(
        source_id="stop_smoking_1",
        relation=SemanticRelationType.PRESUPPOSES,
        target_id="previous_smoking_1",
    )

    interpretation = Interpretation(
        situations=[
            previous_smoking,
            stopped_smoking,
        ],
        semantic_relations=[presupposition],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.PRESUPPOSES
    )

    assert (
        previous_smoking.certainty
        == Certainty.INFERRED
    )


def test_factive_emotion_can_presuppose_event_occurred():
    user = make_user()

    going = Event(
        semantic_id="went_1",
        semantic_type="go",
        participants=[
            Participant(
                entity=user,
                role="actor",
            )
        ],
        temporal=TemporalMeaning(
            frame=TimeFrame.PAST,
        ),
        certainty=Certainty.INFERRED,
    )

    regret = State(
        semantic_id="regret_1",
        semantic_type="regret",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value=True,
    )

    presupposition = SemanticRelation(
        source_id="regret_1",
        relation=SemanticRelationType.PRESUPPOSES,
        target_id="went_1",
    )

    interpretation = Interpretation(
        situations=[
            going,
            regret,
        ],
        semantic_relations=[presupposition],
    )

    assert going.certainty == Certainty.INFERRED

    assert (
        interpretation.semantic_relations[0].target_id
        == "went_1"
    )


def test_counterfactual_does_not_become_actual_world_fact():
    user = make_user()

    job = EntityMention(
        semantic_id="entity_job",
        text="el trabajo",
        semantic_type="job",
    )

    madrid = EntityMention(
        semantic_id="entity_madrid",
        text="Madrid",
        canonical_name="Madrid",
        semantic_type="place",
    )

    accepted_job = Event(
        semantic_id="accept_job_1",
        semantic_type="accept_job",
        participants=[
            Participant(
                entity=user,
                role="actor",
            ),
            Participant(
                entity=job,
                role="object",
            ),
        ],
        reality=RealityStatus.COUNTERFACTUAL,
    )

    live_madrid = State(
        semantic_id="live_madrid_1",
        semantic_type="residence",
        participants=[
            Participant(
                entity=user,
                role="resident",
            )
        ],
        value=madrid,
        reality=RealityStatus.COUNTERFACTUAL,
        temporal=TemporalMeaning(
            frame=TimeFrame.PRESENT,
            expression="ahora",
        ),
    )

    condition = SemanticRelation(
        source_id="accept_job_1",
        relation=SemanticRelationType.CONDITION,
        target_id="live_madrid_1",
    )

    interpretation = Interpretation(
        entities=[user, job, madrid],
        situations=[
            accepted_job,
            live_madrid,
        ],
        semantic_relations=[condition],
    )

    assert all(
        situation.reality
        == RealityStatus.COUNTERFACTUAL
        for situation in interpretation.situations
    )


def test_figurative_expression_does_not_create_literal_death():
    user = make_user()

    fatigue = State(
        semantic_id="fatigue_1",
        semantic_type="fatigue",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="very_tired",
    )

    interpretation = Interpretation(
        discourse=DiscourseMeaning(
            acts=[
                CommunicativeAct.EXPRESS,
            ],
            literal_meaning="Estoy muerto de sueño.",
            intended_meaning="Estoy muy cansado.",
            intended_meaning_confidence=0.98,
        ),
        situations=[fatigue],
    )

    assert (
        interpretation.situations[0].semantic_type
        == "fatigue"
    )

    assert all(
        situation.semantic_type != "death"
        for situation in interpretation.situations
    )

def test_semantic_relation_cannot_reference_missing_node():
    try:
        Interpretation(
            semantic_relations=[
                SemanticRelation(
                    source_id="ghost_1",
                    relation=SemanticRelationType.CAUSE,
                    target_id="ghost_2",
                )
            ]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown semantic_id" in str(exc)


def test_attribution_cannot_reference_missing_content():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    try:
        Interpretation(
            attributions=[
                Attribution(
                    semantic_id="laura_report_1",
                    source=laura,
                    relation=AttributionType.REPORTS,
                    target_id="nonexistent_claim",
                )
            ]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown semantic_id" in str(exc)


def test_proposition_reference_must_target_existing_node():
    user = make_user()

    proposition = Proposition(
        semantic_id="belief_1",
        mode=PropositionMode.BELIEF,
        holder=user,
        content=PropositionReferenceContent(
            target_id="missing_event",
        ),
    )

    try:
        Interpretation(
            propositions=[proposition]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown semantic_id" in str(exc)


def test_evidence_relation_requires_existing_evidence():
    user = make_user()

    wellbeing = State(
        semantic_id="wellbeing_1",
        semantic_type="wellbeing",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="okay",
    )

    try:
        Interpretation(
            situations=[wellbeing],
            evidence_relations=[
                EvidenceRelation(
                    evidence_id="missing_audio",
                    relation=(
                        EvidenceRelationType.QUALIFIES
                    ),
                    target_id="wellbeing_1",
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown evidence_id" in str(exc)


def test_alternative_group_members_must_exist():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    visit = Event(
        semantic_id="laura_visit_1",
        semantic_type="visit",
        participants=[
            Participant(
                entity=laura,
                role="visitor",
            )
        ],
    )

    try:
        Interpretation(
            situations=[visit],
            alternative_groups=[
                AlternativeGroup(
                    semantic_id="alternatives_1",
                    member_ids=[
                        "laura_visit_1",
                        "marta_visit_that_does_not_exist",
                    ],
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown semantic_id" in str(exc)


def test_resolved_discourse_reference_points_to_existing_entity():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    reference = DiscourseReference(
        reference_id="reference_ella_1",
        text="ella",
        candidate_entity_ids=["entity_laura"],
        resolved_entity_id="entity_laura",
        status=ReferenceStatus.RESOLVED,
        confidence=0.98,
    )

    interpretation = Interpretation(
        entities=[laura],
        references=[reference],
    )

    assert (
        interpretation.references[0].resolved_entity_id
        == "entity_laura"
    )
    assert (
        interpretation.references[0].status
        == ReferenceStatus.RESOLVED
    )


def test_ambiguous_pronoun_preserves_multiple_candidates():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    reference = DiscourseReference(
        reference_id="reference_ella_1",
        text="ella",
        candidate_entity_ids=[
            "entity_laura",
            "entity_marta",
        ],
        resolved_entity_id=None,
        status=ReferenceStatus.AMBIGUOUS,
        confidence=0.50,
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        references=[reference],
        unresolved=[
            "The referent of 'ella' is ambiguous."
        ],
    )

    assert set(
        interpretation.references[0].candidate_entity_ids
    ) == {
        "entity_laura",
        "entity_marta",
    }
    assert (
        interpretation.references[0].resolved_entity_id
        is None
    )


def test_discourse_reference_can_remain_unresolved():
    reference = DiscourseReference(
        reference_id="reference_eso_1",
        text="eso",
        candidate_entity_ids=[],
        resolved_entity_id=None,
        status=ReferenceStatus.UNRESOLVED,
        confidence=0.20,
    )

    interpretation = Interpretation(
        references=[reference],
        unresolved=[
            "The referent of 'eso' is unknown."
        ],
    )

    assert (
        interpretation.references[0].status
        == ReferenceStatus.UNRESOLVED
    )
    assert interpretation.entities == []


def test_ordinal_reference_can_resolve_without_creating_new_entity():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    first = DiscourseReference(
        reference_id="reference_first_1",
        text="la primera",
        candidate_entity_ids=[
            "entity_laura",
            "entity_marta",
        ],
        resolved_entity_id="entity_laura",
        status=ReferenceStatus.RESOLVED,
        confidence=1.0,
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        references=[first],
    )

    assert len(interpretation.entities) == 2
    assert (
        interpretation.references[0].resolved_entity_id
        == "entity_laura"
    )


def test_same_turn_ambiguous_reference_does_not_force_event_participant():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    reference = DiscourseReference(
        reference_id="reference_ella_1",
        text="ella",
        candidate_entity_ids=[
            "entity_laura",
            "entity_marta",
        ],
        resolved_entity_id=None,
        status=ReferenceStatus.AMBIGUOUS,
        confidence=0.50,
    )

    interpretation = Interpretation(
        entities=[laura, marta],
        references=[reference],
        unresolved=[
            "Cannot determine who 'ella' refers to."
        ],
    )

    assert interpretation.situations == []
    assert (
        interpretation.references[0].status
        == ReferenceStatus.AMBIGUOUS
    )

def test_same_turn_correction_can_replace_previous_content():
    user = make_user()

    madrid = EntityMention(
        semantic_id="entity_madrid",
        text="Madrid",
        canonical_name="Madrid",
        semantic_type="place",
    )

    getafe = EntityMention(
        semantic_id="entity_getafe",
        text="Getafe",
        canonical_name="Getafe",
        semantic_type="place",
    )

    first_destination = State(
        semantic_id="destination_madrid_1",
        semantic_type="destination",
        participants=[
            Participant(
                entity=user,
                role="traveler",
            )
        ],
        value=madrid,
    )

    corrected_destination = State(
        semantic_id="destination_getafe_1",
        semantic_type="destination",
        participants=[
            Participant(
                entity=user,
                role="traveler",
            )
        ],
        value=getafe,
    )

    revision = DiscourseRevision(
        revision_id="correction_1",
        revision=RevisionType.CORRECTION,
        target_id="destination_madrid_1",
        replacement_id="destination_getafe_1",
    )

    interpretation = Interpretation(
        entities=[
            user,
            madrid,
            getafe,
        ],
        situations=[
            first_destination,
            corrected_destination,
        ],
        revisions=[revision],
    )

    assert (
        interpretation.revisions[0].target_id
        == "destination_madrid_1"
    )

    assert (
        interpretation.revisions[0].replacement_id
        == "destination_getafe_1"
    )

def test_same_turn_intention_can_be_retracted():
    user = make_user()

    leave_job = Transition(
        semantic_id="leave_job_1",
        transition=TransitionKind.END,
        semantic_state="employment",
        participants=[
            Participant(
                entity=user,
                role="employee",
            )
        ],
    )

    intention = Proposition(
        semantic_id="leave_job_intention_1",
        mode=PropositionMode.INTENTION,
        holder=user,
        content=SituationContent(
            situation=leave_job,
        ),
    )

    retraction = DiscourseRevision(
        revision_id="retraction_1",
        revision=RevisionType.RETRACTION,
        target_id="leave_job_intention_1",
    )

    interpretation = Interpretation(
        propositions=[intention],
        revisions=[retraction],
    )

    assert (
        interpretation.revisions[0].revision
        == RevisionType.RETRACTION
    )

    assert (
        interpretation.revisions[0].replacement_id
        is None
    )

def test_reformulation_can_preserve_same_underlying_meaning():
    user = make_user()

    tired = State(
        semantic_id="tired_1",
        semantic_type="fatigue",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="tired",
    )

    exhausted = State(
        semantic_id="exhausted_1",
        semantic_type="fatigue",
        participants=[
            Participant(
                entity=user,
                role="experiencer",
            )
        ],
        value="very_tired",
    )

    reformulation = DiscourseRevision(
        revision_id="reformulation_1",
        revision=RevisionType.REFORMULATION,
        target_id="tired_1",
        replacement_id="exhausted_1",
    )

    interpretation = Interpretation(
        situations=[
            tired,
            exhausted,
        ],
        revisions=[reformulation],
    )

    assert (
        interpretation.revisions[0].revision
        == RevisionType.REFORMULATION
    )

def test_internal_contradiction_can_be_preserved():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    home_positive = State(
        semantic_id="laura_home_positive_1",
        semantic_type="location",
        participants=[
            Participant(
                entity=laura,
                role="located_entity",
            )
        ],
        value="home",
        polarity=Polarity.POSITIVE,
    )

    home_negative = State(
        semantic_id="laura_home_negative_1",
        semantic_type="location",
        participants=[
            Participant(
                entity=laura,
                role="located_entity",
            )
        ],
        value="home",
        polarity=Polarity.NEGATIVE,
    )

    contradiction = SemanticRelation(
        source_id="laura_home_positive_1",
        relation=SemanticRelationType.CONTRADICTS,
        target_id="laura_home_negative_1",
    )

    interpretation = Interpretation(
        entities=[laura],
        situations=[
            home_positive,
            home_negative,
        ],
        semantic_relations=[contradiction],
    )

    assert (
        interpretation.semantic_relations[0].relation
        == SemanticRelationType.CONTRADICTS
    )

def test_ellipsis_can_inherit_previous_event_structure():
    fernando = EntityMention(
        semantic_id="entity_fernando",
        text="Fernando",
        canonical_name="Fernando",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    bar = EntityMention(
        semantic_id="entity_bar",
        text="el bar",
        semantic_type="place",
    )

    fernando_goes = Event(
        semantic_id="fernando_goes_bar_1",
        semantic_type="go",
        participants=[
            Participant(
                entity=fernando,
                role="traveler",
            ),
            Participant(
                entity=bar,
                role="destination",
            ),
        ],
    )

    marta_goes = Event(
        semantic_id="marta_goes_bar_1",
        semantic_type="go",
        participants=[
            Participant(
                entity=marta,
                role="traveler",
            ),
            Participant(
                entity=bar,
                role="destination",
            ),
        ],
    )

    ellipsis = EllipsisResolution(
        ellipsis_id="ellipsis_tambien_1",
        text="también",
        antecedent_ids=[
            "fernando_goes_bar_1",
        ],
        resolved_semantic_id="marta_goes_bar_1",
        status=ReferenceStatus.RESOLVED,
    )

    interpretation = Interpretation(
        entities=[
            fernando,
            marta,
            bar,
        ],
        situations=[
            fernando_goes,
            marta_goes,
        ],
        ellipsis_resolutions=[ellipsis],
    )

    assert (
        interpretation.ellipsis_resolutions[0].status
        == ReferenceStatus.RESOLVED
    )

def test_gapping_can_recover_omitted_predicate():
    user = make_user()

    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    pizza = EntityMention(
        semantic_id="entity_pizza",
        text="pizza",
        semantic_type="food",
    )

    pasta = EntityMention(
        semantic_id="entity_pasta",
        text="pasta",
        semantic_type="food",
    )

    user_order = Event(
        semantic_id="user_order_pizza_1",
        semantic_type="order",
        participants=[
            Participant(
                entity=user,
                role="customer",
            ),
            Participant(
                entity=pizza,
                role="item",
            ),
        ],
    )

    laura_order = Event(
        semantic_id="laura_order_pasta_1",
        semantic_type="order",
        participants=[
            Participant(
                entity=laura,
                role="customer",
            ),
            Participant(
                entity=pasta,
                role="item",
            ),
        ],
    )

    ellipsis = EllipsisResolution(
        ellipsis_id="gapping_1",
        text="Laura pasta",
        antecedent_ids=[
            "user_order_pizza_1",
        ],
        resolved_semantic_id="laura_order_pasta_1",
        status=ReferenceStatus.RESOLVED,
    )

    interpretation = Interpretation(
        entities=[
            user,
            laura,
            pizza,
            pasta,
        ],
        situations=[
            user_order,
            laura_order,
        ],
        ellipsis_resolutions=[ellipsis],
    )

    assert (
        interpretation
        .ellipsis_resolutions[0]
        .resolved_semantic_id
        == "laura_order_pasta_1"
    )

def test_ellipsis_can_remain_unresolved():
    interpretation = Interpretation(
        ellipsis_resolutions=[
            EllipsisResolution(
                ellipsis_id="ellipsis_1",
                text="también",
                status=ReferenceStatus.UNRESOLVED,
            )
        ],
        unresolved=[
            "The antecedent of 'también' is unknown."
        ],
    )

    assert (
        interpretation.ellipsis_resolutions[0].status
        == ReferenceStatus.UNRESOLVED
    )

    assert (
        interpretation
        .ellipsis_resolutions[0]
        .resolved_semantic_id
        is None
    )

def test_revision_cannot_reference_missing_semantic_node():
    try:
        Interpretation(
            revisions=[
                DiscourseRevision(
                    revision_id="bad_revision_1",
                    revision=RevisionType.CORRECTION,
                    target_id="thing_that_does_not_exist",
                )
            ]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "unknown semantic_id" in str(exc)

def test_resolved_reference_points_to_candidate_entity():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    reference = DiscourseReference(
        reference_id="reference_ella_1",
        text="ella",
        candidate_entity_ids=[
            "entity_laura",
            "entity_marta",
        ],
        resolved_entity_id="entity_marta",
        status=ReferenceStatus.RESOLVED,
    )

    interpretation = Interpretation(
        entities=[
            laura,
            marta,
        ],
        references=[reference],
    )

    assert (
        interpretation.references[0].resolved_entity_id
        == "entity_marta"
    )

def test_resolved_reference_requires_resolved_entity():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    try:
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        "entity_laura",
                    ],
                    status=ReferenceStatus.RESOLVED,
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "requires resolved_entity_id" in str(exc)

def test_resolved_reference_must_choose_candidate():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    marta = EntityMention(
        semantic_id="entity_marta",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    fernando = EntityMention(
        semantic_id="entity_fernando",
        text="Fernando",
        canonical_name="Fernando",
        semantic_type="person",
    )

    try:
        Interpretation(
            entities=[
                laura,
                marta,
                fernando,
            ],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        "entity_laura",
                        "entity_marta",
                    ],
                    resolved_entity_id=(
                        "entity_fernando"
                    ),
                    status=ReferenceStatus.RESOLVED,
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert (
            "must resolve to one of its candidates"
            in str(exc)
        )

def test_ambiguous_reference_requires_multiple_candidates():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    try:
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        "entity_laura",
                    ],
                    status=ReferenceStatus.AMBIGUOUS,
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert (
            "requires at least two candidates"
            in str(exc)
        )

def test_reference_candidates_must_exist():
    laura = EntityMention(
        semantic_id="entity_laura",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    try:
        Interpretation(
            entities=[laura],
            references=[
                DiscourseReference(
                    reference_id="reference_ella_1",
                    text="ella",
                    candidate_entity_ids=[
                        "entity_laura",
                        "entity_marta_that_does_not_exist",
                    ],
                    status=ReferenceStatus.AMBIGUOUS,
                )
            ],
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "references unknown entity" in str(exc)

def test_entity_ids_must_be_unique():
    first = EntityMention(
        semantic_id="entity_person_1",
        text="Laura",
        canonical_name="Laura",
        semantic_type="person",
    )

    second = EntityMention(
        semantic_id="entity_person_1",
        text="Marta",
        canonical_name="Marta",
        semantic_type="person",
    )

    try:
        Interpretation(
            entities=[
                first,
                second,
            ]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert (
            "Duplicate entity semantic_id"
            in str(exc)
        )

def test_top_level_semantic_node_ids_must_be_unique():
    first = Event(
        semantic_id="semantic_1",
        semantic_type="rain",
    )

    second = State(
        semantic_id="semantic_1",
        semantic_type="weather",
        value="bad",
    )

    try:
        Interpretation(
            situations=[
                first,
                second,
            ]
        )

        assert False, "Expected ValidationError"

    except ValidationError as exc:
        assert "duplicate semantic_id" in str(exc)