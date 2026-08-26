import pytest

from celeste.cognition.models import TurnUnderstanding
from celeste.cognition.understanding import UnderstandingEngine
from celeste.conversation.engine import ConversationEngine
from celeste.providers.fake import FakeLLMProvider


class DummyComponent:
    pass


@pytest.mark.asyncio
async def test_process_returns_understanding():
    expected = TurnUnderstanding(
        overall_confidence=0.98,
    )

    provider = FakeLLMProvider(expected)
    understanding_engine = UnderstandingEngine(provider)

    engine = ConversationEngine(
        understanding_engine=understanding_engine,
        entity_resolver=DummyComponent(),
        working_memory=DummyComponent(),
        context_resolver=DummyComponent(),
    )

    result = await engine.process(
        "Hola Celeste."
    )

    assert result.message == "Hola Celeste."
    assert result.understanding == expected


@pytest.mark.asyncio
async def test_process_rejects_empty_message():
    provider = FakeLLMProvider(TurnUnderstanding())

    engine = ConversationEngine(
        understanding_engine=UnderstandingEngine(provider),
        entity_resolver=DummyComponent(),
        working_memory=DummyComponent(),
        context_resolver=DummyComponent(),
    )

    with pytest.raises(ValueError):
        await engine.process("   ")