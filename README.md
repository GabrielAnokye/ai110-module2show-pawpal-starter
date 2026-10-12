# PawPal+ Smart Pet Care Management System

> **A smart, object-oriented pet care coordination platform and algorithmic scheduling engine designed for busy multi-pet households.**

PawPal+ combines a rigorous Object-Oriented Programming (OOP) domain model with intelligent scheduling algorithms and an interactive Streamlit dashboard. It eliminates care bottlenecks, catches scheduling conflicts across multiple pets, tracks daily time budgets, and automates recurring wellness routines (feeding, walks, medications, and vet visits).

### 🛠️ Technology Stack
- **Language**: Python 3.10+ / 3.14
- **Architecture**: Object-Oriented Domain Model (Python Dataclasses)
- **User Interface**: Streamlit (Modern Dashboard with Custom Design System & Glassmorphism Badges)
- **Testing & Verification**: Pytest 9.x (Comprehensive Unit & Boundary Test Suite)
- **Modeling & Diagramming**: Mermaid.js Class Architecture (`diagrams/uml_final.mmd`)

---

## 🏛️ Architecture & System Design

PawPal+ is architected around 4 decoupled primary domain classes and standard enumeration types:

1. **`Owner`**: Manages caregiver profile data, contact details, daily time budget constraints (`available_minutes`), operating day start time (`day_start`), and a composition collection of registered pets. Aggregates tasks across all household pets via `get_all_tasks()`.
2. **`Pet`**: Encapsulates animal profile metadata (name, species, breed, age, notes) and manages an internal collection of care tasks. Provides lifecycle methods `add_task()`, `remove_task()`, `pending_tasks()`, and `complete_task()`.
3. **`Task`**: Represents an atomic unit of pet care. Tracks title, description, category (`walk`, `feeding`, `medication`, `appointment`, `grooming`), duration in minutes, priority tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), preferred/scheduled times, completion states (`completed`, `is_completed`), and recurrence rules (`NONE`, `DAILY`, `WEEKLY`).
4. **`Scheduler`**: The algorithmic logic engine. Operates across multi-pet household collections to execute multi-attribute chronological sorting, multi-criteria filtering, O(n log n) interval overlap conflict detection, recurring lifecycle progression, and next available continuous free slot recommendation.

### 📐 Mermaid Class Diagram (`diagrams/uml_final.mmd`)

```mermaid
classDiagram
    %% PawPal+ — Final Production Object-Oriented Domain Model & Architecture
    %% Generated for diagrams/uml_final.mmd

    class TaskPriority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
        CRITICAL
    }

    class TaskStatus {
        <<enumeration>>
        PENDING
        COMPLETED
    }

    class Owner {
        +name : str
        +email : str
        +contact : str
        +available_minutes : int
        +day_start : time
        +pets : List~Pet~
        +add_pet(pet : Pet) : void
        +remove_pet(pet_name : str) : bool
        +get_pet(pet_name : str) : Pet
        +get_all_tasks(pending_only : bool) : List~Task~
    }

    class Pet {
        +name : str
        +species : str
        +breed : str
        +age_years : float
        +notes : str
        +pet_id : str
        +tasks : List~Task~
        +add_task(task : Task) : void
        +remove_task(task_id : str) : bool
        +update_task(task_id : str, fields : dict) : Task
        +pending_tasks() : List~Task~
        +get_pending_tasks() : List~Task~
        +complete_task(task_id : str) : Optional~Task~
    }

    class Task {
        +task_id : str
        +title : str
        +description : str
        +category : str
        +duration_minutes : int
        +priority : str
        +preferred_time : Optional~time~
        +completed : bool
        +is_completed : bool
        +start_time : Optional~time~
        +scheduled_time : Optional~time~
        +scheduled_datetime : Optional~datetime~
        +pet_name : str
        +recurrence : str
        +weight() : float
        +create_next_occurrence() : Optional~Task~
        +mark_complete() : Optional~Task~
        +mark_pending() : void
        +describe() : str
    }

    class Scheduler {
        +strategy : str
        +owner : Optional~Owner~
        +tasks : List~Task~
        +add_task(task : Task) : void
        +complete_task(task_id : str) : Optional~Task~
        +build_plan(owner : Optional~Owner~, pets : Any) : dict
        +sort_tasks(tasks : List~Task~) : List~Task~
        +filter_by_time(tasks : List~Task~, budget : int) : List~Task~
        +assign_times(tasks : List~Task~, day_start : time) : List~Task~
        +get_daily_schedule(target : Any) : List~Task~
        +collect_all_tasks() : List~Task~
        +sort_by_time(tasks : List~Task~) : List~Task~
        +sort_by_priority(tasks : List~Task~) : List~Task~
        +filter_tasks(pet_name : str, is_completed : bool, priority : str) : List~Task~
        +find_next_available_slot(duration_minutes : int, search_date : date) : Optional~datetime~
        +detect_conflicts(tasks : List~Task~) : List~dict~
        +explain(plan : dict) : str
    }

    %% Relationships and Cardinalities
    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : assigned to
    Scheduler o-- "0..1" Owner : manages
    Scheduler ..> Task : processes / sorts
    Task ..> TaskPriority : categorized by
    Task ..> TaskStatus : tracks state with
```

---

## ⚡ Smarter Scheduling Features

PawPal+ includes an algorithmic scheduling engine implemented in `pawpal_system.py`:

- **Multi-Key Sorting & Priority-Based Scheduling (`Scheduler.sort_by_time`, `Scheduler.sort_by_priority`)**:
  - `Scheduler.sort_by_time`: Orders commitments chronologically by `scheduled_time`. If two tasks share the same start time, it intelligently tie-breaks using descending priority weights (`HIGH: 3` > `MEDIUM: 2` > `LOW: 1`).
  - `Scheduler.sort_by_priority`: Priority-Based Scheduling engine implementing a strict 3-tier sort strategy:
    1. *Status Partition*: Incomplete/pending tasks first; completed tasks pushed to bottom.
    2. *Primary Key*: Priority weight descending (`HIGH: 3` > `MEDIUM: 2` > `LOW: 1`).
    3. *Secondary Key*: Earliest scheduled time ascending (`scheduled_time`), ensuring critical routines run first while respecting daily chronology.

- **Multi-Criteria Filtering (`Scheduler.filter_tasks`)**:
  - Aggregates tasks across all pets registered under the `Owner` and supports concurrent, combinable filtering by `pet_name` (case-insensitive substring match), completion state (`is_completed=True/False`), and priority tier (`"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"`). Returns an empty list `[]` when no matches exist without throwing exceptions.

- **Automated Recurrence Engine (`Task.create_next_occurrence`, `Pet.complete_task`)**:
  - Automates repeating routines (`"DAILY"` or `"WEEKLY"`). When `Pet.complete_task(task_id)` or `Scheduler.complete_task(task_id)` is executed:
    - The original task is preserved in historical records as completed (`is_completed=True`) for full auditability.
    - If `recurrence == "DAILY"`, `create_next_occurrence()` instantiates a fresh pending task scheduled exactly 24 hours forward (`+ timedelta(days=1)`).
    - If `recurrence == "WEEKLY"`, the new occurrence is scheduled 7 days forward (`+ timedelta(days=7)`).
    - The new task is automatically appended to the pet's active task list.

- **Interval Overlap Conflict Detection (`Scheduler.detect_conflicts`)**:
  - Evaluates active (pending) time windows across all pets simultaneously using the mathematical interval intersection invariant:
    $$\text{start}_A < \text{end}_B \quad \text{and} \quad \text{start}_B < \text{end}_A$$
  - Runs in $O(n \log n)$ time by sorting commitments by start timestamp, enabling inner-loop early stopping as soon as `start_B >= end_A`.
  - Disregards completed tasks and handles back-to-back borders (`end_A == start_B`) without false positives.
  - Returns structured records with exact overlap duration in minutes and user-facing warning banners.

- **Next Open Slot Calculation (`Scheduler.find_next_available_slot`)**:
  - Scans an owner's daily calendar on any target date starting from `owner.day_start` (e.g., 08:00 AM) through operating hours (20:00).
  - Merges all existing pet commitments, calculates contiguous gaps, and returns the earliest open window capable of accommodating a continuous session of `duration_minutes`.

---

## 📸 Demo Walkthrough & CLI Output

### Streamlit UI Walkthrough
1. **Owner Dashboard & Summary Cards**: View registered caregiver profile information, day start hour, and daily time budget alongside live metric cards (Total Pets, Total Tasks, Pending Tasks, Completed Tasks).
2. **Multi-Pet Management**: Register new pets with species, breed, and age in the "Add / Manage" tab, then schedule one-time or repeating care tasks mapped to individual pets.
3. **Conflict Detection Banner**: Navigate to the "Daily Schedule & Dashboard" tab where `scheduler.detect_conflicts()` displays high-visibility warning cards for simultaneous overlapping commitments or a green success confirmation if clear.
4. **Interactive Filtering & Sorting Bar**: Filter the daily schedule dynamically by pet, status (Pending vs. Completed), or priority level, while toggling sorting between Chronological Time and Priority Tier.
5. **Interactive Completion & Recurrence Handling**: Toggle tasks between "Done" and "Undo". Marking a recurring task done immediately spawns the next occurrence for tomorrow/next week with a confirmation toast notification.
6. **Smart Slot Recommender Widget**: Expand the `🔍 Find Next Open Care Slot` tool, select a duration slider (e.g. 45 min) and date, and click "Scan Open Slot" to get an immediate metric card with start and end times.

### Professional CLI Formatting & UI Features (Challenge 4)

PawPal+ features professional, executive-grade CLI formatting using the `tabulate` library, visual emoji badges, and styled ANSI color-coded containers.

#### 1. Libraries and Utilities Used
- **`tabulate` (`tablefmt="rounded_outline"`)**: Formats complex multi-attribute schedules into clean Unicode tables with rounded outline borders (`╭─┬─╮`, `│ │`, `╰─┴─╯`), ensuring fixed-width column alignment across variable-length task titles.
- **ANSI Escape Code Palette**:
  - `CYAN` (`\033[96m`) & `GREEN` (`\033[92m`): Section headers and optimal free slot recommendation blocks.
  - `RED` (`\033[91m`): High-visibility double-bordered conflict alert boxes (`╔═════╗`).
  - `YELLOW` (`\033[93m`): Pending status indicators and medium priority tags.
  - `MAGENTA` (`\033[95m`): Brand banners and section icons.
- **Python `datetime` & `timedelta`**: Standardized duration and timestamp calculations.

#### 2. Formatting Functions Implemented in `main.py`
- **`get_category_emoji(task: Task) -> str`**: Maps care task types to intuitive emoji badges:
  - Walk = `🦮`
  - Medication = `💊`
  - Meal / Feeding = `🍖`
  - Vet / Appointment = `🩺`
  - Grooming = `✂️`
- **`get_priority_badge(priority: str) -> str`**: Formats priority tiers with color-coded emoji tags:
  - HIGH = `🚨 HIGH`
  - MEDIUM = `⚡ MEDIUM`
  - LOW = `🌱 LOW`
  - CRITICAL = `🚨 CRITICAL`
- **`get_status_badge(completed: bool) -> str`**: Renders dynamic lifecycle indicators:
  - COMPLETED = `✅ Done`
  - PENDING = `⏳ Pending`
- **`print_table(tasks: list[Task], title: str = "SCHEDULE") -> None`**: Formats schedules via `tabulate` with the exact column layout:
  `[Status] | [Time] | [Pet] | [Task] | [Duration] | [Priority]`
- **`print_conflict_block(conflicts: list[dict]) -> None`**: Renders multi-pet schedule conflicts inside styled ANSI red double-bordered warning boxes (`╔═════════════╗`) detailing conflicting tasks, caregiver pets, and exact overlap minutes.
- **`print_slot_block(slot: datetime, duration_minutes: int, target_date: date) -> None`**: Renders optimal continuous care slot recommendations inside styled ANSI cyan/green double-bordered boxes (`╔═════════════╗`).

### Terminal Demonstration Output (`python main.py`)

Below is the verified terminal output from running `python main.py`, showcasing the scenario with Owner Alex Carter, pets Luna and Mochi, out-of-order tasks, 3-tier priority scheduling, cross-pet conflict detection, recurrence lifecycle, and the slot finder:

```text
══════════════════════════════════════════════════════════════════════════════
🐾                      PAWPAL+ ALGORITHMIC ENGINE DEMO                       🐾
                 Multi-Pet Scheduling, Conflicts & Slot Finder                  
══════════════════════════════════════════════════════════════════════════════

👤 Owner: Alex Carter (alex@example.com)
🐾 Pets Registered: Luna (Golden Retriever) & Mochi (Siamese Cat)
📋 Total Tasks Loaded: 6 across all pets.

▶ STEP A: MULTI-ATTRIBUTE CHRONOLOGICAL SORTING
──────────────────────────────────────────────────────────────────────────────

📋 Unsorted Raw Input Order (Tasks as entered):
╭───────────┬────────┬───────┬───────────────────────┬────────────┬────────────╮
│ Status    │ Time   │ Pet   │ Task                  │ Duration   │ Priority   │
├───────────┼────────┼───────┼───────────────────────┼────────────┼────────────┤
│ ⏳ Pending │ 17:00  │ Luna  │ 🦮 Evening Park Walk   │ 30 min     │ ⚡ MEDIUM   │
│ ⏳ Pending │ 09:00  │ Luna  │ 🦮 Morning Walk        │ 45 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 08:00  │ Luna  │ 🍖 Daily Breakfast     │ 15 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 09:15  │ Mochi │ 🩺 Vet Check & Vaccine │ 30 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 08:15  │ Mochi │ 💊 Insulin Injection   │ 15 min     │ 🚨 CRITICAL │
│ ⏳ Pending │ 14:00  │ Mochi │ ✂️ Coat Brushing      │ 20 min     │ 🌱 LOW      │
╰───────────┴────────┴───────┴───────────────────────┴────────────┴────────────╯

📋 Chronologically Ordered Schedule (via scheduler.sort_by_time()):
╭───────────┬────────┬───────┬───────────────────────┬────────────┬────────────╮
│ Status    │ Time   │ Pet   │ Task                  │ Duration   │ Priority   │
├───────────┼────────┼───────┼───────────────────────┼────────────┼────────────┤
│ ⏳ Pending │ 08:00  │ Luna  │ 🍖 Daily Breakfast     │ 15 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 08:15  │ Mochi │ 💊 Insulin Injection   │ 15 min     │ 🚨 CRITICAL │
│ ⏳ Pending │ 09:00  │ Luna  │ 🦮 Morning Walk        │ 45 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 09:15  │ Mochi │ 🩺 Vet Check & Vaccine │ 30 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 14:00  │ Mochi │ ✂️ Coat Brushing      │ 20 min     │ 🌱 LOW      │
│ ⏳ Pending │ 17:00  │ Luna  │ 🦮 Evening Park Walk   │ 30 min     │ ⚡ MEDIUM   │
╰───────────┴────────┴───────┴───────────────────────┴────────────┴────────────╯
✔ Successfully ordered all tasks from 08:00 AM to 17:00 PM with priority tie-breaking.

▶ STEP B: ADVANCED PRIORITY-BASED SCHEDULING (CHALLENGE 3)
──────────────────────────────────────────────────────────────────────────────
Algorithm: Priority Weights (HIGH: 3 > MEDIUM: 2 > LOW: 1) ➔ Time Tie-Break ➔ Completed at Bottom

📋 Priority-Ranked Schedule (via scheduler.sort_by_priority()):
╭───────────┬────────┬───────┬───────────────────────┬────────────┬────────────╮
│ Status    │ Time   │ Pet   │ Task                  │ Duration   │ Priority   │
├───────────┼────────┼───────┼───────────────────────┼────────────┼────────────┤
│ ⏳ Pending │ 08:15  │ Mochi │ 💊 Insulin Injection   │ 15 min     │ 🚨 CRITICAL │
│ ⏳ Pending │ 08:00  │ Luna  │ 🍖 Daily Breakfast     │ 15 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 09:00  │ Luna  │ 🦮 Morning Walk        │ 45 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 09:15  │ Mochi │ 🩺 Vet Check & Vaccine │ 30 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 17:00  │ Luna  │ 🦮 Evening Park Walk   │ 30 min     │ ⚡ MEDIUM   │
│ ⏳ Pending │ 14:00  │ Mochi │ ✂️ Coat Brushing      │ 20 min     │ 🌱 LOW      │
│ ✅ Done    │ 07:00  │ Luna  │ 🦮 Early Morning Walk  │ 20 min     │ 🚨 HIGH     │
╰───────────┴────────┴───────┴───────────────────────┴────────────┴────────────╯
✔ Verified: HIGH tasks lead the schedule, tie-broken by time; completed tasks pushed to bottom!

▶ STEP C: CROSS-PET CONFLICT DETECTION
──────────────────────────────────────────────────────────────────────────────
🔍 Scanning all active commitments for overlapping time windows...

╔════════════════════════════════════════════════════════════════════════════╗
║  ⚠️  SCHEDULING CONFLICT DETECTED (1 OVERLAPPING WINDOW)                          ║
╠════════════════════════════════════════════════════════════════════════════╣
║  [1] 🦮 'Morning Walk' (Luna, 09:00) ⚔️  🩺 'Vet Check & Vaccine' (Mochi, 09:15) ║
║      ↳ Overlap Window: 30 minutes simultaneous care demand                        ║
╚════════════════════════════════════════════════════════════════════════════╝

▶ STEP D: MULTI-CRITERIA FILTERING
──────────────────────────────────────────────────────────────────────────────
🔍 Filter 1: Tasks with Priority == 'HIGH'

📋 Filtered Tasks: High Priority:
╭───────────┬────────┬───────┬───────────────────────┬────────────┬────────────╮
│ Status    │ Time   │ Pet   │ Task                  │ Duration   │ Priority   │
├───────────┼────────┼───────┼───────────────────────┼────────────┼────────────┤
│ ⏳ Pending │ 09:00  │ Luna  │ 🦮 Morning Walk        │ 45 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 08:00  │ Luna  │ 🍖 Daily Breakfast     │ 15 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 09:15  │ Mochi │ 🩺 Vet Check & Vaccine │ 30 min     │ 🚨 HIGH     │
╰───────────┴────────┴───────┴───────────────────────┴────────────┴────────────╯

🔍 Filter 2: Tasks assigned specifically to 'Mochi'

📋 Filtered Tasks: Mochi Only:
╭───────────┬────────┬───────┬───────────────────────┬────────────┬────────────╮
│ Status    │ Time   │ Pet   │ Task                  │ Duration   │ Priority   │
├───────────┼────────┼───────┼───────────────────────┼────────────┼────────────┤
│ ⏳ Pending │ 09:15  │ Mochi │ 🩺 Vet Check & Vaccine │ 30 min     │ 🚨 HIGH     │
│ ⏳ Pending │ 08:15  │ Mochi │ 💊 Insulin Injection   │ 15 min     │ 🚨 CRITICAL │
│ ⏳ Pending │ 14:00  │ Mochi │ ✂️ Coat Brushing      │ 20 min     │ 🌱 LOW      │
╰───────────┴────────┴───────┴───────────────────────┴────────────┴────────────╯

▶ STEP E: AUTOMATED RECURRING TASK LIFECYCLE
──────────────────────────────────────────────────────────────────────────────
Completing recurring task: 'Daily Breakfast' for Luna (Recurrence: DAILY)...

Result of complete_task():
  1. Original Task ID: `ea3ed6e0` | Title: 'Daily Breakfast'
     Status: is_completed = True [PRESERVED IN HISTORY]
  2. Next Occurrence ID: `008d0568` | Title: 'Daily Breakfast'
     Status: is_completed = False [SPAWNED FOR NEXT CYCLE]
     New Scheduled Time: 2026-10-12 08:00
✔ Verified: Original task is preserved as DONE; new task spawned automatically for tomorrow!

▶ STEP F: STRETCH FEATURE — NEXT AVAILABLE SLOT FINDER
──────────────────────────────────────────────────────────────────────────────
🔍 Searching for earliest continuous free window of 45 minutes on 2026-10-11...

╔════════════════════════════════════════════════════════════════════════════╗
║  ✨ OPTIMAL FREE CARE WINDOW RECOMMENDED                                    ║
╠════════════════════════════════════════════════════════════════════════════╣
║  📅 Target Date:      Sunday, Oct 11, 2026                                 ║
║  🕒 Suggested Window:  09:45 AM ➔ 10:30 AM (45 min continuous)                   ║
║  💡 Confidence:        100% Conflict-Free across all pets                       ║
╚════════════════════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════════════════════
🐾                               DEMO COMPLETE                                🐾
       All Algorithmic & UI Formatting Capabilities Successfully Verified       
══════════════════════════════════════════════════════════════════════════════
```


---

## 💾 Data Persistence Layer

PawPal+ includes a zero-dependency JSON persistence layer enabling pets, tasks, and caregiver preferences to persist across application restarts.

### Marshmallow vs. Custom Dictionary Conversion
When architecting persistence for nested domain objects with date/time properties, two design patterns were evaluated:
- **Library Approach (`marshmallow` / `pydantic`)**: While schema libraries offer validation, they introduce external third-party dependencies, schema definition boilerplate (`TaskSchema`, `PetSchema`, `OwnerSchema`), and version synchronization friction.
- **Custom Dictionary Conversion (Adopted)**: Implementing cohesive `to_dict()` and `from_dict()` methods directly on `Task`, `Pet`, and `Owner` uses Python's standard library (`json` and `datetime`). This guarantees zero external runtime dependencies, explicit control over ISO-8601 string formatting (`isoformat()` and `datetime.fromisoformat()`), and fine-grained defensive handling of mixed `datetime.time` / `datetime.datetime` attributes.

### Persistence Workflow Architecture
1. **Startup Auto-Load**:
   - On application startup (`app.py`), the system checks for `data.json`.
   - If `data.json` exists, `load_from_json("data.json")` reads and deserializes the entire object graph (`Owner` -> `Pet` -> `Task`) into `st.session_state.owner`.
   - If `data.json` is missing or corrupted, the system initializes default scenario data and creates `data.json` immediately via `save_to_json(owner, "data.json")`.
2. **Auto-Save on State Mutation**:
   - **Adding a Pet**: Appends the new `Pet` to `owner.pets` and calls `save_to_json(st.session_state.owner, "data.json")`.
   - **Scheduling a Task**: Appends the new `Task` to `pet.tasks` and calls `save_to_json(st.session_state.owner, "data.json")`.
   - **Toggling Task Status (Done / Undo)**: Completing a task (or spawning its next recurring occurrence) immediately updates `data.json`.
   - **Deleting a Task**: Removing a task from a pet's schedule updates `data.json`.
   - **Modifying Owner Settings**: Adjusting time budget or day start hour in the sidebar updates `data.json`.
   - **Resetting Data**: Clicking "Reset to Default Scenario Data" removes `data.json` and cleanly restores initial defaults.

### Files Modified for Persistence
- [`pawpal_system.py`](pawpal_system.py):
  - `Task.to_dict()` & `Task.from_dict()`: Serializes and deserializes task attributes, handling ISO format strings for `scheduled_time`, `scheduled_datetime`, `preferred_time`, and `start_time`.
  - `Pet.to_dict()` & `Pet.from_dict()`: Serializes pet metadata and recursively converts child `tasks`.
  - `Owner.to_dict()` & `Owner.from_dict()`: Serializes caregiver preferences, time budget, day start hour, and child `pets`.
  - `save_to_json(owner, filepath="data.json")`: Serializes the entire domain hierarchy to disk with 2-space indentation.
  - `load_from_json(filepath="data.json")`: Reconstructs the `Owner` hierarchy, gracefully falling back to a default instance if the file is missing.
- [`app.py`](app.py):
  - Integrated `load_from_json` into session state initialization on app startup.
  - Added real-time `save_to_json` triggers on pet registration, task creation, status toggle (Done/Undo), task deletion, and settings updates.
  - Added `data.json` file cleanup on user-triggered reset.
- [`tests/test_pawpal.py`](tests/test_pawpal.py):
  - Implemented `test_persistence_json_serialization` verifying round-trip JSON serialization fidelity, missing-file fallback handling, and ISO string parsing for `datetime` and `time` objects.

---

## 🧪 Testing PawPal+

### Test Execution

Execute the full automated test suite using pytest with verbose output:

```bash
python -m pytest -v
```

### Coverage Summary

The test suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) provides comprehensive unit, integration, and edge-case coverage:
- **Status Transitions**: Verifies `mark_complete()` and `mark_pending()` toggle both `is_completed` and `completed` flags consistently.
- **Multi-Pet Aggregation**: Verifies that owner aggregation collects all tasks across pets without dropping or cross-contaminating tasks.
- **Overlap Edge Cases**: Verifies that touching back-to-back commitments (`end_A == start_B`) trigger **0 conflicts**, and that completed commitments are ignored during conflict checks.
- **24-Hour & 7-Day Recurrence Math**: Validates date incrementation across midnight and month transitions (e.g. Oct 31 to Nov 1).
- **Graceful Empty States**: Verifies owners with 0 pets or empty task lists execute all methods (`collect_all_tasks`, `detect_conflicts`, `sort_by_time`, `filter_tasks`) safely.
- **JSON Persistence Round-Trip**: Validates complete round-trip serialization and deserialization (`to_dict`, `from_dict`, `save_to_json`, `load_from_json`).
- **Priority Tier Sorting**: Validates 3-tier weighting (`HIGH: 3 > MEDIUM: 2 > LOW: 1`), chronological tie-breaking, and completed task relegation.
- **CLI Formatting Helpers**: Verifies category emoji mappings (`🦮`, `💊`, `🍖`, `🩺`), priority indicators, status badges, and table/block rendering.

### Terminal Output

```text
$ python -m pytest -v
============================== test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0 -- venv/bin/python
rootdir: /Users/gabrielanokye/AI Engineer/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 15 items

tests/test_pawpal.py::test_task_lifecycle_and_completion PASSED          [  6%]
tests/test_pawpal.py::test_sorting_chronological_and_priority PASSED     [ 13%]
tests/test_pawpal.py::test_filter_tasks_by_multiple_criteria PASSED      [ 20%]
tests/test_pawpal.py::test_daily_recurrence_generation PASSED            [ 26%]
tests/test_pawpal.py::test_conflict_detection_overlapping_intervals PASSED [ 33%]
tests/test_pawpal.py::test_conflict_detection_edge_cases PASSED          [ 40%]
tests/test_pawpal.py::test_empty_owner_and_edge_conditions PASSED        [ 46%]
tests/test_pawpal.py::test_pet_task_management_edge_cases PASSED         [ 53%]
tests/test_pawpal.py::test_recurrence_across_month_boundary PASSED       [ 60%]
tests/test_pawpal.py::test_scheduler_build_plan_budget_filtering PASSED  [ 66%]
tests/test_pawpal.py::test_scheduler_find_next_available_slot PASSED     [ 73%]
tests/test_pawpal.py::test_find_next_available_slot_challenge_1 PASSED   [ 80%]
tests/test_pawpal.py::test_persistence_json_serialization PASSED         [ 86%]
tests/test_pawpal.py::test_priority_scheduling_challenge_3 PASSED        [ 93%]
tests/test_pawpal.py::test_cli_formatting_helpers_challenge_4 PASSED     [100%]

============================== 15 passed in 0.05s ==============================
```

### System Reliability Confidence Level

**Confidence Rating: ⭐⭐⭐⭐⭐ 5/5**

**Why we have high confidence for real-world usage**:
1. **Mathematical Interval Invariants**: Conflict detection is decoupled from simplistic timestamp equality. Strict interval overlap mathematics ($\text{start}_A < \text{end}_B \land \text{start}_B < \text{end}_A$) ensure simultaneous demands are detected across different pets while avoiding false alerts on contiguous tasks.
2. **Defensive Recurrence Lifecycle**: Real-world pet care relies heavily on recurring routines (daily medications, feedings). Verified date arithmetic preserves schedule accuracy across month boundaries while maintaining completed tasks in history for auditable tracking.
3. **Zero-Crash Empty States**: Tested to ensure that zero-pet owners, empty schedules, and nonexistent task IDs degrade gracefully without unhandled exceptions.

---

## 🚀 Setup & Installation

### 1. Clone the Repository & Create Virtual Environment

```bash
git clone https://github.com/GabrielAnokye/ai110-module2show-pawpal-starter.git
cd ai110-module2show-pawpal-starter

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the Streamlit Web Dashboard

```bash
streamlit run app.py
```

### 4. Run the Terminal Engine Demonstration

```bash
python main.py
```

### 5. Run the Automated Test Suite

```bash
python -m pytest -v
```
