from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any

from celeste.cognition.raw_interpretation import RawInterpretation
from celeste.cognition.understanding import Understanding
from celeste.providers import DEFAULT_MODELS, create_provider


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "tests" / "scenarios" / "interpretation_cases.json"


def feature_values(raw: RawInterpretation) -> dict[str, list[str]]:
    return {
        "acts": [str(x) for x in raw.discourse.acts],
        "entity_ids": [x.temp_id for x in raw.entities],
        "entity_mentions": [x.mention for x in raw.entities],
        "identity_hints": [x.identity_hint for x in raw.entities if x.identity_hint],
        "situation_kinds": [str(x.kind) for x in raw.situations],
        "polarities": [str(x.polarity) for x in raw.situations],
        "realities": [str(x.reality) for x in raw.situations],
        "certainties": [str(x.certainty) for x in raw.situations],
        "transitions": [x.transition for x in raw.situations if x.transition],
        "proposition_modes": [str(x.mode) for x in raw.propositions],
        "proposition_polarities": [str(x.polarity) for x in raw.propositions],
        "attributions": [str(x.relation) for x in raw.attributions],
        "references": [x.text for x in raw.references],
        "revisions": [str(x.revision) for x in raw.revisions],
        "semantic_relations": [str(x.relation) for x in raw.semantic_relations],
    }


def evaluate(raw: RawInterpretation, expected: dict[str, Any]) -> list[str]:
    actual = feature_values(raw)
    failures: list[str] = []
    for feature, required in expected.items():
        if feature.endswith("_any"):
            base_feature = feature.removesuffix("_any")
            available = {str(item).casefold() for item in actual.get(base_feature, [])}
            if not any(str(item).casefold() in available for item in required):
                failures.append(f"{base_feature}: expected any of {required}; got {actual.get(base_feature, [])}")
            continue
        if feature not in actual:
            continue
        available = {str(item).casefold() for item in actual[feature]}
        missing = [item for item in required if str(item).casefold() not in available]
        if missing:
            failures.append(f"{feature}: missing {missing}; got {actual[feature]}")

    counts = {
        "situations": len(raw.situations), "entities": len(raw.entities),
        "revisions": len(raw.revisions), "unresolved": len(raw.unresolved),
    }
    for name, count in counts.items():
        minimum, maximum = expected.get(f"min_{name}"), expected.get(f"max_{name}")
        if minimum is not None and count < minimum:
            failures.append(f"{name}: expected at least {minimum}, got {count}")
        if maximum is not None and count > maximum:
            failures.append(f"{name}: expected at most {maximum}, got {count}")

    candidate_minimum = expected.get("reference_candidates_min")
    if candidate_minimum is not None and not any(
        len(reference.candidate_entity_temp_ids) >= candidate_minimum
        for reference in raw.references
    ):
        failures.append(f"references: no item has {candidate_minimum} candidates")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Understanding with a real model.")
    parser.add_argument("--provider", choices=sorted(DEFAULT_MODELS), required=True)
    parser.add_argument("--model")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--category")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    cases = json.loads(args.corpus.read_text(encoding="utf-8"))
    if args.category:
        cases = [case for case in cases if case["category"] == args.category]
    if args.limit:
        cases = cases[:args.limit]

    provider = create_provider(args.provider, model=args.model)
    understanding = Understanding(provider)
    output_dir = ROOT / "runtime" / "interpretation-evaluation"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output or output_dir / f"{args.provider}.json"
    previous: dict[str, dict[str, Any]] = {}
    if args.resume and output_path.exists():
        saved = json.loads(output_path.read_text(encoding="utf-8"))
        previous = {
            item["id"]: item for item in saved["results"] if item.get("raw") is not None
        }
    results: list[dict[str, Any]] = []
    category_scores: dict[str, list[str]] = defaultdict(list)

    for index, case in enumerate(cases, start=1):
        print(f"[{index:02}/{len(cases):02}] {case['id']}: {case['text']}", flush=True)
        try:
            if case["id"] in previous:
                raw = RawInterpretation.model_validate(previous[case["id"]]["raw"])
            else:
                raw = await understanding.interpret_raw(case["text"])
            failures = evaluate(raw, case["expect"])
            result = {**case, "status": "failed" if failures else "passed",
                      "passed": not failures, "failures": failures,
                      "raw": raw.model_dump(mode="json")}
        except Exception as exc:
            result = {**case, "status": "error", "passed": False,
                      "failures": [f"{type(exc).__name__}: {exc}"], "raw": None}
        category_scores[case["category"]].append(result["status"])
        results.append(result)
        status = result["status"].upper()
        if result["failures"]:
            status += f": {' | '.join(result['failures'])}"
        print(f"  {status}", flush=True)

        if result["status"] == "error" and "RESOURCE_EXHAUSTED" in result["failures"][0]:
            print("  Stopping: provider quota exhausted; use --resume later.", flush=True)
            break

    summary = {
        "provider": args.provider, "model": getattr(provider, "model", args.model),
        "created_at": datetime.now(UTC).isoformat(),
        "passed": sum(item["status"] == "passed" for item in results),
        "failed": sum(item["status"] == "failed" for item in results),
        "errors": sum(item["status"] == "error" for item in results),
        "completed": len(results), "corpus_total": len(cases),
        "categories": {
            name: {
                "passed": scores.count("passed"),
                "failed": scores.count("failed"),
                "errors": scores.count("error"),
                "completed": len(scores),
            }
            for name, scores in sorted(category_scores.items())
        },
    }
    output_path.write_text(json.dumps({"summary": summary, "results": results},
                                      ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{summary['passed']} passed, {summary['failed']} failed, "
          f"{summary['errors']} errors ({summary['completed']}/{summary['corpus_total']})")
    for name, score in summary["categories"].items():
        print(f"  {name}: {score['passed']} pass, {score['failed']} fail, "
              f"{score['errors']} error")
    print(f"Report: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
