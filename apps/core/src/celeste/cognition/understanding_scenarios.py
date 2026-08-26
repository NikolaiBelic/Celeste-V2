from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UnderstandingScenario:
    id: str
    message: str
    context: str | None = None

    focus: tuple[str, ...] = field(
        default_factory=tuple
    )

    notes: str = ""


SCENARIOS: tuple[UnderstandingScenario, ...] = (
    UnderstandingScenario(
        id="relationship_breakup",
        message="Lo he dejado con Laura.",
        focus=(
            "completed_event",
            "relationship_state_change",
            "past_or_recent_time",
        ),
        notes=(
            "Debe distinguir una ruptura completada "
            "de una intención de ruptura."
        ),
    ),

    UnderstandingScenario(
        id="relationship_reconciliation",
        message="Laura y yo hemos vuelto.",
        context=(
            "Previously, the user and Laura had ended "
            "their romantic relationship."
        ),
        focus=(
            "reconciliation",
            "relationship_state_change",
            "context_dependency",
        ),
        notes=(
            "Debe interpretar que existe una reanudación "
            "de una relación previa."
        ),
    ),

    UnderstandingScenario(
        id="ambiguous_romantic_interest",
        message="Últimamente estoy viendo mucho a Marta.",
        focus=(
            "uncertainty",
            "avoid_overclaiming",
            "social_context",
        ),
        notes=(
            "No debe convertir automáticamente a Marta "
            "en pareja romántica."
        ),
    ),

    UnderstandingScenario(
        id="family_argument",
        message="He discutido con mi madre.",
        focus=(
            "episodic_event",
            "social_event",
            "emotional_relevance",
        ),
        notes=(
            "Debe reconocer un episodio interpersonal "
            "sin convertirlo en ruptura familiar."
        ),
    ),

    UnderstandingScenario(
        id="new_job_ambiguous_transition",
        message="Hoy he empezado en otra empresa.",
        context=(
            "The user currently works at Company A."
        ),
        focus=(
            "job_start_event",
            "current_state",
            "avoid_assuming_old_job_ended",
        ),
        notes=(
            "El nuevo trabajo no implica necesariamente "
            "haber dejado el anterior."
        ),
    ),

    UnderstandingScenario(
        id="cancelled_move",
        message="Al final no me mudo a Madrid.",
        context=(
            "The user had previously been considering "
            "moving to Madrid."
        ),
        focus=(
            "cancelled_intention",
            "negation",
            "future_plan",
        ),
        notes=(
            "No debe interpretar una mudanza completada."
        ),
    ),

    UnderstandingScenario(
        id="adopted_dog",
        message="He adoptado un perro.",
        focus=(
            "completed_event",
            "new_entity",
            "persistent_relevance",
        ),
        notes=(
            "Debe detectar una adopción real, no solo "
            "una intención."
        ),
    ),

    UnderstandingScenario(
        id="pet_name_context",
        message="Se llama Nala.",
        context=(
            "The user has just said that they adopted "
            "a dog."
        ),
        focus=(
            "contextual_reference",
            "entity_identity",
            "attribute_update",
        ),
        notes=(
            "Debe vincular Nala con el animal mencionado "
            "en el contexto."
        ),
    ),

    UnderstandingScenario(
        id="explicit_correction",
        message=(
            "Te dije que Laura vivía en Madrid, "
            "pero me equivoqué. Vive en Getafe."
        ),
        focus=(
            "correction",
            "retraction",
            "replacement_fact",
        ),
        notes=(
            "No debe tratarlo como una mudanza real."
        ),
    ),

    UnderstandingScenario(
        id="real_world_move",
        message="Laura se ha mudado de Madrid a Getafe.",
        focus=(
            "real_world_change",
            "move_event",
            "historical_state",
        ),
        notes=(
            "Madrid pudo ser cierto antes; Getafe es "
            "el nuevo estado."
        ),
    ),

    UnderstandingScenario(
        id="user_hypothesis",
        message="Creo que Marta está enfadada conmigo.",
        focus=(
            "user_belief",
            "uncertainty",
            "avoid_fact_conversion",
        ),
        notes=(
            "Que el usuario lo crea no significa que "
            "Marta esté realmente enfadada."
        ),
    ),

    UnderstandingScenario(
        id="relationship_distress_not_breakup",
        message="Laura y yo estamos fatal últimamente.",
        focus=(
            "relationship_distress",
            "current_state",
            "avoid_breakup_assumption",
        ),
        notes=(
            "Deterioro relacional no equivale a ruptura."
        ),
    ),
)