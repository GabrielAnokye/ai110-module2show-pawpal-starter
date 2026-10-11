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

Sample CLI output from running `python main.py` demonstrating multi-pet scheduling across an owner's daily time budget:

```text
======================================================================
🐾                    PAWPAL+ DAILY CARE SCHEDULER                    🐾
======================================================================

👤 Owner Registered: Jordan Lee
⏰ Daily Time Budget: 90 minutes (Starting at 08:00)

🐶 Registered Pets: Biscuit (Golden Retriever) and 🐱 Mochi (Scottish Fold)

📋 Total Tasks Added: 5 pending across all pets.

🧠 Building schedule using strategy: 'priority_first'...

📅 TODAY'S ITINERARY:
Start Time   | Pet        | Priority   | Duration   | Task Description
----------------------------------------------------------------------
08:00        | Mochi      | CRITICAL   | 15 min     | Insulin Injection
08:15        | Biscuit    | HIGH       | 30 min     | Morning Walk
08:45        | Biscuit    | HIGH       | 15 min     | Breakfast Feeding
09:00        | Mochi      | MEDIUM     | 20 min     | Brushing & Coat Care
----------------------------------------------------------------------

⚠️  SKIPPED TASKS (Exceeded Owner's 90-minute Budget):
  • [LOW] Agility Park Play for Biscuit (40 min)

📊 Summary: 4 tasks scheduled (80/90 min), 1 skipped.
⏳ Remaining Time Buffer: 10 min

======================================================================
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
collected 5 items

tests/test_pawpal.py::test_task_completion_status PASSED                 [ 20%]
tests/test_pawpal.py::test_pet_task_management PASSED                    [ 40%]
tests/test_pawpal.py::test_owner_task_aggregation PASSED                 [ 60%]
tests/test_pawpal.py::test_scheduler_daily_schedule_ordering PASSED      [ 80%]
tests/test_pawpal.py::test_scheduler_build_plan_budget_filtering PASSED  [100%]

============================== 5 passed in 0.02s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
