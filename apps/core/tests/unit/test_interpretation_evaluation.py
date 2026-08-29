from __future__ import annotations

import json
from pathlib import Path

from celeste.cognition.raw_interpretation import RawInterpretation
from celeste.cognition.interpretation_evaluation import evaluate_graph


CORPUS = Path(__file__).parents[1] / "scenarios" / "interpretation_cases.json"


def test_interpretation_corpus_covers_roadmap_categories() -> None:
    cases = json.loads(CORPUS.read_text(encoding="utf-8"))

    assert len(cases) == 36
    assert len({case["id"] for case in cases}) == 36
    assert {case["category"] for case in cases} == {
        "simple", "negation", "belief", "desire", "ambiguity",
        "correction", "reported_speech", "question", "request",
    }
    assert all(case["text"] and case["expect"] for case in cases)


def test_llm_schema_requires_discourse_acts() -> None:
    schema = RawInterpretation.model_json_schema()

    assert "discourse" in schema["required"]
    assert "acts" in schema["$defs"]["RawDiscourseMeaning"]["required"]

def test_evaluate_graph_accepts_matching_situation_participants() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                    "identity_hint": "user",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "call",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        },
                        {
                            "role": "recipient",
                            "entity_temp_id": "laura",
                        },
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "situations": [
                {
                    "semantic_type": "call",
                    "participants": {
                        "agent": "user",
                        "recipient": "laura",
                    },
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_situation_participant() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                    "identity_hint": "user",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "call",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        },
                        {
                            "role": "recipient",
                            "entity_temp_id": "user",
                        },
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "situations": [
                {
                    "semantic_type": "call",
                    "participants": {
                        "agent": "user",
                        "recipient": "laura",
                    },
                }
            ]
        },
    )

    assert failures


def test_evaluate_graph_accepts_matching_proposition_target() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "pablo",
                    "mention": "Pablo",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "sevilla",
                    "mention": "Sevilla",
                    "semantic_type": "location",
                },
            ],
            "situations": [
                {
                    "temp_id": "state1",
                    "kind": "state",
                    "semantic_type": "reside",
                    "polarity": "positive",
                    "reality": "hypothetical",
                    "certainty": "uncertain",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        },
                        {
                            "role": "location",
                            "entity_temp_id": "sevilla",
                        },
                    ],
                }
            ],
            "propositions": [
                {
                    "temp_id": "belief1",
                    "mode": "belief",
                    "holder_entity_temp_id": "pablo",
                    "target_id": "state1",
                    "polarity": "positive",
                    "certainty": "uncertain",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "propositions": [
                {
                    "mode": "belief",
                    "holder": "pablo",
                    "target_situation": {
                        "semantic_type": "reside",
                    },
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_proposition_holder() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "pablo",
                    "mention": "Pablo",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "state1",
                    "kind": "state",
                    "semantic_type": "reside",
                    "polarity": "positive",
                    "reality": "hypothetical",
                    "certainty": "uncertain",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        }
                    ],
                }
            ],
            "propositions": [
                {
                    "temp_id": "belief1",
                    "mode": "belief",
                    "holder_entity_temp_id": "laura",
                    "target_id": "state1",
                    "polarity": "positive",
                    "certainty": "uncertain",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "propositions": [
                {
                    "mode": "belief",
                    "holder": "pablo",
                    "target_situation": {
                        "semantic_type": "reside",
                    },
                }
            ]
        },
    )

    assert failures

def test_evaluate_graph_accepts_matching_attribution() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "arrive",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "marta",
                        }
                    ],
                }
            ],
            "attributions": [
                {
                    "temp_id": "attribution1",
                    "source_entity_temp_id": "laura",
                    "relation": "reports",
                    "target_id": "event1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "attributions": [
                {
                    "relation": "reports",
                    "source_entity": "laura",
                    "target_situation": "arrive",
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_attribution_source() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["assert"]},
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "arrive",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "marta",
                        }
                    ],
                }
            ],
            "attributions": [
                {
                    "temp_id": "attribution1",
                    "source_entity_temp_id": "marta",
                    "relation": "reports",
                    "target_id": "event1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "attributions": [
                {
                    "relation": "reports",
                    "source_entity": "laura",
                    "target_situation": "arrive",
                }
            ]
        },
    )

    assert failures


def test_evaluate_graph_accepts_matching_revision() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["correct"]},
            "situations": [
                {
                    "temp_id": "state1",
                    "kind": "state",
                    "semantic_type": "reside",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                },
                {
                    "temp_id": "state2",
                    "kind": "state",
                    "semantic_type": "reside",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                },
            ],
            "revisions": [
                {
                    "temp_id": "revision1",
                    "revision": "correction",
                    "target_id": "state1",
                    "replacement_id": "state2",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "revisions": [
                {
                    "revision": "correction",
                    "target_situation": "reside",
                    "replacement_situation": "reside",
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_revision_replacement() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {"acts": ["correct"]},
            "situations": [
                {
                    "temp_id": "state1",
                    "kind": "state",
                    "semantic_type": "reside",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                },
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "travel",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                },
            ],
            "revisions": [
                {
                    "temp_id": "revision1",
                    "revision": "correction",
                    "target_id": "state1",
                    "replacement_id": "event1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "revisions": [
                {
                    "revision": "correction",
                    "target_situation": "reside",
                    "replacement_situation": "reside",
                }
            ]
        },
    )

    assert failures

def test_evaluate_graph_accepts_matching_reference_usage() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "ella",
                    "candidate_entity_temp_ids": ["laura", "marta"],
                    "resolved_entity_temp_id": "marta",
                }
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "leave",
                    "participants": [
                        {
                            "role": "agent",
                            "reference_temp_id": "ref1",
                        }
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "references": [
                {
                    "text": "ella",
                    "candidates": ["laura", "marta"],
                    "resolved_entity": "marta",
                    "used_in_situation": {
                        "semantic_type": "leave",
                        "role": "agent",
                    },
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_reference_candidates() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "ella",
                    "candidate_entity_temp_ids": ["laura"],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "references": [
                {
                    "text": "ella",
                    "candidates": ["laura", "marta"],
                }
            ]
        },
    )

    assert failures
    assert failures[0].startswith("graph.references:")


def test_evaluate_graph_rejects_wrong_reference_usage_role() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                }
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "ella",
                    "candidate_entity_temp_ids": ["laura"],
                }
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "leave",
                    "participants": [
                        {
                            "role": "patient",
                            "reference_temp_id": "ref1",
                        }
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "references": [
                {
                    "text": "ella",
                    "used_in_situation": {
                        "semantic_type": "leave",
                        "role": "agent",
                    },
                }
            ]
        },
    )

    assert failures
    assert failures[0].startswith("graph.references:")


def test_evaluate_graph_rejects_wrong_resolved_reference() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "marta",
                    "mention": "Marta",
                    "semantic_type": "person",
                },
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "ella",
                    "candidate_entity_temp_ids": ["laura", "marta"],
                    "resolved_entity_temp_id": "laura",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "references": [
                {
                    "text": "ella",
                    "resolved_entity": "marta",
                }
            ]
        },
    )

    assert failures
    assert failures[0].startswith("graph.references:")

def test_evaluate_graph_matches_reference_candidates_semantically() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "entity1",
                    "mention": "Alex",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "entity2",
                    "mention": "su hermano",
                    "semantic_type": "person",
                },
            ],
            "references": [
                {
                    "temp_id": "ref1",
                    "text": "cuál de los dos",
                    "candidate_entity_temp_ids": [
                        "entity1",
                        "entity2",
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "references": [
                {
                    "text": "cuál de los dos",
                    "candidates": [
                        "Alex",
                        "su hermano",
                    ],
                }
            ]
        },
    )

    assert failures == []

def test_evaluate_graph_matches_scope_operator() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                }
            ],
            "situations": [
                {
                    "temp_id": "say1",
                    "kind": "event",
                    "semantic_type": "say",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        }
                    ],
                    "polarity": "negative",
                    "reality": "actual",
                    "certainty": "asserted",
                }
            ],
            "scope_operators": [
                {
                    "temp_id": "scope1",
                    "operator": "negation",
                    "target_id": "say1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "scope_operators": [
                {
                    "operator": "negation",
                    "target_situation": {
                        "semantic_type": "say",
                        "participants": {
                            "agent": "user",
                        },
                    },
                }
            ]
        },
    )

    assert failures == []

def test_evaluate_graph_rejects_scope_on_wrong_situation() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                    "semantic_type": "person",
                },
            ],
            "situations": [
                {
                    "temp_id": "say1",
                    "kind": "event",
                    "semantic_type": "say",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        }
                    ],
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                },
                {
                    "temp_id": "lie1",
                    "kind": "event",
                    "semantic_type": "lie",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        }
                    ],
                    "polarity": "negative",
                    "reality": "actual",
                    "certainty": "asserted",
                },
            ],
            "scope_operators": [
                {
                    "temp_id": "scope1",
                    "operator": "negation",
                    "target_id": "lie1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "scope_operators": [
                {
                    "operator": "negation",
                    "target_situation": {
                        "semantic_type": "say",
                        "participants": {
                            "agent": "user",
                        },
                    },
                }
            ]
        },
    )

    assert len(failures) == 1
    assert failures[0].startswith(
        "graph.scope_operators:"
    )

def test_evaluate_graph_accepts_matching_semantic_content_link() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                },
            ],
            "situations": [
                {
                    "temp_id": "say1",
                    "kind": "event",
                    "semantic_type": "say",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        }
                    ],
                    "polarity": "negative",
                    "reality": "actual",
                    "certainty": "asserted",
                },
                {
                    "temp_id": "lie1",
                    "kind": "event",
                    "semantic_type": "lie",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        }
                    ],
                    "polarity": "positive",
                    "reality": "hypothetical",
                    "certainty": "uncertain",
                },
            ],
            "semantic_content_links": [
                {
                    "source_id": "say1",
                    "target_id": "lie1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "semantic_content_links": [
                {
                    "source_situation": {
                        "semantic_type": "say",
                        "participants": {
                            "agent": "user",
                        },
                    },
                    "target_situation": {
                        "semantic_type": "lie",
                        "participants": {
                            "agent": "laura",
                        },
                    },
                }
            ]
        },
    )

    assert failures == []


def test_evaluate_graph_rejects_wrong_semantic_content_link() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "user",
                    "mention": "yo",
                },
                {
                    "temp_id": "laura",
                    "mention": "Laura",
                },
            ],
            "situations": [
                {
                    "temp_id": "say1",
                    "kind": "event",
                    "semantic_type": "say",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        }
                    ],
                    "polarity": "negative",
                    "reality": "actual",
                    "certainty": "asserted",
                },
                {
                    "temp_id": "lie1",
                    "kind": "event",
                    "semantic_type": "lie",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "laura",
                        }
                    ],
                    "polarity": "positive",
                    "reality": "hypothetical",
                    "certainty": "uncertain",
                },
            ],
            "semantic_content_links": [
                {
                    "source_id": "say1",
                    "target_id": "lie1",
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "semantic_content_links": [
                {
                    "source_situation": {
                        "semantic_type": "say",
                        "participants": {
                            "agent": "user",
                        },
                    },
                    "target_situation": {
                        "semantic_type": "leave",
                        "participants": {
                            "agent": "laura",
                        },
                    },
                }
            ]
        },
    )

    assert len(failures) == 1
    assert (
        "graph.semantic_content_links"
        in failures[0]
    )

def test_evaluate_graph_rejects_missing_semantic_relation_without_propositions() -> None:
    raw = RawInterpretation.model_validate(
        {
            "discourse": {
                "acts": ["assert"],
            },
            "entities": [
                {
                    "temp_id": "pablo",
                    "mention": "Pablo",
                    "semantic_type": "person",
                },
                {
                    "temp_id": "meeting",
                    "mention": "la reunión",
                    "semantic_type": "event",
                },
            ],
            "situations": [
                {
                    "temp_id": "arrive1",
                    "kind": "event",
                    "semantic_type": "arrive",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "pablo",
                        }
                    ],
                },
                {
                    "temp_id": "start1",
                    "kind": "event",
                    "semantic_type": "start",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "theme",
                            "entity_temp_id": "meeting",
                        }
                    ],
                },
            ],
            "propositions": [],
            "semantic_relations": [],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "semantic_relations": [
                {
                    "relation": "temporal_before",
                    "source_situation": "arrive",
                    "target_situation": "start",
                }
            ]
        },
    )

    assert len(failures) == 1
    assert failures[0].startswith(
        "graph.semantic_relations:"
    )

def test_evaluate_graph_matches_participant_entity_semantically() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "entity42",
                    "mention": "un perro",
                    "canonical_name": "perro",
                    "semantic_type": "animal",
                },
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                    "identity_hint": "user",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "adopt",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        },
                        {
                            "role": "patient",
                            "entity_temp_id": "entity42",
                        },
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "situations": [
                {
                    "semantic_type": "adopt",
                    "participants": {
                        "agent": "user",
                        "patient": "perro",
                    },
                }
            ]
        },
    )

    assert failures == []

def test_evaluate_graph_rejects_wrong_participant_entity_semantically() -> None:
    raw = RawInterpretation.model_validate(
        {
            "entities": [
                {
                    "temp_id": "entity42",
                    "mention": "un gato",
                    "canonical_name": "gato",
                    "semantic_type": "animal",
                },
                {
                    "temp_id": "user",
                    "mention": "yo",
                    "semantic_type": "person",
                    "identity_hint": "user",
                },
            ],
            "situations": [
                {
                    "temp_id": "event1",
                    "kind": "event",
                    "semantic_type": "adopt",
                    "polarity": "positive",
                    "reality": "actual",
                    "certainty": "asserted",
                    "participants": [
                        {
                            "role": "agent",
                            "entity_temp_id": "user",
                        },
                        {
                            "role": "patient",
                            "entity_temp_id": "entity42",
                        },
                    ],
                }
            ],
        }
    )

    failures = evaluate_graph(
        raw,
        {
            "situations": [
                {
                    "semantic_type": "adopt",
                    "participants": {
                        "agent": "user",
                        "patient": "perro",
                    },
                }
            ]
        },
    )

    assert len(failures) == 1
    assert failures[0].startswith("graph.situations:")
