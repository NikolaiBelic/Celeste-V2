from __future__ import annotations

import argparse
import asyncio
import json

from celeste.cognition.interpretation_normalizer import normalize_interpretation
from celeste.cognition.understanding import Understanding
from celeste.providers import DEFAULT_MODELS, create_provider


CASES = [
    "Laura viene mañana.",
    "Creo que Marta está enfadada.",
    "No quiero dejar el trabajo.",
    "Laura dijo que Marta vendrá mañana.",
    "Laura habló con Marta y ella se fue.",
    "Me voy a Madrid... perdón, a Getafe.",
    "Creo que Marta está enfadada conmigo, aunque igual me estoy rayando.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Celeste's understanding probe with any LLM provider."
    )
    parser.add_argument(
        "--provider",
        choices=sorted(DEFAULT_MODELS),
        default="ollama",
    )
    parser.add_argument(
        "--model",
        help="Model name (uses the provider default when omitted).",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    provider = create_provider(args.provider, model=args.model)
    understanding = Understanding(provider)

    for index, text in enumerate(CASES, start=1):
        print()
        print("=" * 90)
        print(f"[{index}] {text}")
        print("=" * 90)

        try:
            raw = await understanding.interpret_raw(text)

            print("\nRAW:")
            print(
                json.dumps(
                    raw.model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2,
                )
            )

            interpretation = normalize_interpretation(raw)

            print("\nNORMALIZED:")
            print(
                json.dumps(
                    interpretation.model_dump(mode="json"),
                    ensure_ascii=False,
                    indent=2,
                )
            )

        except Exception as exc:
            print(f"\nERROR: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
