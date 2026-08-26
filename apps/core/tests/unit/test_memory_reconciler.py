import pytest

from celeste.memory.fake_memory_repository import (
    FakeMemoryRepository,
)
from celeste.memory.models import (
    MemoryRecordStatus,
)
from celeste.memory.reconciler import (
    MemoryReconciler,
    ReconciliationAction,
)


@pytest.mark.asyncio
async def test_new_fact_is_added():
    repository = FakeMemoryRepository()
    reconciler = MemoryReconciler(repository)

    result = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    assert result.action == ReconciliationAction.ADDED
    assert result.current_record.value == "Tiendanimal"

    active = await repository.find_active_records(
        subject_id="person_laura",
        predicate="works_at",
    )

    assert len(active) == 1


@pytest.mark.asyncio
async def test_identical_fact_is_not_duplicated():
    repository = FakeMemoryRepository()
    reconciler = MemoryReconciler(repository)

    first = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    second = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    assert second.action == ReconciliationAction.UNCHANGED

    assert (
        second.current_record.id
        == first.current_record.id
    )

    assert len(repository.records) == 1


@pytest.mark.asyncio
async def test_real_world_change_supersedes_old_fact():
    repository = FakeMemoryRepository()
    reconciler = MemoryReconciler(repository)

    old = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="works_at",
        value="Tiendanimal",
    )

    new = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="works_at",
        value="Otra empresa",
    )

    assert new.action == ReconciliationAction.SUPERSEDED

    previous = await repository.get_record(
        old.current_record.id
    )

    assert previous is not None
    assert (
        previous.status
        == MemoryRecordStatus.SUPERSEDED
    )

    assert new.current_record.value == "Otra empresa"


@pytest.mark.asyncio
async def test_correction_retracts_wrong_information():
    repository = FakeMemoryRepository()
    reconciler = MemoryReconciler(repository)

    wrong = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Madrid",
    )

    corrected = await reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Getafe",
        is_correction=True,
    )

    assert corrected.action == ReconciliationAction.CORRECTED

    previous = await repository.get_record(
        wrong.current_record.id
    )

    assert previous is not None
    assert (
        previous.status
        == MemoryRecordStatus.RETRACTED
    )

    assert corrected.correction is not None

    assert (
        corrected.correction.target_record_id
        == wrong.current_record.id
    )

    assert (
        corrected.correction.replacement_record_id
        == corrected.current_record.id
    )

@pytest.mark.asyncio
async def test_change_and_correction_leave_different_history():
    change_repository = FakeMemoryRepository()
    change_reconciler = MemoryReconciler(
        change_repository
    )

    correction_repository = FakeMemoryRepository()
    correction_reconciler = MemoryReconciler(
        correction_repository
    )

    changed_old = await change_reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Madrid",
    )

    await change_reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Getafe",
    )

    corrected_old = await correction_reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Madrid",
    )

    await correction_reconciler.reconcile_fact(
        subject_id="person_laura",
        predicate="lives_in",
        value="Getafe",
        is_correction=True,
    )

    changed_history = await change_repository.get_record(
        changed_old.current_record.id
    )

    corrected_history = await correction_repository.get_record(
        corrected_old.current_record.id
    )

    assert changed_history is not None
    assert corrected_history is not None

    assert (
        changed_history.status
        == MemoryRecordStatus.SUPERSEDED
    )

    assert (
        corrected_history.status
        == MemoryRecordStatus.RETRACTED
    )

    assert len(change_repository.corrections) == 0
    assert len(correction_repository.corrections) == 1