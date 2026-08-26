import pytest
from pydantic import ValidationError

from celeste.cognition.models import (
    Certainty,
    Claim,
    EntityReference,
    EntityType,
    EventCandidate,
    EventParticipant,
    SpeechAct,
    SpeechActType,
    TurnUnderstanding,
)


def test_entity_reference_requires_identifier():
    with pytest.raises(ValidationError):
        EntityReference()


def test_claim_requires_object_or_value():
    with pytest.raises(ValidationError):
        Claim(
            subject=EntityReference(name="Laura"),
            predicate="lives_in",
            certainty=Certainty.ASSERTED,
        )


def test_claim_with_entity_object_is_valid():
    claim = Claim(
        subject=EntityReference(name="Laura"),
        predicate="lives_in",
        object_entity=EntityReference(name="Alicante"),
        certainty=Certainty.ASSERTED,
        confidence=0.98,
    )

    assert claim.subject.name == "Laura"
    assert claim.object_entity is not None
    assert claim.object_entity.name == "Alicante"


def test_relationship_end_can_be_expressed_without_database_ids():
    event = EventCandidate(
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
                    surface_text="mi novia",
                    confidence=0.97,
                )
            ),
        ],
        certainty=Certainty.ASSERTED,
        confidence=0.97,
    )

    assert event.participants[1].entity.known_entity_id is None
    assert (
        event.participants[1].entity.contextual_role
        == "current_romantic_partner"
    )


def test_turn_can_contain_multiple_speech_acts():
    result = TurnUnderstanding(
        speech_acts=[
            SpeechAct(type=SpeechActType.INFORM),
            SpeechAct(type=SpeechActType.ASK),
        ],
        overall_confidence=0.99,
    )

    assert len(result.speech_acts) == 2
    assert result.speech_acts[0].type == SpeechActType.INFORM
    assert result.speech_acts[1].type == SpeechActType.ASK
