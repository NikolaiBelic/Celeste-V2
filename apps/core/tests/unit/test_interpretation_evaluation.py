from __future__ import annotations

import json
from pathlib import Path

from celeste.cognition.raw_interpretation import RawInterpretation


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
