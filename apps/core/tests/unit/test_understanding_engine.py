import pytest

from celeste.cognition.models import (
    Certainty,
    EventCandidate,
    EventParticipant,
    EntityReference,
    TurnUnderstanding,
)
from celeste.cognition.understanding import UnderstandingEngine
from celeste.providers.fake import FakeLLMProvider


@pytest.mark.asyncio
async def test_understanding_engine_returns_structured_result():
    expected = TurnUnderstanding(
        events=[
            EventCandidate(
                event_type="relationship_ended",
                participants=[
                    EventParticipant(
                        entity=EntityReference(
                            contextual_role="user",
                        )
                    ),
                    EventParticipant(
                        entity=EntityReference(
                            contextual_role="current_romantic_partner",
                        )
                    ),
                ],
                certainty=Certainty.ASSERTED,
                confidence=0.97,
            )
        ],
        requires_context_resolution=True,
        overall_confidence=0.97,
    )

    provider = FakeLLMProvider(expected)
    engine = UnderstandingEngine(provider)

    result = await engine.understand(
        "Al final lo hemos dejado.",
        context="The user currently has a romantic partner.",
    )

    assert result == expected
    assert result.events[0].event_type == "relationship_ended"

    assert provider.last_user_prompt is not None
    assert "Al final lo hemos dejado." in provider.last_user_prompt


@pytest.mark.asyncio
async def test_understanding_engine_rejects_empty_messages():
    provider = FakeLLMProvider(TurnUnderstanding())
    engine = UnderstandingEngine(provider)

    with pytest.raises(ValueError):
        await engine.understand("   ")
