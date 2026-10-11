"""Automated Pytest Suite for PawPal+ System.

Verifies Task completion states, Pet task management, Owner multi-pet
task aggregation, and Scheduler chronological daily schedule ordering.
"""

from datetime import time
import pytest
from pawpal_system import Owner, Pet, Scheduler, Task


@pytest.fixture
def sample_owner() -> Owner:
    """Fixture providing a standard test owner with a 120-minute budget."""
    return Owner(name="Alex Rivera", email="alex@example.com", available_minutes=120, day_start=time(8, 0))


@pytest.fixture
def sample_pets() -> tuple[Pet, Pet]:
    """Fixture providing two distinct pet instances."""
    dog = Pet(name="Luna", species="Dog", breed="Labrador", age_years=3.0)
    cat = Pet(name="Milo", species="Cat", breed="Siamese", age_years=2.0)
    return dog, cat


@pytest.fixture
def scheduler() -> Scheduler:
    """Fixture providing a Scheduler instance."""
    return Scheduler(strategy="priority_first")


def test_task_completion_status():
    """Verify task completion transitions from default False, to True, and back to False."""
    task = Task(title="Evening Walk", duration_minutes=30, priority="high")

    # 1. Verifies is_completed defaults to False
    assert task.is_completed is False
    assert task.completed is False

    # 2. Calls mark_complete() and asserts is_completed == True
    task.mark_complete()
    assert task.is_completed is True
    assert task.completed is True

    # 3. Calls mark_pending() and asserts is_completed == False
    task.mark_pending()
    assert task.is_completed is False
    assert task.completed is False


def test_pet_task_management(sample_pets):
    """Verify adding multiple tasks to a Pet and removing a specified task."""
    pet, _ = sample_pets
    assert len(pet.tasks) == 0

    task1 = Task(title="Morning Feeding", duration_minutes=15, priority="high")
    task2 = Task(title="Brush Coat", duration_minutes=20, priority="medium")
    task3 = Task(title="Nail Trim", duration_minutes=10, priority="low")

    # Adds multiple tasks to a Pet and asserts task count increases accurately
    pet.add_task(task1)
    assert len(pet.tasks) == 1
    assert task1.pet_name == pet.name

    pet.add_task(task2)
    pet.add_task(task3)
    assert len(pet.tasks) == 3

    # Verifies remove_task() removes the specified task and decrements count
    removed = pet.remove_task(task2.task_id)
    assert removed is True
    assert len(pet.tasks) == 2
    assert task2 not in pet.tasks
    assert task1 in pet.tasks
    assert task3 in pet.tasks


def test_owner_task_aggregation(sample_owner, sample_pets):
    """Verify Owner aggregates tasks across multiple pets."""
    owner = sample_owner
    pet_a, pet_b = sample_pets

    # 2 tasks for Pet A
    task_a1 = Task(title="Insulin Dose", duration_minutes=10, priority="critical")
    task_a2 = Task(title="Morning Walk", duration_minutes=30, priority="high")
    pet_a.add_task(task_a1)
    pet_a.add_task(task_a2)

    # 1 task for Pet B
    task_b1 = Task(title="Breakfast", duration_minutes=15, priority="high")
    pet_b.add_task(task_b1)

    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    # Verifies owner.get_all_tasks() returns all 3 tasks across both pets
    all_tasks = owner.get_all_tasks(pending_only=True)
    assert len(all_tasks) == 3
    assert task_a1 in all_tasks
    assert task_a2 in all_tasks
    assert task_b1 in all_tasks


def test_scheduler_daily_schedule_ordering(scheduler):
    """Verify tasks with non-chronological times are strictly sorted chronologically."""
    # Adds tasks with non-chronological times
    t_afternoon = Task(title="Afternoon Walk", duration_minutes=30, scheduled_time=time(16, 0))
    t_morning = Task(title="Breakfast", duration_minutes=15, scheduled_time=time(8, 0))
    t_noon = Task(title="Midday Meds", duration_minutes=10, scheduled_time=time(12, 30))
    t_evening = Task(title="Dinner", duration_minutes=15, scheduled_time=time(19, 0))

    scheduler.add_task(t_afternoon)
    scheduler.add_task(t_morning)
    scheduler.add_task(t_evening)
    scheduler.add_task(t_noon)

    # Calls scheduler.get_daily_schedule()
    ordered_schedule = scheduler.get_daily_schedule()

    # Asserts the returned list is strictly sorted chronologically by scheduled_time
    assert len(ordered_schedule) == 4
    expected_order = [t_morning, t_noon, t_afternoon, t_evening]
    assert ordered_schedule == expected_order

    for i in range(len(ordered_schedule) - 1):
        assert ordered_schedule[i].scheduled_time < ordered_schedule[i + 1].scheduled_time


def test_scheduler_build_plan_budget_filtering(sample_owner, sample_pets, scheduler):
    """Verify that build_plan prioritizes high-weight tasks and drops tasks exceeding budget."""
    owner = sample_owner
    owner.available_minutes = 45  # Constrained budget
    pet_a, _ = sample_pets

    high_task = Task(title="Critical Injection", duration_minutes=15, priority="critical")
    med_task = Task(title="Short Walk", duration_minutes=30, priority="high")
    low_task = Task(title="Long Play Session", duration_minutes=30, priority="low")

    pet_a.add_task(high_task)
    pet_a.add_task(med_task)
    pet_a.add_task(low_task)
    owner.add_pet(pet_a)

    plan = scheduler.build_plan(owner)
    scheduled = plan["scheduled"]
    skipped = plan["skipped"]

    assert high_task in scheduled
    assert med_task in scheduled
    assert low_task in skipped
    assert plan["minutes_used"] == 45
