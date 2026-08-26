from celeste.cognition.grounding import SemanticGrounder
from celeste.cognition.models import (
    Certainty,
    EntityMention,
    EntityReference,
    EventCandidate,
    EventParticipant,
    ReferenceKind,
    TurnUnderstanding,
)


def test_rejects_invented_entity_mention():
    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="mi novia",
                reference=EntityReference(
                    surface_text="mi novia",
                    reference_kind=ReferenceKind.CONTEXTUAL_PERSON,
                ),
            )
        ]
    )

    result = SemanticGrounder().ground(
        message="Luego ella me escribió.",
        understanding=understanding,
    )

    assert result.understanding.entities == []
    assert len(result.issues) == 1
    assert result.issues[0].rejected_text == "mi novia"


def test_keeps_real_contextual_reference():
    understanding = TurnUnderstanding(
        entities=[
            EntityMention(
                surface_text="ella",
                reference=EntityReference(
                    surface_text="ella",
                    reference_kind=ReferenceKind.CONTEXTUAL_PERSON,
                ),
            )
        ]
    )

    result = SemanticGrounder().ground(
        message="Luego ella me escribió.",
        understanding=understanding,
    )

    assert len(result.understanding.entities) == 1
    assert result.issues == []


def test_removes_invented_event_participant():
    understanding = TurnUnderstanding(
        events=[
            EventCandidate(
                event_type="sent_message",
                participants=[
                    EventParticipant(
                        entity=EntityReference(
                            surface_text="ella",
                            reference_kind=(
                                ReferenceKind.CONTEXTUAL_PERSON
                            ),
                        ),
                        role="sender",
                    ),
                    EventParticipant(
                        entity=EntityReference(
                            surface_text="mi novia",
                            reference_kind=(
                                ReferenceKind.CONTEXTUAL_PERSON
                            ),
                        ),
                        role="recipient",
                    ),
                ],
                certainty=Certainty.ASSERTED,
            )
        ]
    )

    result = SemanticGrounder().ground(
        message="Luego ella me escribió.",
        understanding=understanding,
    )

    participants = result.understanding.events[0].participants

    assert len(participants) == 1
    assert participants[0].entity.surface_text == "ella"

    assert any(
        issue.rejected_text == "mi novia"
        for issue in result.issues
    )