from __future__ import annotations

from pydantic import BaseModel, Field

from celeste.cognition.models import (
    EventCandidate,
    TurnUnderstanding,
)


class GroundingIssue(BaseModel):
    path: str
    reason: str
    rejected_text: str | None = None


class GroundingResult(BaseModel):
    understanding: TurnUnderstanding
    issues: list[GroundingIssue] = Field(default_factory=list)


class SemanticGrounder:
    def ground(
        self,
        *,
        message: str,
        understanding: TurnUnderstanding,
    ) -> GroundingResult:
        normalized_message = message.casefold()

        cleaned = understanding.model_copy(deep=True)
        issues: list[GroundingIssue] = []

        # Entity mentions must correspond to something actually present
        # in the user's message.
        grounded_entities = []

        for index, entity in enumerate(cleaned.entities):
            if entity.surface_text.casefold() not in normalized_message:
                issues.append(
                    GroundingIssue(
                        path=f"entities[{index}]",
                        reason=(
                            "Entity mention does not occur in the "
                            "original user message."
                        ),
                        rejected_text=entity.surface_text,
                    )
                )
                continue

            grounded_entities.append(entity)

        cleaned.entities = grounded_entities

        # Event participant surface text may not be invented either.
        grounded_events: list[EventCandidate] = []

        for event_index, event in enumerate(cleaned.events):
            grounded_participants = []

            for participant_index, participant in enumerate(
                event.participants
            ):
                surface_text = participant.entity.surface_text

                if (
                    surface_text
                    and surface_text.casefold() not in normalized_message
                ):
                    issues.append(
                        GroundingIssue(
                            path=(
                                f"events[{event_index}]"
                                f".participants[{participant_index}]"
                            ),
                            reason=(
                                "Participant referring expression does "
                                "not occur in the original user message."
                            ),
                            rejected_text=surface_text,
                        )
                    )
                    continue

                grounded_participants.append(participant)

            if grounded_participants:
                event.participants = grounded_participants
                grounded_events.append(event)
            else:
                issues.append(
                    GroundingIssue(
                        path=f"events[{event_index}]",
                        reason=(
                            "Event was removed because none of its "
                            "participants could be grounded."
                        ),
                    )
                )

        cleaned.events = grounded_events

        return GroundingResult(
            understanding=cleaned,
            issues=issues,
        )