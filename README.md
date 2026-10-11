# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample CLI output from running `python main.py` demonstrating Phase 4 algorithmic capabilities (sorting, cross-pet conflict detection, filtering, recurring tasks, and next available slot finding):

```text
============================================================================
🐾                     PAWPAL+ ALGORITHMIC ENGINE DEMO                      🐾
                Multi-Pet Scheduling, Conflicts & Slot Finder                 
============================================================================

👤 Owner: Alex Carter (alex@example.com)
🐾 Pets Registered: Luna (Golden Retriever) & Mochi (Siamese Cat)
📋 Total Tasks Loaded: 6 across all pets.

▶ STEP A: MULTI-ATTRIBUTE CHRONOLOGICAL SORTING
----------------------------------------------------------------------------
Unsorted Raw Input Order (Tasks as entered):
Scheduled   | Pet       | Priority   | Duration  | Recur    | Status     | Description
----------------------------------------------------------------------------------------
17:00       | Luna      | MEDIUM     | 30 min    | None     | PENDING    | Evening Park Walk
09:00       | Luna      | HIGH       | 45 min    | None     | PENDING    | Morning Walk
08:00       | Luna      | HIGH       | 15 min    | Daily    | PENDING    | Daily Breakfast
09:15       | Mochi     | HIGH       | 30 min    | None     | PENDING    | Vet Check & Vaccine
08:15       | Mochi     | CRITICAL   | 15 min    | Daily    | PENDING    | Insulin Injection
14:00       | Mochi     | LOW        | 20 min    | None     | PENDING    | Coat Brushing
----------------------------------------------------------------------------------------

Chronologically Ordered Schedule (via scheduler.sort_by_time()):
Scheduled   | Pet       | Priority   | Duration  | Recur    | Status     | Description
----------------------------------------------------------------------------------------
08:00       | Luna      | HIGH       | 15 min    | Daily    | PENDING    | Daily Breakfast
08:15       | Mochi     | CRITICAL   | 15 min    | Daily    | PENDING    | Insulin Injection
09:00       | Luna      | HIGH       | 45 min    | None     | PENDING    | Morning Walk
09:15       | Mochi     | HIGH       | 30 min    | None     | PENDING    | Vet Check & Vaccine
14:00       | Mochi     | LOW        | 20 min    | None     | PENDING    | Coat Brushing
17:00       | Luna      | MEDIUM     | 30 min    | None     | PENDING    | Evening Park Walk
----------------------------------------------------------------------------------------
✔ Successfully ordered all tasks from 08:00 AM to 17:00 PM with priority tie-breaking.

▶ STEP B: CROSS-PET CONFLICT DETECTION
----------------------------------------------------------------------------
🔍 Scanning all active commitments for overlapping time windows...
⚠ Found 1 Scheduling Conflict(s):
  [1] [CONFLICT] 'Morning Walk' (Luna, 09:00 - 09:45) overlaps with 'Vet Check & Vaccine' (Mochi, 09:15 - 09:45) by 30 mins.
      ↳ Overlap Window: 30 minutes simultaneous demand.

▶ STEP C: MULTI-CRITERIA FILTERING
----------------------------------------------------------------------------
🔍 Filter 1: Tasks with Priority == 'HIGH'
   • [HIGH] Morning Walk for Luna at 09:00
   • [HIGH] Daily Breakfast for Luna at 08:00
   • [HIGH] Vet Check & Vaccine for Mochi at 09:15

🔍 Filter 2: Tasks assigned specifically to 'Mochi'
   • [HIGH] Vet Check & Vaccine (30 min, scheduled 09:15)
   • [CRITICAL] Insulin Injection (15 min, scheduled 08:15)
   • [LOW] Coat Brushing (20 min, scheduled 14:00)

▶ STEP D: AUTOMATED RECURRING TASK LIFECYCLE
----------------------------------------------------------------------------
Completing recurring task: 'Daily Breakfast' for Luna (Recurrence: DAILY)...

Result of complete_task():
  1. Original Task ID: `9ca5a16a` | Title: 'Daily Breakfast'
     Status: is_completed = True [PRESERVED IN HISTORY]
  2. Next Occurrence ID: `377eec46` | Title: 'Daily Breakfast'
     Status: is_completed = False [SPAWNED FOR NEXT CYCLE]
     New Scheduled Time: 2026-10-12 08:00
✔ Verified: Original task is preserved as DONE; new task spawned automatically for tomorrow!

▶ STEP E: STRETCH FEATURE — NEXT AVAILABLE SLOT FINDER
----------------------------------------------------------------------------
🔍 Searching for earliest continuous free window of 45 minutes on 2026-10-11...
✨ Found Available Window!
   Suggested Start: 2026-10-11 09:45
   Window Range:    09:45 ➔ 10:30 (45 min continuous opening)

============================================================================
🐾                              DEMO COMPLETE                               🐾
            All Phase 4 Algorithmic Features Successfully Verified            
============================================================================
```

## 🧪 Testing PawPal+

### Test Execution

Run the complete automated test suite with verbose reporting from the project root:

```bash
python -m pytest -v
```

### Coverage Summary

The test suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) provides comprehensive unit and integration coverage across all core classes (`Task`, `Pet`, `Owner`, `Scheduler`), validating both primary workflows and critical boundary conditions:

- **Task Lifecycle & Completion**: Verifies default `is_completed=False` initialization, bidirectional toggling via `mark_complete()` and `mark_pending()`, and string description generation.
- **Multi-Attribute Sorting & Tie-Breaking**: Validates that `Scheduler.sort_by_time()` sorts chronologically with priority weighting (`CRITICAL` > `HIGH` > `MEDIUM` > `LOW`) as tie-breaker, and `Scheduler.sort_by_priority()` sorts by urgency with time tie-breaking.
- **Multi-Criteria Filtering Engine**: Validates querying across all household pets by pet name, completion state, and priority tier, as well as gracefully returning empty lists `[]` when no tasks match.
- **Automated Recurrence Engine**: Validates that completing a `DAILY` or `WEEKLY` task marks the original task complete (`is_completed=True`) and automatically spawns the next occurrence scheduled exactly 24 hours (`+ timedelta(days=1)`) or 7 days (`+ timedelta(days=7)`) forward.
- **Month & Midnight Boundary Math**: Tests date math rollover across month transitions (e.g., Oct 31 to Nov 1) and cross-month weekly intervals.
- **Interval Overlap Conflict Detection**: Validates mathematical interval intersection ($\text{start}_A < \text{end}_B \land \text{start}_B < \text{end}_A$), reporting exact overlapping minutes and detailed warning messages.
- **Boundary & Edge Case Protection**:
  - Confirms back-to-back adjacent commitments (`end_A == start_B`) trigger **zero** false-positive conflicts.
  - Confirms completed tasks are disregarded during conflict analysis.
  - Confirms owners with 0 pets or empty schedules execute `collect_all_tasks()`, `sort_by_time()`, and `detect_conflicts()` safely without raising exceptions.
- **Time Budget Filtering & Slot Finding**: Tests `Scheduler.build_plan()` against constrained owner time limits, and verifies `Scheduler.find_next_available_slot()` on both empty and scheduled calendars.

### Terminal Output

```text
$ python -m pytest -v
============================== test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/gabrielanokye/AI Engineer/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 11 items

tests/test_pawpal.py::test_task_lifecycle_and_completion PASSED          [  9%]
tests/test_pawpal.py::test_sorting_chronological_and_priority PASSED     [ 18%]
tests/test_pawpal.py::test_filter_tasks_by_multiple_criteria PASSED      [ 27%]
tests/test_pawpal.py::test_daily_recurrence_generation PASSED            [ 36%]
tests/test_pawpal.py::test_conflict_detection_overlapping_intervals PASSED [ 45%]
tests/test_pawpal.py::test_conflict_detection_edge_cases PASSED          [ 54%]
tests/test_pawpal.py::test_empty_owner_and_edge_conditions PASSED        [ 63%]
tests/test_pawpal.py::test_pet_task_management_edge_cases PASSED         [ 72%]
tests/test_pawpal.py::test_recurrence_across_month_boundary PASSED       [ 81%]
tests/test_pawpal.py::test_scheduler_build_plan_budget_filtering PASSED  [ 90%]
tests/test_pawpal.py::test_scheduler_find_next_available_slot PASSED     [100%]

============================== 11 passed in 0.04s ==============================
```

### System Reliability Confidence Level

**Confidence Rating: ⭐⭐⭐⭐⭐ 5/5**

**Why we have high confidence for real-world usage**:
1. **Mathematical Interval Invariants**: Conflict detection is decoupled from simplistic timestamp equality. By verifying strict interval overlap math ($\text{start}_A < \text{end}_B \land \text{start}_B < \text{end}_A$), the scheduler guarantees that simultaneous demands (such as overlapping dog walks and vet visits) are flagged accurately, while back-to-back touching commitments remain conflict-free.
2. **Defensive Recurrence Lifecycle**: Real-world pet care relies heavily on repeating habits (daily insulin, feeding, medications). Tests verify that recurrence math operates on explicit `datetime` increments across day and month boundaries without silent failures or drift. Furthermore, maintaining completed tasks in history while generating fresh pending occurrences guarantees schedule auditability without state loss.
3. **Graceful Degradation Under Empty States**: Boundary testing ensures that empty user states (0 pets, empty task list, zero conflicts) return safe defaults (`[]` or `None`) without throwing unhandled exceptions.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_time`, `sort_by_priority`, `sort_tasks` | Chronological sorting with priority tie-breaks or priority weighting with earliest-time tie-breaks. |
| Filtering | `filter_tasks`, `filter_by_time` | Multi-criteria filtering by pet, completion status, priority tier, and owner time budget limit. |
| Conflict Detection | `detect_conflicts` | Efficient pairwise overlap checking across all pets; returns warnings and overlap duration in minutes. |
| Automated Recurrence | `complete_task`, `create_next_occurrence` | Preserves completed task in history and generates next cycle occurrence for `DAILY` and `WEEKLY` tasks. |
| Slot Finding | `find_next_available_slot` | Detects gaps between commitments and finds the earliest continuous window of `N` minutes. |
| Daily plan aggregation | `build_plan`, `get_daily_schedule` | Automatically projects routines across all pets starting from owner day start with explainability. |

### Smarter Scheduling Features

PawPal+ includes an algorithmic scheduling engine implemented in `pawpal_system.py`:

1. **Chronological & Priority Sorting (`Scheduler.sort_by_time`, `Scheduler.sort_by_priority`)**:
   - `Scheduler.sort_by_time`: Orders commitments chronologically by `scheduled_time`. When two tasks share identical start times, it intelligently breaks ties using priority weights (`CRITICAL: 4` > `HIGH: 3` > `MEDIUM: 2` > `LOW: 1`).
   - `Scheduler.sort_by_priority`: Sorts primarily by descending priority weight, resolving ties by earliest scheduled time to ensure urgent health/medication routines take precedence.

2. **Multi-Criteria Filter Engine (`Scheduler.filter_tasks`)**:
   - Aggregates tasks across all pets registered under the `Owner` and supports concurrent filtering by `pet_name` (case-insensitive substring match), completion state (`is_completed=True/False`), and priority tier (`"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`).

3. **Recurrence Engine (`Task.create_next_occurrence`, `Pet.complete_task`)**:
   - Automates repeating routines (`"DAILY"` or `"WEEKLY"`). When `Pet.complete_task(task_id)` or `Scheduler.complete_task(task_id)` is called:
     - The original task is preserved in historical records with `is_completed=True`.
     - If `recurrence == "DAILY"`, `create_next_occurrence()` generates a new pending task scheduled exactly 24 hours later (`+ timedelta(days=1)`).
     - If `recurrence == "WEEKLY"`, the new occurrence is scheduled 7 days later (`+ timedelta(days=7)`).
     - The new occurrence is automatically appended to the pet's active task list.

4. **Interval Overlap Conflict Detection (`Scheduler.detect_conflicts`)**:
   - Evaluates active (pending) time windows across all pets simultaneously using the mathematical interval intersection invariant:
     $$\text{start}_A < \text{end}_B \quad \text{and} \quad \text{start}_B < \text{end}_A$$
   - Executes in $O(n \log n)$ time by first sorting commitments by start time, enabling inner-loop early termination as soon as candidate task start exceeds the current task's end window.
   - Returns structured records with exact overlap duration in minutes and user-facing warning banners (e.g., `"[CONFLICT] 'Morning Walk' (Luna, 09:00 - 09:45) overlaps with 'Vet Check & Vaccine' (Mochi, 09:15 - 09:45) by 30 mins."`).

5. **Next Open Slot Finder (`Scheduler.find_next_available_slot`)**:
   - Scans the calendar on a given search date from `owner.day_start` (default 08:00 AM) through the evening.
   - Computes open time windows between existing commitments and returns the earliest continuous slot of `duration_minutes` where no cross-pet conflicts occur.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
