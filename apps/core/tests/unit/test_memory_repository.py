import pytest

from celeste.memory.fake_memory_repository import (
    FakeMemoryRepository,
)
from celeste.memory.models import (
    MemoryRecord,
    MemoryRecordKind,
    MemoryRecordStatus,
)


@pytest.mark.asyncio
async def test_add_and_read_memory_record():
    repository = FakeMemoryRepository()

    record = MemoryRecord(
        id="memory_1",
        kind=MemoryRecordKind.FACT,
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    await repository.add_record(record)

    stored = await repository.get_record(
        "memory_1"
    )

    assert stored is not None
    assert stored.value == "Tiendanimal"


@pytest.mark.asyncio
async def test_find_only_active_records():
    repository = FakeMemoryRepository()

    active = MemoryRecord(
        id="memory_active",
        kind=MemoryRecordKind.FACT,
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    old = MemoryRecord(
        id="memory_old",
        kind=MemoryRecordKind.FACT,
        subject_id="person_laura",
        predicate="works_at",
        value="Otra tienda",
        status=MemoryRecordStatus.SUPERSEDED,
    )

    await repository.add_record(active)
    await repository.add_record(old)

    result = await repository.find_active_records(
        subject_id="person_laura",
        predicate="works_at",
    )

    assert len(result) == 1
    assert result[0].id == "memory_active"

@pytest.mark.asyncio
async def test_old_fact_can_remain_in_history_without_being_current():
    repository = FakeMemoryRepository()

    old = MemoryRecord(
        id="memory_old_job",
        kind=MemoryRecordKind.FACT,
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    await repository.add_record(old)

    old.status = MemoryRecordStatus.SUPERSEDED

    await repository.update_record(old)

    current = MemoryRecord(
        id="memory_current_job",
        kind=MemoryRecordKind.FACT,
        subject_id="person_laura",
        predicate="works_at",
        value="Otra empresa",
    )

    await repository.add_record(current)

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="works_at",
    )

    assert len(active) == 1
    assert active[0].value == "Otra empresa"

    historical = await repository.get_record(
        "memory_old_job"
    )

    assert historical is not None
    assert (
        historical.status
        == MemoryRecordStatus.SUPERSEDED
    )