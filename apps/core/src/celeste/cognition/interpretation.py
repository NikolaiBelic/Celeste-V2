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

class EntityMention(BaseModel):
    semantic_id: str

    text: str

    canonical_name: str | None = None

    semantic_type: str | None = None

    identity_hint: str | None = None

    qualifiers: dict[str, str] = Field(
        default_factory=dict
    )

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

SemanticValue = (
    str
    | int
    | float
    | bool
    | EntityMention
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
    """
    A speaker changes, retracts or reformulates semantic content
    inside the same turn.

    Examples:
    "Madrid... perdón, Getafe."
    "Quiero hacerlo... pensándolo mejor, no."
    """

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
    """
    Represents content omitted from the surface utterance but
    recoverable from material in the same turn.

    Example:
    "Fernando fue al bar y Marta también."

    "también" inherits semantic material from the first event.
    """

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
    entity: EntityMention

    role: str

class Evidence(BaseModel):
    """
    A perceptual or external signal available during interpretation.

    Evidence is not automatically a fact about the world.
    """

    evidence_id: str

    modality: EvidenceModality

    signal_type: str

    value: str

    source: EntityMention | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class EvidenceRelation(BaseModel):
    """
    Connects evidence to a semantic interpretation.

    Example:
    an audio signal may suggest distress without proving it.
    """

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
    reality: RealityStatus = RealityStatus.ACTUAL

    kind: Literal[SituationKind.EVENT] = (
        SituationKind.EVENT
    )

    semantic_type: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    temporal: TemporalMeaning | None = None

    polarity: Polarity = Polarity.POSITIVE

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
    reality: RealityStatus = RealityStatus.ACTUAL

    kind: Literal[SituationKind.STATE] = (
        SituationKind.STATE
    )

    semantic_type: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    value: SemanticValue = None

    temporal: TemporalMeaning | None = None

    polarity: Polarity = Polarity.POSITIVE

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
    reality: RealityStatus = RealityStatus.ACTUAL

    kind: Literal[SituationKind.TRANSITION] = (
        SituationKind.TRANSITION
    )

    transition: TransitionKind

    semantic_state: str

    participants: list[Participant] = Field(
        default_factory=list
    )

    previous_value: SemanticValue = None
    new_value: SemanticValue = None

    temporal: TemporalMeaning | None = None

    polarity: Polarity = Polarity.POSITIVE

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

    subject: EntityMention

    predicate: str

    object: SemanticValue = None

    polarity: Polarity = Polarity.POSITIVE


class SituationContent(BaseModel):
    kind: Literal["situation"] = "situation"

    situation: Situation

class PropositionReferenceContent(BaseModel):
    """
    Allows a proposition to take another semantic node
    as its content without duplicating that node.

    Example:
    Marta believes [Fernando knows X].
    """

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

    holder: EntityMention

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
    """
    A semantic connection between meanings in the same turn.

    source_id and target_id refer only to semantic nodes from
    this interpretation. They are not persistent memory IDs.
    """

    source_id: str

    relation: SemanticRelationType

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class Attribution(BaseModel):
    """
    Describes who is the source of some semantic content.

    It has its own semantic_id because the attribution itself
    may be negated, qualified or otherwise scoped.

    Example:
    "Laura did not say X"

    The negation applies to Laura's reporting act,
    not necessarily to X.
    """

    semantic_id: str

    source: EntityMention

    relation: AttributionType

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class ScopeOperator(BaseModel):
    """
    An operator whose meaning applies to one specific
    semantic node.

    This preserves scope instead of flattening meanings.

    Examples:

    "Laura did not say X"
        NEGATION -> attribution

    "Laura said not X"
        NEGATION -> X
    """

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
    exceptions: list[EntityMention] = Field(default_factory=list)

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
    member_ids: list[str] = Field(min_length=2)
    exclusive: bool | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class InterpretationAlternative(BaseModel):
    """
    A plausible reading considered by Celeste.

    An alternative is not an assertion about reality.
    """

    description: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    evidence: list[str] = Field(
        default_factory=list
    )


class DiscourseMeaning(BaseModel):
    """
    What the speaker is doing by producing the utterance.
    """

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

    entities: list[EntityMention] = Field(
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
    def validate_semantic_graph(self) -> "Interpretation":
        semantic_ids: set[str] = set()

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

        # -------------------------------------------------
        # ENTITY IDS
        # -------------------------------------------------

        entity_ids: set[str] = set()

        for entity in self.entities:
            if entity.semantic_id in entity_ids:
                raise ValueError(
                    "Duplicate entity semantic_id "
                    f"{entity.semantic_id!r}"
                )

            entity_ids.add(entity.semantic_id)

        # -------------------------------------------------
        # SEMANTIC NODE IDS
        # -------------------------------------------------

        # Top-level situations.
        for situation in self.situations:
            register_semantic_id(
                situation.semantic_id,
                owner="Situation",
            )

        # Propositions.
        for proposition in self.propositions:
            register_semantic_id(
                proposition.semantic_id,
                owner="Proposition",
            )

        # Situations nested inside propositions are also
        # addressable semantic nodes.
        #
        # Do not treat an already registered nested ID as a
        # duplicate here because the same semantic content may
        # legitimately be reused by multiple propositions.
        for proposition in self.propositions:
            if isinstance(
                proposition.content,
                SituationContent,
            ):
                semantic_ids.add(
                    proposition.content.situation.semantic_id
                )

        # Attribution acts.
        for attribution in self.attributions:
            register_semantic_id(
                attribution.semantic_id,
                owner="Attribution",
            )

        # Comparisons.
        for comparison in self.comparisons:
            register_semantic_id(
                comparison.semantic_id,
                owner="Comparison",
            )

        # Explicit alternative groups.
        for group in self.alternative_groups:
            register_semantic_id(
                group.semantic_id,
                owner="AlternativeGroup",
            )

        def require_semantic_id(
            target_id: str,
            *,
            owner: str,
        ) -> None:
            if target_id not in semantic_ids:
                raise ValueError(
                    f"{owner} references unknown semantic_id "
                    f"{target_id!r}"
                )

        # -------------------------------------------------
        # PROPOSITION REFERENCES
        # -------------------------------------------------

        for proposition in self.propositions:
            if isinstance(
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

        # -------------------------------------------------
        # SEMANTIC RELATIONS
        # -------------------------------------------------

        for relation in self.semantic_relations:
            require_semantic_id(
                relation.source_id,
                owner="SemanticRelation.source_id",
            )

            require_semantic_id(
                relation.target_id,
                owner="SemanticRelation.target_id",
            )

        # -------------------------------------------------
        # ATTRIBUTIONS
        # -------------------------------------------------

        for attribution in self.attributions:
            require_semantic_id(
                attribution.target_id,
                owner=(
                    f"Attribution "
                    f"{attribution.semantic_id!r}"
                ),
            )

        # -------------------------------------------------
        # SCOPE
        # -------------------------------------------------

        for operator in self.scope_operators:
            require_semantic_id(
                operator.target_id,
                owner=(
                    f"ScopeOperator "
                    f"{operator.operator_id!r}"
                ),
            )

        # -------------------------------------------------
        # QUANTIFIERS
        # -------------------------------------------------

        for quantifier in self.quantifiers:
            require_semantic_id(
                quantifier.target_id,
                owner=(
                    f"Quantifier "
                    f"{quantifier.operator_id!r}"
                ),
            )

        # -------------------------------------------------
        # EXPLICIT ALTERNATIVES
        # -------------------------------------------------

        for group in self.alternative_groups:
            for member_id in group.member_ids:
                require_semantic_id(
                    member_id,
                    owner=(
                        f"AlternativeGroup "
                        f"{group.semantic_id!r}"
                    ),
                )

        # -------------------------------------------------
        # EVIDENCE
        # -------------------------------------------------

        evidence_ids: set[str] = set()

        for evidence in self.evidence:
            if evidence.evidence_id in evidence_ids:
                raise ValueError(
                    "Duplicate evidence_id "
                    f"{evidence.evidence_id!r}"
                )

            evidence_ids.add(evidence.evidence_id)

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

        # -------------------------------------------------
        # DISCOURSE REFERENCES
        # -------------------------------------------------

        reference_ids: set[str] = set()

        for reference in self.references:
            if reference.reference_id in reference_ids:
                raise ValueError(
                    "Duplicate reference_id "
                    f"{reference.reference_id!r}"
                )

            reference_ids.add(reference.reference_id)

            candidate_ids = (
                reference.candidate_entity_ids
            )

            if len(candidate_ids) != len(set(candidate_ids)):
                raise ValueError(
                    f"DiscourseReference "
                    f"{reference.reference_id!r} "
                    "contains duplicate candidate entity IDs"
                )

            for candidate_id in candidate_ids:
                if candidate_id not in entity_ids:
                    raise ValueError(
                        f"DiscourseReference "
                        f"{reference.reference_id!r} "
                        "references unknown entity "
                        f"{candidate_id!r}"
                    )

            if (
                reference.status
                == ReferenceStatus.RESOLVED
            ):
                if reference.resolved_entity_id is None:
                    raise ValueError(
                        f"Resolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "requires resolved_entity_id"
                    )

                if (
                    reference.resolved_entity_id
                    not in entity_ids
                ):
                    raise ValueError(
                        f"Resolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "references unknown resolved entity "
                        f"{reference.resolved_entity_id!r}"
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

            elif (
                reference.status
                == ReferenceStatus.AMBIGUOUS
            ):
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

            elif (
                reference.status
                == ReferenceStatus.UNRESOLVED
            ):
                if reference.resolved_entity_id is not None:
                    raise ValueError(
                        f"Unresolved DiscourseReference "
                        f"{reference.reference_id!r} "
                        "cannot have resolved_entity_id"
                    )

        # -------------------------------------------------
        # SAME-TURN REVISIONS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # ELLIPSIS
        # -------------------------------------------------

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