from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


class RawPropositionMode(StrEnum):
    BELIEF = "belief"
    HYPOTHESIS = "hypothesis"
    INTENTION = "intention"
    DESIRE = "desire"
    PREFERENCE = "preference"
    OPINION = "opinion"
    POSSIBILITY = "possibility"
    KNOWLEDGE = "knowledge"


class RawPolarity(StrEnum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class RawCertainty(StrEnum):
    ASSERTED = "asserted"
    INFERRED = "inferred"
    UNCERTAIN = "uncertain"


class RawRealityStatus(StrEnum):
    ACTUAL = "actual"
    HYPOTHETICAL = "hypothetical"
    COUNTERFACTUAL = "counterfactual"


class RawCommunicativeAct(StrEnum):
    ASSERT = "assert"
    ASK = "ask"
    REQUEST = "request"
    CORRECT = "correct"
    CONFIRM = "confirm"
    DENY = "deny"
    EXPRESS = "express"
    SPECULATE = "speculate"


class RawAttributionType(StrEnum):
    ASSERTS = "asserts"
    REPORTS = "reports"


class RawRevisionType(StrEnum):
    CORRECTION = "correction"
    RETRACTION = "retraction"
    REFORMULATION = "reformulation"


class RawSemanticRelationType(StrEnum):
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

class RawScopeOperatorType(StrEnum):
    NEGATION = "negation"
    EXCLUSIVITY = "exclusivity"

class RawParticipantRole(StrEnum):
    AGENT = "agent"
    EXPERIENCER = "experiencer"
    PATIENT = "patient"
    THEME = "theme"
    RECIPIENT = "recipient"
    TARGET = "target"
    SOURCE = "source"
    DESTINATION = "destination"
    LOCATION = "location"
    INSTRUMENT = "instrument"

class RawParticipant(BaseModel):
    role: RawParticipantRole

    entity_temp_id: str | None = None
    reference_temp_id: str | None = None

    @model_validator(mode="after")
    def validate_target(self) -> "RawParticipant":
        targets = sum(
            value is not None
            for value in (
                self.entity_temp_id,
                self.reference_temp_id,
            )
        )

        if targets != 1:
            raise ValueError(
                "RawParticipant requires exactly one of "
                "entity_temp_id or reference_temp_id"
            )

        return self

class RawEntity(BaseModel):
    temp_id: str

    mention: str

    canonical_name: str | None = None

    semantic_type: str | None = None

    identity_hint: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class RawTemporalMeaning(BaseModel):
    frame: Literal[
        "past",
        "present",
        "future",
        "unknown",
    ] = "unknown"

    expression: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class RawSituationKind(StrEnum):
    EVENT = "event"
    STATE = "state"
    TRANSITION = "transition"


class RawSituation(BaseModel):
    temp_id: str

    kind: RawSituationKind | None = None

    semantic_type: str | None = None

    semantic_state: str | None = None

    transition: Literal[
        "start",
        "end",
        "resume",
        "pause",
        "change",
        "continue",
        "cancel",
    ] | None = None

    participants: list[RawParticipant]

    value: str | int | float | bool | None = None

    previous_value: str | int | float | bool | None = None

    new_value: str | int | float | bool | None = None

    temporal: RawTemporalMeaning | None = None

    polarity: RawPolarity = RawPolarity.POSITIVE

    reality: RawRealityStatus = RawRealityStatus.ACTUAL

    certainty: RawCertainty = RawCertainty.ASSERTED

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema,
        handler,
    ):
        """
        Require critical semantic decisions from the LLM while
        keeping Python construction forgiving through defaults.
        """
        schema = handler(core_schema)
        required = schema.setdefault("required", [])

        for field_name in (
            "polarity",
            "reality",
            "certainty",
        ):
            if field_name not in required:
                required.append(field_name)

        return schema

    @model_validator(mode="after")
    def infer_kind(self) -> "RawSituation":
        if self.kind is not None:
            return self

        if self.transition is not None:
            self.kind = RawSituationKind.TRANSITION

        elif self.value is not None:
            self.kind = RawSituationKind.STATE

        else:
            self.kind = RawSituationKind.EVENT

        return self

class RawEvent(RawSituation):
    kind: RawSituationKind = RawSituationKind.EVENT


class RawState(RawSituation):
    kind: RawSituationKind = RawSituationKind.STATE


class RawTransition(RawSituation):
    kind: RawSituationKind = RawSituationKind.TRANSITION

class RawProposition(BaseModel):
    temp_id: str

    mode: RawPropositionMode

    holder_entity_temp_id: str

    target_id: str

    polarity: RawPolarity = RawPolarity.POSITIVE

    certainty: RawCertainty = RawCertainty.ASSERTED

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema,
        handler,
    ):
        """
        Require critical semantic decisions from the LLM while
        keeping Python construction forgiving through defaults.
        """
        schema = handler(core_schema)
        required = schema.setdefault("required", [])

        for field_name in (
            "polarity",
            "certainty",
        ):
            if field_name not in required:
                required.append(field_name)

        return schema


class RawAttribution(BaseModel):
    temp_id: str

    source_entity_temp_id: str

    relation: RawAttributionType

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class RawReference(BaseModel):
    temp_id: str

    text: str

    candidate_entity_temp_ids: list[str] = Field(
        default_factory=list
    )

    resolved_entity_temp_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class RawRevision(BaseModel):
    temp_id: str

    revision: RawRevisionType

    target_id: str

    replacement_id: str | None = None

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


class RawSemanticRelation(BaseModel):
    source_id: str

    relation: RawSemanticRelationType

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class RawSemanticContentLink(BaseModel):
    source_id: str

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class RawScopeOperator(BaseModel):
    temp_id: str

    operator: RawScopeOperatorType

    target_id: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

class RawDiscourseMeaning(BaseModel):
    acts: list[RawCommunicativeAct] = Field(
        default_factory=list
    )

    literal_meaning: str | None = None

    intended_meaning: str | None = None

    intended_meaning_confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema,
        handler,
    ):
        schema = handler(core_schema)
        required = schema.setdefault("required", [])
        if "acts" not in required:
            required.append("acts")
        return schema


class RawInterpretation(BaseModel):
    discourse: RawDiscourseMeaning = Field(
        default_factory=RawDiscourseMeaning
    )

    entities: list[RawEntity] = Field(
        default_factory=list
    )

    situations: list[RawSituation] = Field(
        default_factory=list
    )

    propositions: list[RawProposition] = Field(
        default_factory=list
    )

    attributions: list[RawAttribution] = Field(
        default_factory=list
    )

    references: list[RawReference] = Field(
        default_factory=list
    )

    revisions: list[RawRevision] = Field(
        default_factory=list
    )

    semantic_relations: list[
        RawSemanticRelation
    ] = Field(
        default_factory=list
    )

    semantic_content_links: list[
        RawSemanticContentLink
    ] = Field(
        default_factory=list
    )

    scope_operators: list[
        RawScopeOperator
    ] = Field(
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

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema,
        handler,
    ):
        """Require discourse acts from LLMs while keeping Python construction forgiving."""
        schema = handler(core_schema)
        required = schema.setdefault("required", [])
        if "discourse" not in required:
            required.append("discourse")

        return schema

    @model_validator(mode="before")
    @classmethod
    def repair_raw_input(
        cls,
        data,
    ):
        if not isinstance(data, dict):
            return data

        data = dict(data)

        def as_dict(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump(
                    mode="python"
                )

            if isinstance(obj, dict):
                return dict(obj)

            return obj

        # Convert nested Pydantic objects to dictionaries too.
        # This makes the repair behave identically whether input
        # comes from Qwen JSON or directly from Python tests.
        entities = [
            as_dict(item)
            for item in (
                data.get("entities") or []
            )
        ]

        references = [
            as_dict(item)
            for item in (
                data.get("references") or []
            )
        ]

        situations = [
            as_dict(item)
            for item in (
                data.get("situations") or []
            )
        ]

        propositions = [
            as_dict(item)
            for item in (
                data.get("propositions") or []
            )
        ]

        attributions = [
            as_dict(item)
            for item in (
                data.get("attributions") or []
            )
        ]

        entity_ids = {
            entity.get("temp_id")
            for entity in entities
            if isinstance(entity, dict)
        }

        reference_ids = {
            reference.get("temp_id")
            for reference in references
            if isinstance(reference, dict)
        }

        user_is_referenced = False

        repaired_situations = []

        for situation in situations:
            if not isinstance(
                situation,
                dict,
            ):
                repaired_situations.append(
                    situation
                )
                continue

            situation = dict(situation)

            participants = [
                as_dict(item)
                for item in (
                    situation.get(
                        "participants"
                    )
                    or []
                )
            ]

            repaired_participants = []

            for participant in participants:
                if not isinstance(
                    participant,
                    dict,
                ):
                    repaired_participants.append(
                        participant
                    )
                    continue

                participant = dict(
                    participant
                )

                entity_temp_id = (
                    participant.get(
                        "entity_temp_id"
                    )
                )

                reference_temp_id = (
                    participant.get(
                        "reference_temp_id"
                    )
                )

                # The model put an entity ID in the
                # reference field.
                if (
                    reference_temp_id
                    is not None
                    and reference_temp_id
                    in entity_ids
                    and reference_temp_id
                    not in reference_ids
                ):
                    participant[
                        "entity_temp_id"
                    ] = reference_temp_id

                    participant[
                        "reference_temp_id"
                    ] = None

                    entity_temp_id = (
                        reference_temp_id
                    )

                    reference_temp_id = None

                # The model put a reference ID in the
                # entity field.
                elif (
                    entity_temp_id
                    is not None
                    and entity_temp_id
                    in reference_ids
                    and entity_temp_id
                    not in entity_ids
                ):
                    participant[
                        "reference_temp_id"
                    ] = entity_temp_id

                    participant[
                        "entity_temp_id"
                    ] = None

                    reference_temp_id = (
                        entity_temp_id
                    )

                    entity_temp_id = None

                if entity_temp_id == "user":
                    user_is_referenced = True

                # A participant with no target carries no usable
                # semantic information. Drop it instead of inventing
                # an entity or reference to satisfy the graph.
                if (
                    entity_temp_id is None
                    and reference_temp_id is None
                ):
                    continue

                repaired_participants.append(
                    participant
                )

            situation[
                "participants"
            ] = repaired_participants

            repaired_situations.append(
                situation
            )

        # Explicit mental attitude holder.
        for proposition in propositions:
            if (
                isinstance(
                    proposition,
                    dict,
                )
                and proposition.get(
                    "holder_entity_temp_id"
                )
                == "user"
            ):
                user_is_referenced = True

        # Explicit attribution source.
        for attribution in attributions:
            if (
                isinstance(
                    attribution,
                    dict,
                )
                and attribution.get(
                    "source_entity_temp_id"
                )
                == "user"
            ):
                user_is_referenced = True

        # User may also appear inside a discourse reference.
        for reference in references:
            if not isinstance(
                reference,
                dict,
            ):
                continue

            if (
                "user"
                in (
                    reference.get(
                        "candidate_entity_temp_ids"
                    )
                    or []
                )
            ):
                user_is_referenced = True

            if (
                reference.get(
                    "resolved_entity_temp_id"
                )
                == "user"
            ):
                user_is_referenced = True

        # "user" is a reserved turn-local identity.
        # If Qwen refers to it, Python can safely materialize it.
        if (
            user_is_referenced
            and "user"
            not in entity_ids
        ):
            entities.insert(
                0,
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "canonical_name": None,
                    "semantic_type": "person",
                    "identity_hint": "user",
                    "confidence": 1.0,
                },
            )

        data["entities"] = entities
        data["references"] = references
        data["situations"] = (
            repaired_situations
        )
        data["propositions"] = propositions
        data["attributions"] = attributions

        return data

    @model_validator(mode="after")
    def validate_raw_graph(
        self,
    ) -> "RawInterpretation":
        node_ids: set[str] = set()
        entity_ids: set[str] = set()
        semantic_ids: set[str] = set()
        reference_ids: set[str] = set()

        def register_node(
            value: str,
        ) -> None:
            if value in node_ids:
                raise ValueError(
                    f"Duplicate raw temp_id {value!r}"
                )

            node_ids.add(value)

        for reference in self.references:
            register_node(reference.temp_id)
            reference_ids.add(reference.temp_id)

        for entity in self.entities:
            register_node(entity.temp_id)
            entity_ids.add(entity.temp_id)

        for situation in self.situations:
            register_node(situation.temp_id)
            semantic_ids.add(situation.temp_id)

        for proposition in self.propositions:
            register_node(proposition.temp_id)
            semantic_ids.add(proposition.temp_id)

        for attribution in self.attributions:
            register_node(attribution.temp_id)
            semantic_ids.add(attribution.temp_id)

        for revision in self.revisions:
            register_node(revision.temp_id)

        for operator in self.scope_operators:
            register_node(operator.temp_id)

        for situation in self.situations:
            for participant in situation.participants:
                if participant.entity_temp_id is not None:
                    if (
                        participant.entity_temp_id
                        not in entity_ids
                    ):
                        raise ValueError(
                            "Raw participant references "
                            "unknown entity temp_id "
                            f"{participant.entity_temp_id!r}"
                        )

                elif participant.reference_temp_id is not None:
                    if (
                        participant.reference_temp_id
                        not in reference_ids
                    ):
                        raise ValueError(
                            "Raw participant references "
                            "unknown reference temp_id "
                            f"{participant.reference_temp_id!r}"
                        )

        for proposition in self.propositions:
            if (
                proposition.holder_entity_temp_id
                not in entity_ids
            ):
                raise ValueError(
                    "Raw proposition references unknown "
                    "holder entity temp_id "
                    f"{proposition.holder_entity_temp_id!r}"
                )

            if proposition.target_id not in semantic_ids:
                raise ValueError(
                    "Raw proposition references unknown "
                    "semantic target "
                    f"{proposition.target_id!r}"
                )

            if (
                proposition.target_id
                == proposition.temp_id
            ):
                raise ValueError(
                    "Raw proposition cannot target itself"
                )

        for attribution in self.attributions:
            if (
                attribution.source_entity_temp_id
                not in entity_ids
            ):
                raise ValueError(
                    "Raw attribution references unknown "
                    "source entity temp_id "
                    f"{attribution.source_entity_temp_id!r}"
                )

            if attribution.target_id not in semantic_ids:
                raise ValueError(
                    "Raw attribution references unknown "
                    "semantic target "
                    f"{attribution.target_id!r}"
                )

        for reference in self.references:
            for candidate_id in (
                reference.candidate_entity_temp_ids
            ):
                if candidate_id not in entity_ids:
                    raise ValueError(
                        "Raw reference candidate "
                        "does not exist: "
                        f"{candidate_id!r}"
                    )

            if (
                reference.resolved_entity_temp_id
                is not None
                and
                reference.resolved_entity_temp_id
                not in entity_ids
            ):
                raise ValueError(
                    "Raw resolved reference points to "
                    "unknown entity temp_id "
                    f"{reference.resolved_entity_temp_id!r}"
                )

        for revision in self.revisions:
            if revision.target_id not in semantic_ids:
                raise ValueError(
                    "Raw revision references unknown "
                    "semantic target "
                    f"{revision.target_id!r}"
                )

            if (
                revision.replacement_id is not None
                and revision.replacement_id
                not in semantic_ids
            ):
                raise ValueError(
                    "Raw revision replacement references "
                    "unknown semantic target "
                    f"{revision.replacement_id!r}"
                )

        for relation in self.semantic_relations:
            if relation.source_id not in semantic_ids:
                raise ValueError(
                    "Raw semantic relation references "
                    "unknown source "
                    f"{relation.source_id!r}"
                )

            if relation.target_id not in semantic_ids:
                raise ValueError(
                    "Raw semantic relation references "
                    "unknown target "
                    f"{relation.target_id!r}"
                )

        for link in self.semantic_content_links:
            if link.source_id not in semantic_ids:
                raise ValueError(
                    "Raw semantic content link references "
                    "unknown source "
                    f"{link.source_id!r}"
                )

            if link.target_id not in semantic_ids:
                raise ValueError(
                    "Raw semantic content link references "
                    "unknown target "
                    f"{link.target_id!r}"
                )

        for operator in self.scope_operators:
            if operator.target_id not in semantic_ids:
                raise ValueError(
                    "Raw scope operator references "
                    "unknown semantic target "
                    f"{operator.target_id!r}"
                )

        return self
