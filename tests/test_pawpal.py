"""Automated Production-Grade Pytest Suite for PawPal+ System.

Covers:
- Task lifecycle and completion state management
- Multi-attribute chronological and priority sorting with tie-breaking
- Multi-criteria filtering (pet, completion status, priority, empty matches)
- Automated recurring task lifecycle (daily & weekly forward scheduling across month boundaries)
- Cross-pet interval overlap conflict detection & edge cases (touching borders, completed tasks)
- Edge conditions (empty owner, zero pets, empty tasks)
- Time budget constrained plan building and next available slot finding
"""

from datetime import date, datetime, time, timedelta
import pytest
from pawpal_system import (
    PRIORITY_WEIGHTS,
    Owner,
    Pet,
    Scheduler,
    Task,
    load_from_json,
    save_to_json,
)


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------

@pytest.fixture
def sample_owner() -> Owner:
    """Returns an Owner with 2 Pets ('Luna' and 'Mochi') and pre-configured tasks."""
    owner = Owner(
        name="Alex Carter",
        email="alex@example.com",
        contact="alex@example.com",
        available_minutes=180,
        day_start=time(8, 0),
    )
    luna = Pet(name="Luna", species="Dog", breed="Golden Retriever", age_years=3.0, pet_id="pet_1")
    mochi = Pet(name="Mochi", species="Cat", breed="Siamese Cat", age_years=2.0, pet_id="pet_2")

    # Pre-configured tasks with distinct times, durations, and priorities
    t_walk = Task(
        title="Morning Walk",
        duration_minutes=30,
        priority="high",
        category="walk",
        scheduled_time=time(8, 30),
    )
    t_breakfast = Task(
        title="Breakfast",
        duration_minutes=15,
        priority="medium",
        category="feeding",
        scheduled_time=time(9, 0),
    )
    t_insulin = Task(
        title="Insulin Injection",
        duration_minutes=15,
        priority="critical",
        category="medication",
        scheduled_time=time(8, 15),
    )

    luna.add_task(t_walk)
    luna.add_task(t_breakfast)
    mochi.add_task(t_insulin)

    owner.add_pet(luna)
    owner.add_pet(mochi)
    return owner


@pytest.fixture
def scheduler(sample_owner: Owner) -> Scheduler:
    """Returns a Scheduler pre-linked to sample_owner."""
    return Scheduler(owner=sample_owner)


# -----------------------------------------------------------------------------
# REQUIRED TEST FUNCTIONS
# -----------------------------------------------------------------------------

def test_task_lifecycle_and_completion():
    """Verify task completion transitions from default False, to True, and back to False."""
    task = Task(title="Evening Walk", duration_minutes=30, priority="high")

    # 1. Assert default initial state is not completed
    assert task.is_completed is False, "Task should initialize with is_completed=False"
    assert task.completed is False, "Task should maintain backwards-compatible completed=False"

    # 2. Assert mark_complete() toggles status to True
    task.mark_complete()
    assert task.is_completed is True, "Task.mark_complete() should set is_completed=True"
    assert task.completed is True, "Task.mark_complete() should set completed=True"

    # 3. Assert mark_pending() reverts status to False
    task.mark_pending()
    assert task.is_completed is False, "Task.mark_pending() should set is_completed=False"
    assert task.completed is False, "Task.mark_pending() should set completed=False"


def test_sorting_chronological_and_priority(scheduler: Scheduler):
    """Verify multi-attribute chronological sorting and priority sorting with tie-breaking."""
    # Tasks added in intentionally scrambled order
    t_evening = Task(title="Evening Walk", duration_minutes=30, scheduled_time=time(17, 0), priority="medium")
    t_noon = Task(title="Midday Nap", duration_minutes=20, scheduled_time=time(12, 0), priority="low")
    t_morn_low = Task(title="Morning Play", duration_minutes=15, scheduled_time=time(9, 0), priority="low")
    t_morn_high = Task(title="Vet Visit", duration_minutes=45, scheduled_time=time(9, 0), priority="high")
    t_early = Task(title="Early Stroll", duration_minutes=25, scheduled_time=time(8, 0), priority="medium")

    scrambled = [t_evening, t_morn_low, t_early, t_noon, t_morn_high]

    # 1. Test chronological sorting with priority tie-breaker at 09:00 (high > low)
    time_sorted = scheduler.sort_by_time(scrambled)
    assert time_sorted == [t_early, t_morn_high, t_morn_low, t_noon, t_evening], (
        f"Expected strictly chronological order with tie-breaking, got: {[t.title for t in time_sorted]}"
    )
    # Explicitly check the tie-breaker at 09:00
    assert time_sorted[1] == t_morn_high, "At equal time 09:00, HIGH priority must precede LOW priority"
    assert time_sorted[2] == t_morn_low

    # 2. Test priority sorting: HIGH > MEDIUM > LOW, with time as tiebreaker
    prio_sorted = scheduler.sort_by_priority(scrambled)
    expected_prio = [t_morn_high, t_early, t_evening, t_morn_low, t_noon]
    assert prio_sorted == expected_prio, (
        f"Expected priority-first ordering with time tiebreaker, got: {[t.title for t in prio_sorted]}"
    )


def test_filter_tasks_by_multiple_criteria(sample_owner: Owner, scheduler: Scheduler):
    """Verify filtering tasks by pet name, status (is_completed), priority, and empty matches."""
    # Pre-state: Luna has Morning Walk (high), Breakfast (medium); Mochi has Insulin (critical)
    # Mark Luna's Breakfast as completed
    luna = sample_owner.pets[0]
    breakfast_task = [t for t in luna.tasks if t.title == "Breakfast"][0]
    breakfast_task.mark_complete()

    # 1. Filter by pet name
    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    assert len(luna_tasks) == 2, f"Expected 2 tasks for Luna, got {len(luna_tasks)}"
    assert all(t.pet_name == "Luna" for t in luna_tasks), "All filtered tasks must belong to Luna"

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    assert len(mochi_tasks) == 1, f"Expected 1 task for Mochi, got {len(mochi_tasks)}"
    assert mochi_tasks[0].title == "Insulin Injection"

    # 2. Filter by completion status
    completed_tasks = scheduler.filter_tasks(is_completed=True)
    assert len(completed_tasks) == 1, "Only Breakfast should be completed"
    assert completed_tasks[0].title == "Breakfast"

    pending_tasks = scheduler.filter_tasks(is_completed=False)
    assert len(pending_tasks) == 2, "2 tasks should remain pending"

    # 3. Filter by priority tier
    high_tasks = scheduler.filter_tasks(priority="high")
    assert len(high_tasks) == 1 and high_tasks[0].title == "Morning Walk"

    crit_tasks = scheduler.filter_tasks(priority="critical")
    assert len(crit_tasks) == 1 and crit_tasks[0].title == "Insulin Injection"

    # 4. Filter when no tasks match (assert returns empty list [])
    no_pet = scheduler.filter_tasks(pet_name="NonExistentPet")
    assert no_pet == [], f"Expected empty list for nonexistent pet, got {no_pet}"

    no_prio = scheduler.filter_tasks(priority="low")
    assert no_prio == [], f"Expected empty list for nonexistent priority tier, got {no_prio}"

    no_match = scheduler.filter_tasks(pet_name="Luna", priority="critical")
    assert no_match == [], f"Expected empty list for conflicting filter criteria, got {no_match}"


def test_daily_recurrence_generation(sample_owner: Owner):
    """Verify daily recurring task completion spawns a new task scheduled exactly 24 hours later."""
    luna = sample_owner.pets[0]
    initial_count = len(luna.tasks)

    # Create a task with recurrence="DAILY"
    base_time = datetime(2026, 10, 15, 8, 30)
    daily_task = Task(
        title="Daily Morning Walk",
        duration_minutes=30,
        priority="high",
        category="walk",
        recurrence="DAILY",
        scheduled_time=time(8, 30),
        scheduled_datetime=base_time,
    )
    luna.add_task(daily_task)
    assert len(luna.tasks) == initial_count + 1

    # Complete it via pet.complete_task(task.task_id)
    next_task = luna.complete_task(daily_task.task_id)

    # 1. Assert the original task is marked complete
    assert daily_task.is_completed is True, "Original task must be marked complete"
    assert daily_task.completed is True, "Backwards-compatible completed must be True"

    # 2. Assert a new task was generated and returned
    assert next_task is not None, "pet.complete_task must return the newly spawned occurrence"
    assert next_task.is_completed is False, "Newly spawned occurrence must be pending"

    # 3. Assert new task was added to pet.tasks scheduled exactly 24 hours later (timedelta(days=1))
    assert len(luna.tasks) == initial_count + 2, "pet.tasks should contain both original and next occurrence"
    expected_new_datetime = base_time + timedelta(days=1)
    assert next_task.scheduled_datetime == expected_new_datetime, (
        f"Expected scheduled_datetime {expected_new_datetime}, got {next_task.scheduled_datetime}"
    )
    assert next_task.scheduled_time == time(8, 30), "Scheduled time of day must be preserved"
    assert next_task.title == "Daily Morning Walk", "Task metadata must be retained"
    assert next_task.priority == "high"
    assert next_task.recurrence == "DAILY"


def test_conflict_detection_overlapping_intervals(scheduler: Scheduler):
    """Verify scheduler.detect_conflicts() detects overlapping intervals and calculates overlap duration."""
    # Task A: 09:00 - 09:45 (45 min)
    task_a = Task(
        title="Luna Park Walk",
        pet_name="Luna",
        duration_minutes=45,
        scheduled_time=time(9, 0),
    )
    # Task B: 09:30 - 10:00 (30 min) -> Overlap from 09:30 to 09:45 = 15 mins
    task_b = Task(
        title="Mochi Vet Exam",
        pet_name="Mochi",
        duration_minutes=30,
        scheduled_time=time(9, 30),
    )

    conflicts = scheduler.detect_conflicts([task_a, task_b])

    assert len(conflicts) == 1, f"Expected 1 conflict detected, found {len(conflicts)}"
    conflict = conflicts[0]
    assert conflict["task_1"] == task_a
    assert conflict["task_2"] == task_b
    assert conflict["overlap_minutes"] == 15, f"Expected 15 minutes overlap, got {conflict['overlap_minutes']}"
    assert "[CONFLICT]" in conflict["warning_message"]
    assert "Luna Park Walk" in conflict["warning_message"]
    assert "Mochi Vet Exam" in conflict["warning_message"]
    assert "by 15 mins" in conflict["warning_message"]


def test_conflict_detection_edge_cases(scheduler: Scheduler):
    """Verify edge cases: back-to-back touching boundaries and completed tasks produce NO conflicts."""
    # Case 1: Back-to-back tasks where end time equals next start time:
    # Task 1: 09:00 - 09:30 (30 min, ends exactly at 09:30)
    # Task 2: 09:30 - 10:00 (30 min, starts exactly at 09:30)
    t_first = Task(title="Luna Breakfast", pet_name="Luna", duration_minutes=30, scheduled_time=time(9, 0))
    t_second = Task(title="Mochi Grooming", pet_name="Mochi", duration_minutes=30, scheduled_time=time(9, 30))

    touching_conflicts = scheduler.detect_conflicts([t_first, t_second])
    assert len(touching_conflicts) == 0, (
        f"Back-to-back tasks (09:00-09:30 and 09:30-10:00) should NOT conflict! Got: {touching_conflicts}"
    )

    # Case 2: Completed overlapping tasks:
    # Overlapping tasks (09:00-09:45 and 09:30-10:00) where one task is marked complete
    t_overlap_a = Task(title="Walk A", pet_name="Luna", duration_minutes=45, scheduled_time=time(9, 0))
    t_overlap_b = Task(title="Walk B", pet_name="Mochi", duration_minutes=30, scheduled_time=time(9, 30))

    # Before completion: 1 conflict
    assert len(scheduler.detect_conflicts([t_overlap_a, t_overlap_b])) == 1

    # Mark t_overlap_a complete: must be ignored by conflict detector
    t_overlap_a.mark_complete()
    resolved_conflicts = scheduler.detect_conflicts([t_overlap_a, t_overlap_b])
    assert len(resolved_conflicts) == 0, (
        f"Completed tasks must be ignored during conflict detection! Got: {resolved_conflicts}"
    )


def test_empty_owner_and_edge_conditions():
    """Verify Owner with 0 pets and empty scheduler methods handle edge cases without raising exceptions."""
    empty_owner = Owner(name="Solo Owner", email="solo@example.com", available_minutes=120)
    assert len(empty_owner.pets) == 0, "Owner should have 0 pets initially"

    scheduler_empty = Scheduler(owner=empty_owner)

    # 1. Assert scheduler.collect_all_tasks() returns [] without raising an exception
    collected = scheduler_empty.collect_all_tasks()
    assert collected == [], f"Expected [] from empty owner collect_all_tasks, got {collected}"

    # 2. Assert owner.get_all_tasks() returns []
    assert empty_owner.get_all_tasks() == []

    # 3. Assert algorithmic methods handle empty task collections safely
    assert scheduler_empty.detect_conflicts() == []
    assert scheduler_empty.sort_by_time() == []
    assert scheduler_empty.sort_by_priority() == []
    assert scheduler_empty.filter_tasks(pet_name="Luna") == []
    assert scheduler_empty.get_daily_schedule() == []


# -----------------------------------------------------------------------------
# ADDITIONAL PRODUCTION-GRADE COVERAGE TESTS
# -----------------------------------------------------------------------------

def test_pet_task_management_edge_cases():
    """Verify adding, removing, and attempting to remove nonexistent tasks from Pet."""
    pet = Pet(name="Luna", species="Dog", breed="Labrador", age_years=3.0)
    assert len(pet.tasks) == 0

    t1 = Task(title="Morning Feeding", duration_minutes=15, priority="high")
    t2 = Task(title="Brush Coat", duration_minutes=20, priority="medium")
    pet.add_task(t1)
    pet.add_task(t2)
    assert len(pet.tasks) == 2
    assert t1.pet_name == "Luna"

    # Remove valid task
    removed = pet.remove_task(t1.task_id)
    assert removed is True
    assert len(pet.tasks) == 1
    assert t1 not in pet.tasks

    # Attempt to remove nonexistent task id
    removed_fake = pet.remove_task("nonexistent_id_1234")
    assert removed_fake is False
    assert len(pet.tasks) == 1

    # Attempt to complete nonexistent task
    res_fake = pet.complete_task("nonexistent_id_1234")
    assert res_fake is None


def test_recurrence_across_month_boundary():
    """Verify daily and weekly recurrence calculations correctly handle month/year roll-overs."""
    pet = Pet(name="Mochi", species="Cat", breed="Siamese Cat", age_years=2.0)

    # Daily rollover on October 31 -> November 1
    t_halloween = Task(
        title="Night Feeding",
        duration_minutes=15,
        recurrence="DAILY",
        scheduled_datetime=datetime(2026, 10, 31, 23, 30),
    )
    pet.add_task(t_halloween)
    next_daily = pet.complete_task(t_halloween.task_id)
    assert next_daily is not None
    assert next_daily.scheduled_datetime == datetime(2026, 11, 1, 23, 30), (
        "Daily recurrence must rollover into the next month cleanly"
    )

    # Weekly rollover from October 28 -> November 4
    t_oct_weekly = Task(
        title="Weekly Bath",
        duration_minutes=45,
        recurrence="WEEKLY",
        scheduled_datetime=datetime(2026, 10, 28, 10, 0),
    )
    pet.add_task(t_oct_weekly)
    next_weekly = pet.complete_task(t_oct_weekly.task_id)
    assert next_weekly is not None
    assert next_weekly.scheduled_datetime == datetime(2026, 11, 4, 10, 0), (
        "Weekly recurrence must add 7 days across month boundaries"
    )


def test_scheduler_build_plan_budget_filtering(sample_owner: Owner, scheduler: Scheduler):
    """Verify build_plan respects owner time budget and drops lowest priority tasks."""
    # Constrain owner budget to 45 minutes
    sample_owner.available_minutes = 45

    plan = scheduler.build_plan(sample_owner)
    scheduled = plan["scheduled"]
    skipped = plan["skipped"]

    # In sample_owner:
    # Insulin Injection (15 min, critical) + Morning Walk (30 min, high) = 45 min
    # Breakfast (15 min, medium) should be skipped
    assert len(scheduled) == 2
    assert plan["minutes_used"] == 45
    assert any(t.title == "Insulin Injection" for t in scheduled)
    assert any(t.title == "Morning Walk" for t in scheduled)
    assert any(t.title == "Breakfast" for t in skipped)


def test_scheduler_find_next_available_slot(sample_owner: Owner, scheduler: Scheduler):
    """Verify find_next_available_slot on empty calendar vs calendar with commitments."""
    search_d = date(2026, 10, 20)

    # Calendar with commitments: Luna has Morning Walk (08:30-09:00), Mochi has Insulin (08:15-08:30)
    # Owner day start is 08:00. Window 08:00-08:15 is 15 mins.
    # Gap after 09:15 (Breakfast is 09:00-09:15) opens at 09:15.
    slot_30 = scheduler.find_next_available_slot(duration_minutes=30, search_date=search_d)
    assert slot_30 == datetime(2026, 10, 20, 9, 15)

    # Empty calendar test: create empty scheduler
    empty_owner = Owner(name="Clean Slate", email="clean@example.com", day_start=time(8, 0))
    sched_empty = Scheduler(owner=empty_owner)
    slot_empty = sched_empty.find_next_available_slot(duration_minutes=45, search_date=search_d)
    assert slot_empty == datetime(2026, 10, 20, 8, 0), "Empty schedule should suggest day_start"


def test_find_next_available_slot_challenge_1():
    """Verify Challenge 1 requirements: target_date signature, interval merging, and gap detection."""
    target_d = date(2026, 10, 25)
    owner = Owner(name="Alex Rivera", day_start=time(8, 0))
    pet_a = Pet(name="Luna", species="Dog")
    pet_b = Pet(name="Mochi", species="Cat")

    # Overlapping tasks that must merge into a single busy interval: [08:00, 09:15]
    t1 = Task(
        title="Luna Morning Walk",
        duration_minutes=45,
        scheduled_time=time(8, 0),
        scheduled_datetime=datetime(2026, 10, 25, 8, 0),
    )
    t2 = Task(
        title="Mochi Vet Check",
        duration_minutes=45,
        scheduled_time=time(8, 30),
        scheduled_datetime=datetime(2026, 10, 25, 8, 30),
    )
    # A completed task that should be IGNORED (10:00 - 11:00)
    t_completed = Task(
        title="Completed Grooming",
        duration_minutes=60,
        completed=True,
        scheduled_time=time(10, 0),
        scheduled_datetime=datetime(2026, 10, 25, 10, 0),
    )

    pet_a.add_task(t1)
    pet_b.add_task(t2)
    pet_a.add_task(t_completed)
    owner.add_pet(pet_a)
    owner.add_pet(pet_b)

    scheduler = Scheduler(owner=owner)

    # 1. Test target_date signature with interval merging:
    # Gap after merged busy block [08:00, 09:15] opens at 09:15:
    slot = scheduler.find_next_available_slot(
        duration_minutes=30,
        target_date=target_d,
        day_start=time(8, 0),
        day_end=time(20, 0),
    )
    assert slot == datetime(2026, 10, 25, 9, 15), f"Expected 09:15, got {slot}"

    # Verify when scheduled_time is passed as a pure datetime object
    t3 = Task(
        title="Luna Afternoon Training",
        duration_minutes=60,
        scheduled_time=datetime(2026, 10, 25, 14, 0),
    )
    pet_a.add_task(t3)
    slot_afternoon = scheduler.find_next_available_slot(
        duration_minutes=60,
        target_date=target_d,
        day_start=time(13, 0),
        day_end=time(16, 0),
    )
    # Window 13:00 to 14:00 is 60 min, so earliest slot is 13:00
    assert slot_afternoon == datetime(2026, 10, 25, 13, 0)

    # 2. Test when operating hours cannot accommodate the requested duration:
    slot_impossible = scheduler.find_next_available_slot(
        duration_minutes=1200,  # 20 hours exceeds daily window
        target_date=target_d,
        day_start=time(8, 0),
        day_end=time(20, 0),
    )
    assert slot_impossible is None, "Should return None when no window fits inside operating hours"



def test_persistence_json_serialization(tmp_path, sample_owner: Owner):
    """Verify JSON persistence layer: to_dict, from_dict, save_to_json, and load_from_json."""
    file_path = tmp_path / "owner_data.json"

    # 1. Test top-level save_to_json and load_from_json
    save_to_json(sample_owner, str(file_path))
    assert file_path.exists(), "JSON file should be created"

    loaded_owner = load_from_json(str(file_path))

    # Assert structural integrity and data equality
    assert loaded_owner.name == sample_owner.name
    assert loaded_owner.contact == sample_owner.contact
    assert loaded_owner.available_minutes == sample_owner.available_minutes
    assert loaded_owner.day_start == sample_owner.day_start
    assert len(loaded_owner.pets) == len(sample_owner.pets)

    # Check pet tasks round-trip fidelity
    orig_tasks = sample_owner.get_all_tasks(pending_only=False)
    loaded_tasks = loaded_owner.get_all_tasks(pending_only=False)
    assert len(loaded_tasks) == len(orig_tasks)
    assert [t.title for t in loaded_tasks] == [t.title for t in orig_tasks]
    assert [t.priority for t in loaded_tasks] == [t.priority for t in orig_tasks]

    # 2. Test missing file graceful fallback (returns default Owner)
    missing_file = tmp_path / "does_not_exist.json"
    default_owner = load_from_json(str(missing_file))
    assert isinstance(default_owner, Owner)
    assert default_owner.name != ""

    # 3. Test Task to_dict and from_dict with ISO formatted datetimes
    task_with_dt = Task(
        title="Emergency Vet",
        duration_minutes=45,
        priority="critical",
        scheduled_time=time(14, 30),
        scheduled_datetime=datetime(2026, 10, 25, 14, 30),
    )
    t_dict = task_with_dt.to_dict()
    assert t_dict["scheduled_datetime"] == "2026-10-25T14:30:00"
    restored_task = Task.from_dict(t_dict)
    assert restored_task.title == "Emergency Vet"
    assert restored_task.scheduled_datetime == datetime(2026, 10, 25, 14, 30)
    assert restored_task.duration_minutes == 45

    # 4. Test Pet to_dict and from_dict
    pet = Pet(name="Bella", species="Dog", breed="Beagle", age_years=4.0)
    pet.add_task(task_with_dt)
    p_dict = pet.to_dict()
    restored_pet = Pet.from_dict(p_dict)
    assert restored_pet.name == "Bella"
    assert len(restored_pet.tasks) == 1
    assert restored_pet.tasks[0].title == "Emergency Vet"


def test_priority_scheduling_challenge_3():
    """Verify Challenge 3 requirements:
    1. PRIORITY_WEIGHTS mapping (HIGH: 3, MEDIUM: 2, LOW: 1).
    2. Primary key: priority weight descending (HIGH first).
    3. Secondary key: chronological scheduled_time ascending.
    4. Incomplete tasks first, completed tasks pushed to bottom.
    """
    assert PRIORITY_WEIGHTS["HIGH"] == 3
    assert PRIORITY_WEIGHTS["MEDIUM"] == 2
    assert PRIORITY_WEIGHTS["LOW"] == 1

    scheduler = Scheduler()

    t_low_noon = Task(title="Brush Coat", priority="LOW", scheduled_time=time(12, 0))
    t_low_morn = Task(title="Trim Nails", priority="LOW", scheduled_time=time(9, 0))
    t_med_aft = Task(title="Park Walk", priority="MEDIUM", scheduled_time=time(16, 0))
    t_med_morn = Task(title="Breakfast", priority="MEDIUM", scheduled_time=time(8, 0))
    t_high_late = Task(title="Vet Visit", priority="HIGH", scheduled_time=time(11, 0))
    t_high_early = Task(title="Insulin Dose", priority="HIGH", scheduled_time=time(7, 30))
    # Completed task - even though HIGH priority and early, must be pushed to bottom
    t_high_done = Task(title="Morning Pill", priority="HIGH", scheduled_time=time(6, 0), completed=True)

    scrambled = [
        t_low_noon,
        t_high_done,
        t_med_aft,
        t_high_late,
        t_low_morn,
        t_high_early,
        t_med_morn,
    ]

    sorted_tasks = scheduler.sort_by_priority(scrambled)

    # Expected order:
    # 1. Incomplete HIGH: t_high_early (07:30), t_high_late (11:00)
    # 2. Incomplete MEDIUM: t_med_morn (08:00), t_med_aft (16:00)
    # 3. Incomplete LOW: t_low_morn (09:00), t_low_noon (12:00)
    # 4. Completed: t_high_done (06:00) pushed to bottom!
    expected = [
        t_high_early,
        t_high_late,
        t_med_morn,
        t_med_aft,
        t_low_morn,
        t_low_noon,
        t_high_done,
    ]

    assert sorted_tasks == expected, (
        f"Expected {[t.title for t in expected]}, got {[t.title for t in sorted_tasks]}"
    )


def test_cli_formatting_helpers_challenge_4(capsys):
    """Verify Challenge 4 Professional UI & Output Formatting:
    1. Emoji indicators for Priority: HIGH = '🚨 HIGH', MEDIUM = '⚡ MEDIUM', LOW = '🌱 LOW'.
    2. Status badges: COMPLETED = '✅ Done', PENDING = '⏳ Pending'.
    3. Category emojis: Walk = '🦮', Medication = '💊', Meal = '🍖', Vet = '🩺'.
    4. Table and block printers render without exceptions.
    """
    from main import (
        get_category_emoji,
        get_priority_badge,
        get_status_badge,
        print_conflict_block,
        print_slot_block,
        print_table,
    )

    # 1. Emoji category mapping
    t_walk = Task(title="Morning Walk", category="walk")
    t_med = Task(title="Insulin Injection", category="medication")
    t_meal = Task(title="Evening Meal", category="feeding")
    t_vet = Task(title="Vet Visit", category="appointment")
    assert get_category_emoji(t_walk) == "🦮"
    assert get_category_emoji(t_med) == "💊"
    assert get_category_emoji(t_meal) == "🍖"
    assert get_category_emoji(t_vet) == "🩺"

    # 2. Priority badges
    assert "🚨 HIGH" in get_priority_badge("HIGH")
    assert "⚡ MEDIUM" in get_priority_badge("MEDIUM")
    assert "🌱 LOW" in get_priority_badge("LOW")

    # 3. Status badges
    assert "✅ Done" in get_status_badge(True)
    assert "⏳ Pending" in get_status_badge(False)

    # 4. Table and block rendering
    print_table([t_walk, t_med], title="Test Table")
    captured = capsys.readouterr().out
    assert "Status" in captured
    assert "Time" in captured
    assert "Pet" in captured
    assert "Task" in captured
    assert "Duration" in captured
    assert "Priority" in captured
    assert "🦮 Morning Walk" in captured

    # Conflict block
    conflict = {
        "task_1": t_walk,
        "task_2": t_med,
        "overlap_minutes": 15,
        "warning_message": "Overlapping window",
    }
    print_conflict_block([conflict])
    captured_conflict = capsys.readouterr().out
    assert "SCHEDULING CONFLICT DETECTED" in captured_conflict
    assert "15 minutes" in captured_conflict

    # Slot block
    print_slot_block(datetime(2026, 10, 11, 10, 0), 45, date(2026, 10, 11))
    captured_slot = capsys.readouterr().out
    assert "OPTIMAL FREE CARE WINDOW RECOMMENDED" in captured_slot
    assert "45 min continuous" in captured_slot



