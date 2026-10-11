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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```text
============================== test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0 -- venv/bin/python
rootdir: /Users/gabrielanokye/AI Engineer/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
collected 10 items

tests/test_pawpal.py::test_task_completion_status PASSED                 [ 10%]
tests/test_pawpal.py::test_pet_task_management PASSED                    [ 20%]
tests/test_pawpal.py::test_owner_task_aggregation PASSED                 [ 30%]
tests/test_pawpal.py::test_scheduler_daily_schedule_ordering PASSED      [ 40%]
tests/test_pawpal.py::test_scheduler_build_plan_budget_filtering PASSED  [ 50%]
tests/test_pawpal.py::test_scheduler_multi_attribute_sorting PASSED      [ 60%]
tests/test_pawpal.py::test_scheduler_multi_criteria_filtering PASSED     [ 70%]
tests/test_pawpal.py::test_scheduler_find_next_available_slot PASSED     [ 80%]
tests/test_pawpal.py::test_task_recurring_lifecycle PASSED               [ 90%]
tests/test_pawpal.py::test_scheduler_conflict_detection PASSED           [100%]

============================== 10 passed in 0.02s ==============================
```

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
