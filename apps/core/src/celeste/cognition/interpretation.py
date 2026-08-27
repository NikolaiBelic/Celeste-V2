from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator


class Certainty(StrEnum):
    ASSERTED = "asserted"
    INFERRED = "inferred"
    UNCERTAIN = "uncertain"


class Polarity(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class PropositionMode(StrEnum):
    FACT = "fact"
    BELIEF = "belief"
    HYPOTHESIS = "hypothesis"
    INTENTION = "intention"
    DESIRE = "desire"
    PREFERENCE = "preference"
    OPINION = "opinion"
    POSSIBILITY = "possibility"
    KNOWLEDGE = "knowledge"


class SituationKind(StrEnum):
    EVENT = "event"
    STATE = "state"
    TRANSITION = "transition"


class TransitionKind(StrEnum):
    START = "start"
    END = "end"
    RESUME = "resume"
    PAUSE = "pause"
    CHANGE = "change"
    CONTINUE = "continue"
    CANCEL = "cancel"


class TimeFrame(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    UNKNOWN = "unknown"


class CommunicativeAct(StrEnum):
    ASSERT = "assert"
    ASK = "ask"
    REQUEST = "request"
    CORRECT = "correct"
    CONFIRM = "confirm"
    DENY = "deny"
    EXPRESS = "express"
    SPECULATE = "speculate"


class EvidenceModality(StrEnum):
    TEXT = "text"
    AUDIO = "audio"
    VISION = "vision"
    SENSOR = "sensor"
    TOOL = "tool"


class EvidenceRelationType(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    QUALIFIES = "qualifies"
    SUGGESTS = "suggests"


class AttributionType(StrEnum):
    ASSERTS = "asserts"
    REPORTS = "reports"


class SemanticRelationType(StrEnum):
    CAUSE = "cause"
    REASON = "reason"
    CONSEQUENCE = "consequence"
    CONTRAST = "contrast"
    CONDITION = "condition"
    ENABLES = "enables"
    PREVENTS = "prevents"
    TEMPORAL_BEFORE = "temporal_before"
    TEMPORAL_AFTER = "temporal_after"
    CORRECTS = "corrects"
    PRESUPPOSES = "presupposes"
    CONTRADICTS = "contradicts"


class ScopeOperatorType(StrEnum):
    NEGATION = "negation"
    EXCLUSIVITY = "exclusivity"


class ReferenceStatus(StrEnum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    UNRESOLVED = "unresolved"


class RealityStatus(StrEnum):
    ACTUAL = "actual"
    HYPOTHETICAL = "hypothetical"
    COUNTERFACTUAL = "counterfactual"


class QuantifierType(StrEnum):
    ALL = "all"
    SOME = "some"
    NONE = "none"
    MOST = "most"
    EXACTLY = "exactly"
    AT_LEAST = "at_least"
    AT_MOST = "at_most"


class ComparisonOperator(StrEnum):
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    AT_LEAST = "at_least"
    AT_MOST = "at_most"


class RevisionType(StrEnum):
    CORRECTION = "correction"
    RETRACTION = "retraction"
    REFORMULATION = "reformulation"


class Entity(BaseModel):
    """
    A turn-local semantic entity.

    This is the referent in the semantic graph, not a textual mention.
    Persistent identity resolution belongs to later cognitive stages.
    """

    entity_id: str
    canonical_name: str | None = None
    semantic_type: str | None = None
    identity_hint: str | None = None
    qualifiers: dict[str, str] = Field(default_factory=dict)

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class EntityMention(BaseModel):
    """
    One surface occurrence in the current utterance.

    Multiple mentions may point to the same Entity.
    A mention may remain unresolved by leaving entity_id as None.
    """

    mention_id: str
    text: str
    entity_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class EntityReferenceValue(BaseModel):
    entity_id: str


SemanticValue = (
    str
    | int
    | float
    | bool
    | EntityReferenceValue
    | None
)


class DiscourseReference(BaseModel):
    reference_id: str
    text: str

    candidate_entity_ids: list[str] = Field(
        default_factory=list
    )

    resolved_entity_id: str | None = None
    status: ReferenceStatus

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class DiscourseRevision(BaseModel):
    revision_id: str
    revision: RevisionType
    target_id: str
    replacement_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class EllipsisResolution(BaseModel):
    ellipsis_id: str
    text: str

    antecedent_ids: list[str] = Field(
        default_factory=list
    )

    resolved_semantic_id: str | None = None
    status: ReferenceStatus

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class TemporalMeaning(BaseModel):
    frame: TimeFrame = TimeFrame.UNKNOWN
    expression: str | None = None
    start: str | None = None
    end: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Participant(BaseModel):
    role: str

    entity_id: str | None = None
    reference_id: str | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "Participant":
        targets = sum(
            value is not None
            for value in (
                self.entity_id,
                self.reference_id,
            )
        )

        if targets != 1:
            raise ValueError(
                "Participant requires exactly one of "
                "entity_id or reference_id"
            )

        return self


class Evidence(BaseModel):
    evidence_id: str
    modality: EvidenceModality
    signal_type: str
    value: str
    source_entity_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class EvidenceRelation(BaseModel):
    evidence_id: str
    relation: EvidenceRelationType
    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Event(BaseModel):
    semantic_id: str

    kind: Literal[SituationKind.EVENT] = SituationKind.EVENT
    semantic_type: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    temporal: TemporalMeaning | None = None
    polarity: Polarity = Polarity.POSITIVE
    reality: RealityStatus = RealityStatus.ACTUAL
    certainty: Certainty = Certainty.ASSERTED

    attributes: dict[str, SemanticValue] = Field(
        default_factory=dict
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class State(BaseModel):
    semantic_id: str

    kind: Literal[SituationKind.STATE] = SituationKind.STATE
    semantic_type: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    value: SemanticValue = None
    temporal: TemporalMeaning | None = None
    polarity: Polarity = Polarity.POSITIVE
    reality: RealityStatus = RealityStatus.ACTUAL
    certainty: Certainty = Certainty.ASSERTED

    attributes: dict[str, SemanticValue] = Field(
        default_factory=dict
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Transition(BaseModel):
    semantic_id: str

    kind: Literal[SituationKind.TRANSITION] = SituationKind.TRANSITION
    transition: TransitionKind
    semantic_state: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    previous_value: SemanticValue = None
    new_value: SemanticValue = None
    temporal: TemporalMeaning | None = None
    polarity: Polarity = Polarity.POSITIVE
    reality: RealityStatus = RealityStatus.ACTUAL
    certainty: Certainty = Certainty.ASSERTED

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


Situation = Annotated[
    Event | State | Transition,
    Field(discriminator="kind"),
]


class RelationContent(BaseModel):
    kind: Literal["relation"] = "relation"
    subject_entity_id: str
    predicate: str
    object: SemanticValue = None
    polarity: Polarity = Polarity.POSITIVE


class SituationContent(BaseModel):
    kind: Literal["situation"] = "situation"
    situation: Situation


class PropositionReferenceContent(BaseModel):
    kind: Literal["reference"] = "reference"
    target_id: str


PropositionContent = Annotated[
    RelationContent
    | SituationContent
    | PropositionReferenceContent,
    Field(discriminator="kind"),
]


class Proposition(BaseModel):
    semantic_id: str
    mode: PropositionMode
    holder_entity_id: str
    content: PropositionContent

    polarity: Polarity = Polarity.POSITIVE
    temporal: TemporalMeaning | None = None
    certainty: Certainty = Certainty.ASSERTED

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class SemanticRelation(BaseModel):
    source_id: str
    relation: SemanticRelationType
    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Attribution(BaseModel):
    semantic_id: str
    source_entity_id: str
    relation: AttributionType
    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class ScopeOperator(BaseModel):
    operator_id: str
    operator: ScopeOperatorType
    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Quantifier(BaseModel):
    operator_id: str
    quantifier: QuantifierType
    target_id: str
    role: str | None = None
    amount: int | None = None
    domain: str | None = None

    exception_entity_ids: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Comparison(BaseModel):
    semantic_id: str
    left: SemanticValue
    dimension: str
    operator: ComparisonOperator
    right: SemanticValue
    degree: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class AlternativeGroup(BaseModel):
    semantic_id: str

    member_ids: list[str] = Field(
        min_length=2
    )

    exclusive: bool | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class InterpretationAlternative(BaseModel):
    description: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence: list[str] = Field(
        default_factory=list
    )


class DiscourseMeaning(BaseModel):
    acts: list[CommunicativeAct] = Field(
        default_factory=list
    )

    literal_meaning: str | None = None
    intended_meaning: str | None = None

    intended_meaning_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class Interpretation(BaseModel):
    discourse: DiscourseMeaning = Field(
        default_factory=DiscourseMeaning
    )

    entities: list[Entity] = Field(
        default_factory=list
    )

    mentions: list[EntityMention] = Field(
        default_factory=list
    )

    references: list[DiscourseReference] = Field(
        default_factory=list
    )

    revisions: list[DiscourseRevision] = Field(
        default_factory=list
    )

    ellipsis_resolutions: list[EllipsisResolution] = Field(
        default_factory=list
    )

    propositions: list[Proposition] = Field(
        default_factory=list
    )

    situations: list[Situation] = Field(
        default_factory=list
    )

    semantic_relations: list[SemanticRelation] = Field(
        default_factory=list
    )

    attributions: list[Attribution] = Field(
        default_factory=list
    )

    scope_operators: list[ScopeOperator] = Field(
        default_factory=list
    )

    quantifiers: list[Quantifier] = Field(
        default_factory=list
    )

    comparisons: list[Comparison] = Field(
        default_factory=list
    )

    alternative_groups: list[AlternativeGroup] = Field(
        default_factory=list
    )

    evidence: list[Evidence] = Field(
        default_factory=list
    )

    evidence_relations: list[EvidenceRelation] = Field(
        default_factory=list
    )

    alternatives: list[InterpretationAlternative] = Field(
        default_factory=list
    )

    unresolved: list[str] = Field(
        default_factory=list
    )

    overall_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @model_validator(mode="after")
    def validate_graph(self) -> "Interpretation":
        entity_ids: set[str] = set()
        semantic_ids: set[str] = set()
        mention_ids: set[str] = set()
        evidence_ids: set[str] = set()
        reference_ids: set[str] = set()

        def register_unique(
            value: str,
            registry: set[str],
            *,
            label: str,
        ) -> None:
            if value in registry:
                raise ValueError(
                    f"Duplicate {label} {value!r}"
                )
            registry.add(value)

        def require_entity_id(
            entity_id: str,
            *,
            owner: str,
        ) -> None:
            if entity_id not in entity_ids:
                raise ValueError(
                    f"{owner} references unknown entity_id "
                    f"{entity_id!r}"
                )

        def register_semantic_id(
            semantic_id: str,
            *,
            owner: str,
        ) -> None:
            if semantic_id in semantic_ids:
                raise ValueError(
                    f"{owner} uses duplicate semantic_id "
                    f"{semantic_id!r}"
                )
            semantic_ids.add(semantic_id)

        def require_semantic_id(
            semantic_id: str,
            *,
            owner: str,
        ) -> None:
            if semantic_id not in semantic_ids:
                raise ValueError(
                    f"{owner} references unknown semantic_id "
                    f"{semantic_id!r}"
                )

        def validate_semantic_value(
            value: SemanticValue,
            *,
            owner: str,
        ) -> None:
            if isinstance(
                value,
                EntityReferenceValue,
            ):
                require_entity_id(
                    value.entity_id,
                    owner=owner,
                )

        def validate_situation_entities(
            situation: Situation,
            *,
            owner: str,
        ) -> None:
            for participant in situation.participants:
                if participant.entity_id is not None:
                    require_entity_id(
                        participant.entity_id,
                        owner=owner,
                    )

                elif participant.reference_id is not None:
                    if (
                        participant.reference_id
                        not in reference_ids
                    ):
                        raise ValueError(
                            f"{owner} references unknown "
                            "discourse reference "
                            f"{participant.reference_id!r}"
                        )

            if isinstance(
                situation,
                State,
            ):
                validate_semantic_value(
                    situation.value,
                    owner=f"{owner}.value",
                )

                for key, value in (
                    situation.attributes.items()
                ):
                    validate_semantic_value(
                        value,
                        owner=(
                            f"{owner}.attributes"
                            f"[{key!r}]"
                        ),
                    )

            elif isinstance(
                situation,
                Event,
            ):
                for key, value in (
                    situation.attributes.items()
                ):
                    validate_semantic_value(
                        value,
                        owner=(
                            f"{owner}.attributes"
                            f"[{key!r}]"
                        ),
                    )

            elif isinstance(
                situation,
                Transition,
            ):
                validate_semantic_value(
                    situation.previous_value,
                    owner=f"{owner}.previous_value",
                )

                validate_semantic_value(
                    situation.new_value,
                    owner=f"{owner}.new_value",
                )
                
        # Entities are the canonical turn-local referents.
        for entity in self.entities:
            register_unique(
                entity.entity_id,
                entity_ids,
                label="entity_id",
            )

        # Surface mentions may repeat the same entity, but each
        # occurrence gets its own mention_id.
        for mention in self.mentions:
            register_unique(
                mention.mention_id,
                mention_ids,
                label="mention_id",
            )

            if mention.entity_id is not None:
                require_entity_id(
                    mention.entity_id,
                    owner=(
                        f"EntityMention "
                        f"{mention.mention_id!r}"
                    ),
                )

        for reference in self.references:
            register_unique(
                reference.reference_id,
                reference_ids,
                label="reference_id",
            )

        # Register all semantic nodes first, so graph references
        # may point forward or backward within the same turn.
        for situation in self.situations:
            register_semantic_id(
                situation.semantic_id,
                owner="Situation",
            )

        for proposition in self.propositions:
            register_semantic_id(
                proposition.semantic_id,
                owner="Proposition",
            )

            if isinstance(
                proposition.content,
                SituationContent,
            ):
                register_semantic_id(
                    proposition.content.situation.semantic_id,
                    owner=(
                        f"Nested situation in proposition "
                        f"{proposition.semantic_id!r}"
                    ),
                )

        for attribution in self.attributions:
            register_semantic_id(
                attribution.semantic_id,
                owner="Attribution",
            )

        for comparison in self.comparisons:
            register_semantic_id(
                comparison.semantic_id,
                owner="Comparison",
            )

        for group in self.alternative_groups:
            register_semantic_id(
                group.semantic_id,
                owner="AlternativeGroup",
            )

        # Validate entity references in situations.
        for situation in self.situations:
            validate_situation_entities(
                situation,
                owner=(
                    f"Situation {situation.semantic_id!r}"
                ),
            )

        # Propositions.
        for proposition in self.propositions:
            require_entity_id(
                proposition.holder_entity_id,
                owner=(
                    f"Proposition "
                    f"{proposition.semantic_id!r}"
                ),
            )

            if isinstance(
                proposition.content,
                RelationContent,
            ):
                require_entity_id(
                    proposition.content.subject_entity_id,
                    owner=(
                        f"Proposition "
                        f"{proposition.semantic_id!r}"
                        ".content"
                    ),
                )
                validate_semantic_value(
                    proposition.content.object,
                    owner=(
                        f"Proposition "
                        f"{proposition.semantic_id!r}"
                        ".content.object"
                    ),
                )

            elif isinstance(
                proposition.content,
                SituationContent,
            ):
                validate_situation_entities(
                    proposition.content.situation,
                    owner=(
                        f"Nested situation "
                        f"{proposition.content.situation.semantic_id!r}"
                    ),
                )

            elif isinstance(
                proposition.content,
                PropositionReferenceContent,
            ):
                require_semantic_id(
                    proposition.content.target_id,
                    owner=(
                        f"Proposition "
                        f"{proposition.semantic_id!r}"
                    ),
                )

        # Semantic relations.
        for relation in self.semantic_relations:
            require_semantic_id(
                relation.source_id,
                owner="SemanticRelation.source_id",
            )
            require_semantic_id(
                relation.target_id,
                owner="SemanticRelation.target_id",
            )

        # Attribution.
        for attribution in self.attributions:
            require_entity_id(
                attribution.source_entity_id,
                owner=(
                    f"Attribution "
                    f"{attribution.semantic_id!r}"
                ),
            )
            require_semantic_id(
                attribution.target_id,
                owner=(
                    f"Attribution "
                    f"{attribution.semantic_id!r}"
                ),
            )

        # Scope.
        for operator in self.scope_operators:
            require_semantic_id(
                operator.target_id,
                owner=(
                    f"ScopeOperator "
                    f"{operator.operator_id!r}"
                ),
            )

        # Quantifiers.
        for quantifier in self.quantifiers:
            require_semantic_id(
                quantifier.target_id,
                owner=(
                    f"Quantifier "
                    f"{quantifier.operator_id!r}"
                ),
            )

            for entity_id in quantifier.exception_entity_ids:
                require_entity_id(
                    entity_id,
                    owner=(
                        f"Quantifier "
                        f"{quantifier.operator_id!r}"
                    ),
                )

        # Comparisons.
        for comparison in self.comparisons:
            validate_semantic_value(
                comparison.left,
                owner=(
                    f"Comparison "
                    f"{comparison.semantic_id!r}.left"
                ),
            )
            validate_semantic_value(
                comparison.right,
                owner=(
                    f"Comparison "
                    f"{comparison.semantic_id!r}.right"
                ),
            )

        # Explicit alternatives.
        for group in self.alternative_groups:
            for member_id in group.member_ids:
                require_semantic_id(
                    member_id,
                    owner=(
                        f"AlternativeGroup "
                        f"{group.semantic_id!r}"
                    ),
                )

        # Evidence.
        for evidence in self.evidence:
            register_unique(
                evidence.evidence_id,
                evidence_ids,
                label="evidence_id",
            )

            if evidence.source_entity_id is not None:
                require_entity_id(
                    evidence.source_entity_id,
                    owner=(
                        f"Evidence "
                        f"{evidence.evidence_id!r}"
                    ),
                )

        for relation in self.evidence_relations:
            if relation.evidence_id not in evidence_ids:
                raise ValueError(
                    "EvidenceRelation references unknown "
                    f"evidence_id {relation.evidence_id!r}"
                )

            require_semantic_id(
                relation.target_id,
                owner="EvidenceRelation.target_id",
            )

        # Discourse references.
        for reference in self.references:

            candidate_ids = reference.candidate_entity_ids

            if len(candidate_ids) != len(set(candidate_ids)):
                raise ValueError(
                    f"DiscourseReference "
                    f"{reference.reference_id!r} "
                    "contains duplicate candidate entity IDs"
                )

            for candidate_id in candidate_ids:
                require_entity_id(
                    candidate_id,
                    owner=(
                        f"DiscourseReference "
                        f"{reference.reference_id!r}"
                    ),
                )

            if reference.status == ReferenceStatus.RESOLVED:
                if reference.resolved_entity_id is None:
                    raise ValueError(
                        f"Resolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "requires resolved_entity_id"
                    )

                require_entity_id(
                    reference.resolved_entity_id,
                    owner=(
                        f"Resolved DiscourseReference "
                        f"{reference.reference_id!r}"
                    ),
                )

                if (
                    reference.resolved_entity_id
                    not in candidate_ids
                ):
                    raise ValueError(
                        f"Resolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "must resolve to one of its candidates"
                    )

            elif reference.status == ReferenceStatus.AMBIGUOUS:
                if reference.resolved_entity_id is not None:
                    raise ValueError(
                        f"Ambiguous DiscourseReference "
                        f"{reference.reference_id!r} "
                        "cannot have resolved_entity_id"
                    )

                if len(candidate_ids) < 2:
                    raise ValueError(
                        f"Ambiguous DiscourseReference "
                        f"{reference.reference_id!r} "
                        "requires at least two candidates"
                    )

            elif reference.status == ReferenceStatus.UNRESOLVED:
                if reference.resolved_entity_id is not None:
                    raise ValueError(
                        f"Unresolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "cannot have resolved_entity_id"
                    )

        # Same-turn revisions.
        for revision in self.revisions:
            require_semantic_id(
                revision.target_id,
                owner=(
                    f"DiscourseRevision "
                    f"{revision.revision_id!r}"
                ),
            )

            if revision.replacement_id is not None:
                require_semantic_id(
                    revision.replacement_id,
                    owner=(
                        f"DiscourseRevision "
                        f"{revision.revision_id!r}"
                    ),
                )

        # Ellipsis.
        for ellipsis in self.ellipsis_resolutions:
            for antecedent_id in ellipsis.antecedent_ids:
                require_semantic_id(
                    antecedent_id,
                    owner=(
                        f"EllipsisResolution "
                        f"{ellipsis.ellipsis_id!r}"
                    ),
                )

            if ellipsis.resolved_semantic_id is not None:
                require_semantic_id(
                    ellipsis.resolved_semantic_id,
                    owner=(
                        f"EllipsisResolution "
                        f"{ellipsis.ellipsis_id!r}"
                    ),
                )

        return self
