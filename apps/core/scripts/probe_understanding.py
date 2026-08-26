from __future__ import annotations

import asyncio

from celeste.cognition.understanding import UnderstandingEngine
from celeste.providers.ollama import OllamaProvider
from celeste.cognition.understanding_scenarios import SCENARIOS


async def main() -> None:
    provider = OllamaProvider(
        model="qwen3.5:9b",
        think=False,
        temperature=0.0,
    )

    engine = UnderstandingEngine(
        provider
    )

    print()
    print("=" * 80)
    print("CELESTE V2 — UNDERSTANDING SCENARIO PROBE")
    print("=" * 80)

    for index, scenario in enumerate(
        SCENARIOS,
        start=1,
    ):
        print()
        print("=" * 80)
        print(
            f"[{index}/{len(SCENARIOS)}] "
            f"{scenario.id}"
        )
        print("=" * 80)

        print()
        print("MESSAGE:")
        print(scenario.message)

        if scenario.context is not None:
            print()
            print("CONTEXT:")
            print(scenario.context)

        print()
        print("FOCUS:")
        for item in scenario.focus:
            print(f"- {item}")

        print()
        print("EXPECTED BEHAVIOR NOTE:")
        print(scenario.notes)

        print()
        print("UNDERSTANDING:")

        try:
            understanding = await engine.understand(
                scenario.message,
                context=scenario.context,
            )

            print(
                understanding.model_dump_json(
                    indent=2
                )
            )

        except Exception as exc:
            print()
            print("ERROR:")
            print(
                f"{type(exc).__name__}: {exc}"
            )

    print()
    print("=" * 80)
    print("PROBE FINISHED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())