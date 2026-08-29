from __future__ import annotations

from celeste.cognition.interpretation import (
    Attribution,
    AttributionType,
    Certainty,
    CommunicativeAct,
    DiscourseMeaning,
    DiscourseReference,
    DiscourseRevision,
    Entity,
    EntityMention,
    Event,
    Interpretation,
    Participant,
    ParticipantRole,
    Polarity,
    Proposition,
    PropositionMode,
    PropositionReferenceContent,
    RealityStatus,
    ReferenceStatus,
    RevisionType,
    SemanticRelation,
    SemanticRelationType,
    SemanticContentLink,
    ScopeOperator,
    ScopeOperatorType,
    SituationContent,
    State,
    TemporalMeaning,
    TimeFrame,
    Transition,
    TransitionKind,
)

from celeste.cognition.raw_interpretation import (
    RawAttribution,
    RawInterpretation,
    RawProposition,
    RawReference,
    RawRevision,
    RawScopeOperator,
    RawSemanticContentLink,
    RawSemanticRelation,
    RawSituation,
    RawSituationKind,
    RawTemporalMeaning,
)


class InterpretationNormalizationError(ValueError):
    pass


def _entity_id(temp_id: str) -> str:
    return f"entity_{temp_id}"


def _mention_id(temp_id: str) -> str:
    return f"mention_{temp_id}_1"


def _reference_id(temp_id: str) -> str:
    return f"reference_{temp_id}"


def _normalize_temporal(
    temporal: RawTemporalMeaning | None,
) -> TemporalMeaning | None:
    if temporal is None:
        return None

    return TemporalMeaning(
        frame=TimeFrame(temporal.frame),
        expression=temporal.expression,
        confidence=temporal.confidence,
    )

def _normalize_participants(
    participants,
) -> list[Participant]:
    normalized: list[Participant] = []

    for participant in participants:
        try:
            role = ParticipantRole(
                participant.role.value
            )
        except ValueError as exc:
            raise InterpretationNormalizationError(
                "Unsupported participant role "
                f"{participant.role!r}"
            ) from exc

        if participant.entity_temp_id is not None:
            normalized.append(
                Participant(
                    entity_id=_entity_id(
                        participant.entity_temp_id
                    ),
                    role=role,
                )
            )

        elif participant.reference_temp_id is not None:
            normalized.append(
                Participant(
                    reference_id=_reference_id(
                        participant.reference_temp_id
                    ),
                    role=role,
                )
            )

        else:
            raise InterpretationNormalizationError(
                "Raw participant has no target"
            )

    return normalized

def _normalize_event(
    raw: RawSituation,
    semantic_id: str,
) -> Event:
    if raw.semantic_type is None:
        raise InterpretationNormalizationError(
            f"Raw event {raw.temp_id!r} requires semantic_type"
        )

    return Event(
        semantic_id=semantic_id,
        semantic_type=raw.semantic_type,
        participants=_normalize_participants(
            raw.participants
        ),
        temporal=_normalize_temporal(
            raw.temporal
        ),
        polarity=Polarity(raw.polarity.value),
        reality=RealityStatus(raw.reality.value),
        certainty=Certainty(raw.certainty.value),
        confidence=raw.confidence,
    )


def _normalize_state(
    raw: RawSituation,
    semantic_id: str,
) -> State:
    if raw.semantic_type is None:
        raise InterpretationNormalizationError(
            f"Raw state {raw.temp_id!r} requires semantic_type"
        )

    return State(
        semantic_id=semantic_id,
        semantic_type=raw.semantic_type,
        participants=_normalize_participants(
            raw.participants
        ),
        value=raw.value,
        temporal=_normalize_temporal(
            raw.temporal
        ),
        polarity=Polarity(raw.polarity.value),
        reality=RealityStatus(raw.reality.value),
        certainty=Certainty(raw.certainty.value),
        confidence=raw.confidence,
    )


def _normalize_transition(
    raw: RawSituation,
    semantic_id: str,
) -> Transition:

    return Transition(
        semantic_id=semantic_id,
        semantic_state=raw.semantic_state,
        transition=(
            TransitionKind(raw.transition)
            if raw.transition is not None
            else None
        ),
        participants=_normalize_participants(
            raw.participants
        ),
        previous_value=raw.previous_value,
        new_value=raw.new_value,
        temporal=_normalize_temporal(
            raw.temporal
        ),
        polarity=Polarity(raw.polarity.value),
        reality=RealityStatus(raw.reality.value),
        certainty=Certainty(raw.certainty.value),
        confidence=raw.confidence,
    )


def _normalize_situation(
    raw: RawSituation,
    semantic_id: str,
):
    if raw.kind == RawSituationKind.EVENT:
        return _normalize_event(
            raw,
            semantic_id,
        )

    if raw.kind == RawSituationKind.STATE:
        return _normalize_state(
            raw,
            semantic_id,
        )

    if raw.kind == RawSituationKind.TRANSITION:
        return _normalize_transition(
            raw,
            semantic_id,
        )

    raise InterpretationNormalizationError(
        "Unsupported raw situation kind "
        f"{raw.kind!r}"
    )


def _build_semantic_id_map(
    raw: RawInterpretation,
) -> dict[str, str]:
    """
    Build every semantic ID before graph edges are normalized.

    Raw situations that later become nested SituationContent still
    receive a stable semantic ID here, so other semantic nodes may
    reference them safely.
    """

    mapping: dict[str, str] = {}

    def register(
        temp_id: str,
        semantic_id: str,
    ) -> None:
        if temp_id in mapping:
            raise InterpretationNormalizationError(
                "Duplicate raw semantic temp_id "
                f"{temp_id!r}"
            )

        mapping[temp_id] = semantic_id

    for situation in raw.situations:
        if situation.kind == RawSituationKind.EVENT:
            prefix = "event"

        elif situation.kind == RawSituationKind.STATE:
            prefix = "state"

        elif situation.kind == RawSituationKind.TRANSITION:
            prefix = "transition"

        else:
            raise InterpretationNormalizationError(
                "Unsupported raw situation kind "
                f"{situation.kind!r}"
            )

        register(
            situation.temp_id,
            f"{prefix}_{situation.temp_id}",
        )

    for proposition in raw.propositions:
        register(
            proposition.temp_id,
            f"proposition_{proposition.temp_id}",
        )

    for attribution in raw.attributions:
        register(
            attribution.temp_id,
            f"attribution_{attribution.temp_id}",
        )

    return mapping


def _require_semantic_mapping(
    temp_id: str,
    mapping: dict[str, str],
    *,
    owner: str,
) -> str:
    try:
        return mapping[temp_id]
    except KeyError as exc:
        raise InterpretationNormalizationError(
            f"{owner} references unknown raw semantic "
            f"temp_id {temp_id!r}"
        ) from exc


def _normalize_proposition(
    raw: RawProposition,
    mapping: dict[str, str],
    normalized_situations: dict[str, Event | State | Transition],
    embedded_situation_ids: set[str],
) -> Proposition:
    """
    Mental/epistemic attitudes scope their situation content.

    If a raw proposition targets a situation, the first proposition
    that owns that target embeds the Situation directly. This prevents
    content such as "Marta is angry" in "I think Marta is angry" from
    also appearing as a standalone external situation.

    If another proposition targets the same situation, it references
    the already-registered nested semantic node instead of embedding a
    duplicate object with the same semantic_id.
    """

    target_semantic_id = _require_semantic_mapping(
        raw.target_id,
        mapping,
        owner=f"RawProposition {raw.temp_id!r}",
    )

    target_situation = normalized_situations.get(
        raw.target_id
    )

    if (
        target_situation is not None
        and raw.target_id not in embedded_situation_ids
    ):
        content = SituationContent(
            situation=target_situation
        )
        embedded_situation_ids.add(
            raw.target_id
        )

    else:
        content = PropositionReferenceContent(
            target_id=target_semantic_id
        )

    return Proposition(
        semantic_id=mapping[raw.temp_id],
        mode=PropositionMode(
            raw.mode.value
        ),
        holder_entity_id=_entity_id(
            raw.holder_entity_temp_id
        ),
        content=content,
        polarity=Polarity(
            raw.polarity.value
        ),
        certainty=Certainty(
            raw.certainty.value
        ),
        confidence=raw.confidence,
    )


def _normalize_attribution(
    raw: RawAttribution,
    mapping: dict[str, str],
) -> Attribution:
    return Attribution(
        semantic_id=mapping[raw.temp_id],
        source_entity_id=_entity_id(
            raw.source_entity_temp_id
        ),
        relation=AttributionType(
            raw.relation.value
        ),
        target_id=_require_semantic_mapping(
            raw.target_id,
            mapping,
            owner=(
                f"RawAttribution "
                f"{raw.temp_id!r}"
            ),
        ),
        confidence=raw.confidence,
    )


def _normalize_reference(
    raw: RawReference,
) -> DiscourseReference:
    candidates = [
        _entity_id(temp_id)
        for temp_id
        in raw.candidate_entity_temp_ids
    ]

    resolved = (
        _entity_id(
            raw.resolved_entity_temp_id
        )
        if raw.resolved_entity_temp_id
        is not None
        else None
    )

    if resolved is not None:
        status = ReferenceStatus.RESOLVED

    elif len(candidates) >= 2:
        status = ReferenceStatus.AMBIGUOUS

    else:
        status = ReferenceStatus.UNRESOLVED

    return DiscourseReference(
        reference_id=_reference_id(
            raw.temp_id
        ),
        text=raw.text,
        candidate_entity_ids=candidates,
        resolved_entity_id=resolved,
        status=status,
        confidence=raw.confidence,
    )


def _normalize_revision(
    raw: RawRevision,
    mapping: dict[str, str],
) -> DiscourseRevision:
    target_id = _require_semantic_mapping(
        raw.target_id,
        mapping,
        owner=f"RawRevision {raw.temp_id!r}",
    )

    replacement_id = None

    if raw.replacement_id is not None:
        replacement_id = (
            _require_semantic_mapping(
                raw.replacement_id,
                mapping,
                owner=(
                    f"RawRevision "
                    f"{raw.temp_id!r}"
                ),
            )
        )

    return DiscourseRevision(
        revision_id=(
            f"revision_{raw.temp_id}"
        ),
        revision=RevisionType(
            raw.revision.value
        ),
        target_id=target_id,
        replacement_id=replacement_id,
        confidence=raw.confidence,
    )


def _normalize_relation(
    raw: RawSemanticRelation,
    mapping: dict[str, str],
) -> SemanticRelation:
    return SemanticRelation(
        source_id=_require_semantic_mapping(
            raw.source_id,
            mapping,
            owner="RawSemanticRelation.source_id",
        ),
        relation=SemanticRelationType(
            raw.relation.value
        ),
        target_id=_require_semantic_mapping(
            raw.target_id,
            mapping,
            owner="RawSemanticRelation.target_id",
        ),
        confidence=raw.confidence,
    )

def _normalize_semantic_content_link(
    raw: RawSemanticContentLink,
    mapping: dict[str, str],
) -> SemanticContentLink:
    return SemanticContentLink(
        source_id=_require_semantic_mapping(
            raw.source_id,
            mapping,
            owner="RawSemanticContentLink.source_id",
        ),
        target_id=_require_semantic_mapping(
            raw.target_id,
            mapping,
            owner="RawSemanticContentLink.target_id",
        ),
        confidence=raw.confidence,
    )

def _normalize_scope_operator(
    raw: RawScopeOperator,
    mapping: dict[str, str],
) -> ScopeOperator:
    return ScopeOperator(
        operator_id=f"scope_{raw.temp_id}",
        operator=ScopeOperatorType(
            raw.operator.value
        ),
        target_id=_require_semantic_mapping(
            raw.target_id,
            mapping,
            owner=(
                f"RawScopeOperator "
                f"{raw.temp_id!r}"
            ),
        ),
        confidence=raw.confidence,
    )

def normalize_interpretation(
    raw: RawInterpretation,
) -> Interpretation:
    """
    Convert the forgiving LLM-facing RawInterpretation into the
    strict semantic Interpretation used internally by Celeste.

    Situations that are explicit contents of mental/epistemic
    propositions are scoped inside those propositions rather than
    duplicated as standalone external situations.
    """

    semantic_id_map = (
        _build_semantic_id_map(raw)
    )

    entities = [
        Entity(
            entity_id=_entity_id(
                entity.temp_id
            ),
            canonical_name=(
                entity.canonical_name
            ),
            semantic_type=(
                entity.semantic_type
            ),
            identity_hint=(
                entity.identity_hint
            ),
            confidence=(
                entity.confidence
            ),
        )
        for entity in raw.entities
    ]

    mentions = [
        EntityMention(
            mention_id=_mention_id(
                entity.temp_id
            ),
            text=entity.mention,
            entity_id=_entity_id(
                entity.temp_id
            ),
            confidence=(
                entity.confidence
            ),
        )
        for entity in raw.entities
    ]

    references = [
        _normalize_reference(reference)
        for reference
        in raw.references
    ]

    normalized_situations: dict[
        str,
        Event | State | Transition,
    ] = {}

    for situation in raw.situations:
        normalized_situations[
            situation.temp_id
        ] = _normalize_situation(
            situation,
            semantic_id_map[
                situation.temp_id
            ],
        )

    # Any situation targeted by a mental/epistemic proposition is
    # proposition-scoped, not a standalone external situation.
    proposition_targeted_situations = {
        proposition.target_id
        for proposition in raw.propositions
        if proposition.target_id
        in normalized_situations
    }

    situations = [
        normalized_situations[
            situation.temp_id
        ]
        for situation in raw.situations
        if situation.temp_id
        not in proposition_targeted_situations
    ]

    embedded_situation_ids: set[str] = set()

    propositions = [
        _normalize_proposition(
            proposition,
            semantic_id_map,
            normalized_situations,
            embedded_situation_ids,
        )
        for proposition
        in raw.propositions
    ]

    attributions = [
        _normalize_attribution(
            attribution,
            semantic_id_map,
        )
        for attribution
        in raw.attributions
    ]

    revisions = [
        _normalize_revision(
            revision,
            semantic_id_map,
        )
        for revision
        in raw.revisions
    ]

    semantic_relations = [
        _normalize_relation(
            relation,
            semantic_id_map,
        )
        for relation
        in raw.semantic_relations
    ]

    semantic_content_links = [
        _normalize_semantic_content_link(
            link,
            semantic_id_map,
        )
        for link
        in raw.semantic_content_links
    ]

    scope_operators = [
        _normalize_scope_operator(
            operator,
            semantic_id_map,
        )
        for operator
        in raw.scope_operators
    ]

    acts: list[CommunicativeAct] = []

    for raw_act in raw.discourse.acts:
        try:
            acts.append(
                CommunicativeAct(
                    raw_act.value
                )
            )
        except ValueError as exc:
            raise (
                InterpretationNormalizationError(
                    "Unsupported communicative act "
                    f"{raw_act!r}"
                )
            ) from exc

    discourse = DiscourseMeaning(
        acts=acts,
        literal_meaning=(
            raw.discourse.literal_meaning
        ),
        intended_meaning=(
            raw.discourse.intended_meaning
        ),
        intended_meaning_confidence=(
            raw.discourse
            .intended_meaning_confidence
        ),
    )

    return Interpretation(
        discourse=discourse,
        entities=entities,
        mentions=mentions,
        situations=situations,
        propositions=propositions,
        attributions=attributions,
        references=references,
        revisions=revisions,
        semantic_relations=semantic_relations,
        semantic_content_links=semantic_content_links,
        scope_operators=scope_operators,
        unresolved=list(
            raw.unresolved
        ),
        overall_confidence=(
            raw.overall_confidence
        ),
    )
