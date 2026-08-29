from __future__ import annotations

from typing import TypeVar

import pytest
from pydantic import BaseModel

from celeste.cognition.interpretation import (
    AttributionType,
    Polarity,
    PropositionMode,
    ReferenceStatus,
    SituationKind,
)
from celeste.cognition.raw_interpretation import (
    RawAttribution,
    RawEntity,
    RawEvent,
    RawInterpretation,
    RawParticipant,
    RawPolarity,
    RawProposition,
    RawPropositionMode,
    RawReference,
    RawRevision,
    RawState,
)
from celeste.cognition.understanding import (
    UNDERSTANDING_SYSTEM_PROMPT,
    Understanding,
)
from celeste.providers.base import LLMProvider


T = TypeVar(
    "T",
    bound=BaseModel,
)


class StubProvider(LLMProvider):
    """
    Controlled provider for unit tests.

    It behaves like an LLM provider but always returns the
    RawInterpretation supplied by the test.
    """

    def __init__(
        self,
        response: BaseModel,
    ) -> None:
        self.response = response

        self.last_system_prompt: str | None = None
        self.last_user_prompt: str | None = None
        self.last_response_model: type[BaseModel] | None = None

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        self.last_response_model = response_model

        return response_model.model_validate(
            self.response.model_dump()
        )


@pytest.mark.asyncio
async def test_understanding_converts_raw_event_to_interpretation():
    provider = StubProvider(
        RawInterpretation(
            entities=[
                RawEntity(
                    temp_id="laura",
                    mention="Laura",
                    canonical_name="Laura",
                    semantic_type="person",
                )
            ],
            situations=[
                RawEvent(
                    temp_id="come1",
                    semantic_type="come",
                    participants=[
                        RawParticipant(
                            entity_temp_id="laura",
                            role="agent",
                        )
                    ],
                )
            ],
        )
    )

    understanding = Understanding(provider)

    result = await understanding.interpret(
        "Laura viene."
    )

    assert len(result.entities) == 1
    assert len(result.situations) == 1

    assert (
        result.situations[0].kind
        == SituationKind.EVENT
    )

    assert (
        result.situations[0].participants[0].entity_id
        == "entity_laura"
    )


@pytest.mark.asyncio
async def test_understanding_preserves_belief_as_proposition():
    provider = StubProvider(
        RawInterpretation(
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
                    canonical_name="Marta",
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
    )

    result = await Understanding(
        provider
    ).interpret(
        "Creo que Marta está enfadada."
    )

    assert len(result.propositions) == 1

    assert (
        result.propositions[0].mode
        == PropositionMode.BELIEF
    )

    assert (
        result.propositions[0].holder_entity_id
        == "entity_user"
    )


@pytest.mark.asyncio
async def test_understanding_preserves_relational_emotion_target():
    provider = StubProvider(
        RawInterpretation(
            entities=[
                RawEntity(
                    temp_id="user",
                    mention="conmigo",
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
                    value="angry",
                    participants=[
                        RawParticipant(
                            entity_temp_id="marta",
                            role="experiencer",
                        ),
                        RawParticipant(
                            entity_temp_id="user",
                            role="target",
                        ),
                    ],
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
    )

    result = await Understanding(provider).interpret(
        "Creo que Marta est\u00e1 enfadada conmigo."
    )

    situation = result.propositions[0].content.situation

    assert situation is not None
    assert {
        (participant.role, participant.entity_id)
        for participant in situation.participants
    } == {
        ("experiencer", "entity_marta"),
        ("target", "entity_user"),
    }


@pytest.mark.asyncio
async def test_understanding_preserves_reported_speech_as_attribution():
    provider = StubProvider(
        RawInterpretation(
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
            situations=[
                RawEvent(
                    temp_id="come1",
                    semantic_type="come",
                    participants=[
                        RawParticipant(
                            entity_temp_id="marta",
                            role="agent",
                        )
                    ],
                )
            ],
            attributions=[
                RawAttribution(
                    temp_id="report1",
                    source_entity_temp_id="laura",
                    relation="reports",
                    target_id="come1",
                )
            ],
        )
    )

    result = await Understanding(provider).interpret(
        "Laura dijo que Marta vendr\u00e1 ma\u00f1ana."
    )

    assert result.propositions == []
    assert len(result.attributions) == 1
    assert (
        result.attributions[0].relation
        == AttributionType.REPORTS
    )
    assert (
        result.attributions[0].source_entity_id
        == "entity_laura"
    )
    assert (
        result.attributions[0].target_id
        == "event_come1"
    )


@pytest.mark.asyncio
async def test_understanding_preserves_negated_intention():
    provider = StubProvider(
        RawInterpretation(
            entities=[
                RawEntity(
                    temp_id="user",
                    mention="yo",
                    semantic_type="person",
                    identity_hint="user",
                )
            ],
            situations=[
                RawEvent(
                    temp_id="leave",
                    semantic_type="leave_job",
                    participants=[
                        RawParticipant(
                            entity_temp_id="user",
                            role="agent",
                        )
                    ],
                )
            ],
            propositions=[
                RawProposition(
                    temp_id="intention",
                    mode=RawPropositionMode.INTENTION,
                    holder_entity_temp_id="user",
                    target_id="leave",
                    polarity=RawPolarity.NEGATIVE,
                )
            ],
        )
    )

    result = await Understanding(
        provider
    ).interpret(
        "No quiero dejar el trabajo."
    )

    assert (
        result.propositions[0].mode
        == PropositionMode.INTENTION
    )

    assert (
        result.propositions[0].polarity
        == Polarity.NEGATIVE
    )


@pytest.mark.asyncio
async def test_understanding_preserves_ambiguous_reference():
    provider = StubProvider(
        RawInterpretation(
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
    )

    result = await Understanding(
        provider
    ).interpret(
        "Laura habló con Marta y ella se fue."
    )

    assert len(result.references) == 1

    assert (
        result.references[0].status
        == ReferenceStatus.AMBIGUOUS
    )

    assert set(
        result.references[0].candidate_entity_ids
    ) == {
        "entity_laura",
        "entity_marta",
    }


@pytest.mark.asyncio
async def test_understanding_preserves_same_turn_correction():
    provider = StubProvider(
        RawInterpretation(
            situations=[
                RawState(
                    temp_id="madrid",
                    semantic_type="destination",
                    value="Madrid",
                    participants=[],
                ),
                RawState(
                    temp_id="getafe",
                    semantic_type="destination",
                    value="Getafe",
                    participants=[],
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
    )

    result = await Understanding(
        provider
    ).interpret(
        "Me voy a Madrid... perdón, a Getafe."
    )

    assert len(result.revisions) == 1

    assert (
        result.revisions[0].target_id
        == "state_madrid"
    )

    assert (
        result.revisions[0].replacement_id
        == "state_getafe"
    )


@pytest.mark.asyncio
async def test_understanding_sends_raw_schema_to_provider():
    provider = StubProvider(
        RawInterpretation()
    )

    understanding = Understanding(provider)

    await understanding.interpret(
        "Hola."
    )

    assert (
        provider.last_response_model
        is RawInterpretation
    )

    assert (
        provider.last_system_prompt
        == UNDERSTANDING_SYSTEM_PROMPT
    )

    assert provider.last_user_prompt == "Hola."


@pytest.mark.asyncio
async def test_understanding_rejects_empty_input():
    provider = StubProvider(
        RawInterpretation()
    )

    understanding = Understanding(provider)

    with pytest.raises(
        ValueError,
        match="empty utterance",
    ):
        await understanding.interpret("   ")
