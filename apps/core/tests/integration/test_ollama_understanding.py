import pytest

from celeste.cognition.models import Certainty, SpeechActType
from celeste.cognition.understanding import UnderstandingEngine
from celeste.providers.ollama import OllamaProvider


@pytest.fixture
def engine() -> UnderstandingEngine:
    provider = OllamaProvider(
        model="qwen3.5:9b",
        think=False,
        temperature=0.0,
    )
    return UnderstandingEngine(provider)


@pytest.mark.asyncio
async def test_ollama_understands_relationship_end(
    engine: UnderstandingEngine,
):
    result = await engine.understand(
        "Al final lo hemos dejado.",
        context=(
            "The user currently has a romantic partner named Laura."
        ),
    )

    print()
    print(result.model_dump_json(indent=2))

    assert len(result.events) == 1

    event = result.events[0]

    assert event.certainty == Certainty.ASSERTED

    participant_refs = [
    (p.entity.name or p.entity.contextual_role or "").lower()
    for p in event.participants
    ]

    assert "user" in participant_refs

    assert any(
        value in {
            "laura",
            "current_romantic_partner",
            "romantic_partner",
        }
        for value in participant_refs
    )

@pytest.mark.asyncio
async def test_ollama_does_not_turn_intention_into_breakup(
    engine: UnderstandingEngine,
):
    result = await engine.understand(
        "Estoy pensando en dejar a Laura.",
        context=(
            "Laura is the user's current romantic partner."
        ),
    )

    print()
    print(result.model_dump_json(indent=2))

    completed_breakup_events = [
        event
        for event in result.events
        if event.event_type in {
            "relationship_ended",
            "relationship_status_change",
        }
        and event.state_change in {
            "ended",
            "terminated",
        }
    ]

    assert completed_breakup_events == []


@pytest.mark.asyncio
async def test_ollama_distinguishes_correction_from_move(
    engine: UnderstandingEngine,
):
    correction = await engine.understand(
        (
            "Antes te dije que Laura vivía en Madrid, "
            "pero me equivoqué. Vive en Getafe."
        )
    )

    real_change = await engine.understand(
        "Laura se ha mudado de Madrid a Getafe."
    )

    print()
    print("CORRECTION")
    print(correction.model_dump_json(indent=2))
    print()
    print("REAL CHANGE")
    print(real_change.model_dump_json(indent=2))

    assert len(correction.corrections) >= 1

    assert len(real_change.corrections) == 0
    assert len(real_change.events) >= 1