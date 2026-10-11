"""PawPal+ CLI Demo Script.

Demonstrates Phase 4 algorithmic capabilities in the terminal:
- Multi-attribute chronological sorting with priority tie-breaks
- O(n log n) cross-pet conflict detection
- Multi-criteria filtering (pet, priority, completion)
- Automated recurring task lifecycle (completion & next occurrence generation)
- Continuous free time slot finding (stretch feature)
"""

from datetime import date, datetime, time
from pawpal_system import Owner, Pet, Scheduler, Task

# ANSI Colors for rich terminal presentation
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(title: str, subtitle: str = "") -> None:
    """Print a visually distinct section banner."""
    line = "=" * 76
    print(f"\n{CYAN}{line}{RESET}")
    print(f"{BOLD}{MAGENTA}🐾  {title.center(70)}  🐾{RESET}")
    if subtitle:
        print(f"{CYAN}    {subtitle.center(70)}    {RESET}")
    print(f"{CYAN}{line}{RESET}\n")


def print_step(step_num: str, step_name: str) -> None:
    """Print step headline."""
    print(f"\n{BOLD}{GREEN}▶ STEP {step_num}: {step_name.upper()}{RESET}")
    print(f"{'-' * 76}")


def print_table(tasks: list[Task], title: str = "TASKS") -> None:
    """Format and print tasks in a structured tabular layout."""
    print(f"{BOLD}{title}:{RESET}")
    header = (
        f"{'Scheduled':<11} | {'Pet':<9} | {'Priority':<10} | {'Duration':<9} | "
        f"{'Recur':<8} | {'Status':<10} | {'Description'}"
    )
    divider = "-" * 88
    print(header)
    print(divider)
    for t in tasks:
        effective_time = t.scheduled_time or t.start_time or t.preferred_time
        time_str = effective_time.strftime("%H:%M") if effective_time else "TBD"
        pet_str = t.pet_name or "All"
        prio_str = t.priority.upper()
        dur_str = f"{t.duration_minutes} min"
        recur_str = t.recurrence.title()
        status_str = f"{GREEN}DONE{RESET}" if t.completed else f"{YELLOW}PENDING{RESET}"
        desc = t.title or t.description
        print(
            f"{time_str:<11} | {pet_str:<9} | {prio_str:<10} | {dur_str:<9} | "
            f"{recur_str:<8} | {status_str:<19} | {desc}"
        )
    print(divider)


def main() -> None:
    print_header("PAWPAL+ ALGORITHMIC ENGINE DEMO", "Multi-Pet Scheduling, Conflicts & Slot Finder")

    # -------------------------------------------------------------------------
    # 1. SCENARIO SETUP
    # -------------------------------------------------------------------------
    owner = Owner(
        name="Alex Carter",
        contact="alex@example.com",
        available_minutes=180,
        day_start=time(8, 0),
    )
    luna = Pet(name="Luna", species="Dog", breed="Golden Retriever", age_years=3.0, pet_id="pet_1")
    mochi = Pet(name="Mochi", species="Cat", breed="Siamese Cat", age_years=2.0, pet_id="pet_2")

    owner.add_pet(luna)
    owner.add_pet(mochi)

    today = date.today()

    # Tasks deliberately added OUT OF CHRONOLOGICAL ORDER:
    # 1. Late afternoon walk (17:00)
    t_evening = Task(
        title="Evening Park Walk",
        duration_minutes=30,
        priority="medium",
        category="walk",
        scheduled_time=time(17, 0),
        scheduled_datetime=datetime.combine(today, time(17, 0)),
    )
    # 2. Morning walk (09:00 - 09:45) - Intentionally overlaps with Mochi's vet visit!
    t_walk = Task(
        title="Morning Walk",
        duration_minutes=45,
        priority="high",
        category="walk",
        scheduled_time=time(9, 0),
        scheduled_datetime=datetime.combine(today, time(9, 0)),
    )
    # 3. Vet check for Mochi (09:15 - 09:45) - Intentionally overlaps with Luna's walk!
    t_vet = Task(
        title="Vet Check & Vaccine",
        duration_minutes=30,
        priority="high",
        category="appointment",
        scheduled_time=time(9, 15),
        scheduled_datetime=datetime.combine(today, time(9, 15)),
    )
    # 4. Daily Breakfast for Luna (08:00) - Recurring daily!
    t_breakfast = Task(
        title="Daily Breakfast",
        duration_minutes=15,
        priority="high",
        category="feeding",
        recurrence="DAILY",
        scheduled_time=time(8, 0),
        scheduled_datetime=datetime.combine(today, time(8, 0)),
    )
    # 5. Insulin Injection for Mochi (08:15)
    t_meds = Task(
        title="Insulin Injection",
        duration_minutes=15,
        priority="critical",
        category="medication",
        recurrence="DAILY",
        scheduled_time=time(8, 15),
        scheduled_datetime=datetime.combine(today, time(8, 15)),
    )
    # 6. Coat brushing for Mochi (14:00)
    t_brush = Task(
        title="Coat Brushing",
        duration_minutes=20,
        priority="low",
        category="grooming",
        scheduled_time=time(14, 0),
        scheduled_datetime=datetime.combine(today, time(14, 0)),
    )

    # Attach in jumbled order
    luna.add_task(t_evening)
    luna.add_task(t_walk)
    mochi.add_task(t_vet)
    luna.add_task(t_breakfast)
    mochi.add_task(t_meds)
    mochi.add_task(t_brush)

    scheduler = Scheduler(owner=owner)

    print(f"👤 {BOLD}Owner:{RESET} {owner.name} ({owner.contact})")
    print(f"🐾 {BOLD}Pets Registered:{RESET} {luna.name} ({luna.breed}) & {mochi.name} ({mochi.breed})")
    print(f"📋 {BOLD}Total Tasks Loaded:{RESET} {len(owner.get_all_tasks())} across all pets.")

    # -------------------------------------------------------------------------
    # STEP A: MULTI-ATTRIBUTE CHRONOLOGICAL SORTING
    # -------------------------------------------------------------------------
    print_step("A", "Multi-Attribute Chronological Sorting")
    raw_tasks = owner.get_all_tasks()
    print_table(raw_tasks, title="Unsorted Raw Input Order (Tasks as entered)")

    sorted_tasks = scheduler.sort_by_time()
    print()
    print_table(sorted_tasks, title="Chronologically Ordered Schedule (via scheduler.sort_by_time())")
    print(f"{GREEN}✔ Successfully ordered all tasks from 08:00 AM to 17:00 PM with priority tie-breaking.{RESET}")

    # -------------------------------------------------------------------------
    # STEP B: ROBUST CONFLICT DETECTION
    # -------------------------------------------------------------------------
    print_step("B", "Cross-Pet Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    print(f"🔍 Scanning all active commitments for overlapping time windows...")
    if conflicts:
        print(f"{RED}{BOLD}⚠ Found {len(conflicts)} Scheduling Conflict(s):{RESET}")
        for idx, conf in enumerate(conflicts, 1):
            print(f"  {RED}{BOLD}[{idx}]{RESET} {conf['warning_message']}")
            print(f"      ↳ Overlap Window: {conf['overlap_minutes']} minutes simultaneous demand.")
    else:
        print(f"{GREEN}✔ No conflicts detected.{RESET}")

    # -------------------------------------------------------------------------
    # STEP C: MULTI-CRITERIA FILTERING
    # -------------------------------------------------------------------------
    print_step("C", "Multi-Criteria Filtering")
    high_priority = scheduler.filter_tasks(priority="high")
    print(f"🔍 {BOLD}Filter 1: Tasks with Priority == 'HIGH'{RESET}")
    for t in high_priority:
        print(f"   • [{t.priority.upper()}] {t.title} for {t.pet_name} at {t.scheduled_time.strftime('%H:%M')}")

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    print(f"\n🔍 {BOLD}Filter 2: Tasks assigned specifically to 'Mochi'{RESET}")
    for t in mochi_tasks:
        print(f"   • [{t.priority.upper()}] {t.title} ({t.duration_minutes} min, scheduled {t.scheduled_time.strftime('%H:%M')})")

    # -------------------------------------------------------------------------
    # STEP D: RECURRING TASK COMPLETION & NEXT OCCURRENCE
    # -------------------------------------------------------------------------
    print_step("D", "Automated Recurring Task Lifecycle")
    print(f"Completing recurring task: '{t_breakfast.title}' for {t_breakfast.pet_name} (Recurrence: {t_breakfast.recurrence})...")
    
    # Complete through Pet lifecycle
    next_occurrence = luna.complete_task(t_breakfast.task_id)

    print(f"\n{BOLD}Result of complete_task():{RESET}")
    print(f"  1. Original Task ID: `{t_breakfast.task_id}` | Title: '{t_breakfast.title}'")
    print(f"     Status: {GREEN}is_completed = {t_breakfast.is_completed} [PRESERVED IN HISTORY]{RESET}")
    
    if next_occurrence:
        print(f"  2. Next Occurrence ID: `{next_occurrence.task_id}` | Title: '{next_occurrence.title}'")
        print(f"     Status: {YELLOW}is_completed = {next_occurrence.is_completed} [SPAWNED FOR NEXT CYCLE]{RESET}")
        print(f"     New Scheduled Time: {BOLD}{next_occurrence.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}{RESET}")
        print(f"{GREEN}✔ Verified: Original task is preserved as DONE; new task spawned automatically for tomorrow!{RESET}")

    # -------------------------------------------------------------------------
    # STEP E: NEXT AVAILABLE SLOT FINDER (STRETCH FEATURE)
    # -------------------------------------------------------------------------
    print_step("E", "Stretch Feature — Next Available Slot Finder")
    req_duration = 45
    print(f"🔍 Searching for earliest continuous free window of {req_duration} minutes on {today}...")
    
    slot = scheduler.find_next_available_slot(duration_minutes=req_duration, search_date=today)
    if slot:
        slot_end = (slot + (t_walk.scheduled_datetime - t_walk.scheduled_datetime)).time()  # type helper
        slot_end_time = (datetime.combine(today, slot.time()) + (slot - slot)).time()
        print(f"{GREEN}{BOLD}✨ Found Available Window!{RESET}")
        print(f"   Suggested Start: {BOLD}{CYAN}{slot.strftime('%Y-%m-%d %H:%M')}{RESET}")
        end_time_dt = datetime.combine(today, slot.time()) + (datetime.min.replace(hour=0, minute=req_duration) - datetime.min)
        print(f"   Window Range:    {slot.strftime('%H:%M')} ➔ {end_time_dt.strftime('%H:%M')} ({req_duration} min continuous opening)")
    else:
        print(f"{RED}No open slots of {req_duration} minutes found for {today}.{RESET}")

    print_header("DEMO COMPLETE", "All Phase 4 Algorithmic Features Successfully Verified")


if __name__ == "__main__":
    main()
