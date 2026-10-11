"""Automated Pytest Suite for PawPal+ System.

Verifies Task completion states, Pet task management, Owner multi-pet
task aggregation, and Scheduler chronological daily schedule ordering.
"""

from datetime import date, datetime, time
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


def test_scheduler_multi_attribute_sorting():
    """Verify sort_by_time and sort_by_priority methods with tie-breaking logic."""
    scheduler = Scheduler()
    t_meds = Task(title="Morning Meds", duration_minutes=15, scheduled_time=time(9, 0), priority="high")
    t_play = Task(title="Play Time", duration_minutes=30, scheduled_time=time(9, 0), priority="low")
    t_walk = Task(title="Early Walk", duration_minutes=20, scheduled_time=time(8, 0), priority="medium")

    # sort_by_time: 08:00 first, then at 09:00 high priority (t_meds) before low priority (t_play)
    by_time = scheduler.sort_by_time([t_meds, t_play, t_walk])
    assert by_time == [t_walk, t_meds, t_play]

    # sort_by_priority: high (t_meds) -> medium (t_walk) -> low (t_play)
    by_prio = scheduler.sort_by_priority([t_meds, t_play, t_walk])
    assert by_prio == [t_meds, t_walk, t_play]


def test_scheduler_multi_criteria_filtering(sample_owner, sample_pets):
    """Verify filter_tasks filtering across all owner pets by pet name, status, and priority."""
    owner = sample_owner
    pet_a, pet_b = sample_pets

    t1 = Task(title="Luna Walk", duration_minutes=30, priority="high")
    t2 = Task(title="Luna Brush", duration_minutes=15, priority="low")
    t2.mark_complete()
    t3 = Task(title="Milo Vet", duration_minutes=45, priority="high")

    pet_a.add_task(t1)
    pet_a.add_task(t2)
    pet_b.add_task(t3)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    scheduler = Scheduler(owner=owner)

    # Filter by pet name
    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    assert len(luna_tasks) == 2
    assert t1 in luna_tasks and t2 in luna_tasks

    # Filter by completion status
    completed = scheduler.filter_tasks(is_completed=True)
    assert len(completed) == 1 and completed[0].title == "Luna Brush"

    # Filter by priority
    high_tasks = scheduler.filter_tasks(priority="high")
    assert len(high_tasks) == 2
    assert t1 in high_tasks and t3 in high_tasks


def test_scheduler_find_next_available_slot(sample_owner, sample_pets):
    """Verify finding the earliest continuous slot within operating hours across all pets."""
    owner = sample_owner
    pet_a, pet_b = sample_pets
    search_d = date(2026, 10, 15)

    # Pet A has morning task 08:00 - 08:30
    t1 = Task(
        title="Walk",
        duration_minutes=30,
        scheduled_time=time(8, 0),
        scheduled_datetime=datetime(2026, 10, 15, 8, 0),
    )
    # Pet B has vet visit 09:00 - 10:00
    t2 = Task(
        title="Vet",
        duration_minutes=60,
        scheduled_time=time(9, 0),
        scheduled_datetime=datetime(2026, 10, 15, 9, 0),
    )

    pet_a.add_task(t1)
    pet_b.add_task(t2)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    scheduler = Scheduler(owner=owner)

    # Gap between 08:30 and 09:00 is 30 mins:
    # A 30-min slot should fit right at 08:30:
    slot_30 = scheduler.find_next_available_slot(duration_minutes=30, search_date=search_d)
    assert slot_30 == datetime(2026, 10, 15, 8, 30)

    # A 45-min slot cannot fit between 08:30 and 09:00, so it must start after 10:00:
    slot_45 = scheduler.find_next_available_slot(duration_minutes=45, search_date=search_d)
    assert slot_45 == datetime(2026, 10, 15, 10, 0)

    # If entire operating window is booked (e.g. asking for 15 hours in a 12 hour day):
    slot_none = scheduler.find_next_available_slot(duration_minutes=900, search_date=search_d)
    assert slot_none is None


def test_task_recurring_lifecycle(sample_pets):
    """Verify DAILY, WEEKLY, and NONE recurrence behaviors and Pet.complete_task integration."""
    pet, _ = sample_pets

    # 1. Non-recurring task
    t_none = Task(title="One-time Nail Trim", recurrence="NONE")
    assert t_none.create_next_occurrence() is None

    # 2. Daily recurring task
    t_daily = Task(
        title="Daily Walk",
        duration_minutes=30,
        priority="high",
        recurrence="DAILY",
        scheduled_datetime=datetime(2026, 10, 15, 8, 0),
    )
    pet.add_task(t_daily)
    assert len(pet.tasks) == 1

    next_daily = pet.complete_task(t_daily.task_id)
    assert next_daily is not None
    assert t_daily.is_completed is True
    assert next_daily.is_completed is False
    assert next_daily.scheduled_datetime == datetime(2026, 10, 16, 8, 0)
    assert next_daily.title == "Daily Walk"
    assert next_daily.priority == "high"
    assert len(pet.tasks) == 2
    assert len(pet.pending_tasks()) == 1

    # 3. Weekly recurring task
    t_weekly = Task(
        title="Weekly Bath",
        duration_minutes=45,
        priority="medium",
        recurrence="WEEKLY",
        scheduled_datetime=datetime(2026, 10, 15, 10, 0),
    )
    pet.add_task(t_weekly)
    next_weekly = pet.complete_task(t_weekly.task_id)
    assert next_weekly is not None
    assert t_weekly.is_completed is True
    assert next_weekly.scheduled_datetime == datetime(2026, 10, 22, 10, 0)


def test_scheduler_conflict_detection():
    """Verify pairwise conflict detection, overlap minute calculation, and completion filtering."""
    scheduler = Scheduler()
    t1 = Task(title="Morning Walk", pet_name="Luna", duration_minutes=45, scheduled_time=time(8, 0))
    t2 = Task(title="Medication & Feeding", pet_name="Mochi", duration_minutes=30, scheduled_time=time(8, 30))
    t3 = Task(title="Afternoon Nap", pet_name="Luna", duration_minutes=60, scheduled_time=time(14, 0))

    conflicts = scheduler.detect_conflicts([t1, t2, t3])
    assert len(conflicts) == 1
    conflict = conflicts[0]
    assert conflict["task_1"] == t1
    assert conflict["task_2"] == t2
    assert conflict["overlap_minutes"] == 15
    assert "[CONFLICT]" in conflict["warning_message"]
    assert "Morning Walk" in conflict["warning_message"]
    assert "Medication & Feeding" in conflict["warning_message"]
    assert "by 15 mins" in conflict["warning_message"]

    # Disregard completed tasks
    t2.mark_complete()
    conflicts_resolved = scheduler.detect_conflicts([t1, t2, t3])
    assert len(conflicts_resolved) == 0
