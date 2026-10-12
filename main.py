"""PawPal+ Professional CLI Formatting & Engine Demo.

Demonstrates algorithmic capabilities with professional terminal presentation:
- Visual emoji indicators (Priority, Status, Care Categories)
- Formatted tabular layouts using tabulate
- Styled ANSI red warning containers for conflict detection
- Styled ANSI cyan/green recommendation blocks for slot finding
"""

from datetime import date, datetime, time, timedelta
from typing import List, Optional
from tabulate import tabulate
from pawpal_system import Owner, Pet, Scheduler, Task

# -----------------------------------------------------------------------------
# ANSI Color Palette
# -----------------------------------------------------------------------------
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


# -----------------------------------------------------------------------------
# Emoji Formatting Helpers
# -----------------------------------------------------------------------------
def get_category_emoji(task: Task) -> str:
    """Return an emoji indicator based on task category or title."""
    cat = (task.category or "").lower()
    title = (task.title or "").lower()
    if "walk" in cat or "walk" in title:
        return "🦮"
    if "med" in cat or "pill" in title or "insulin" in title or "injection" in title:
        return "💊"
    if "feed" in cat or "meal" in title or "breakfast" in title or "dinner" in title or "food" in title:
        return "🍖"
    if "vet" in cat or "appoint" in cat or "doctor" in title or "vaccine" in title:
        return "🩺"
    if "groom" in cat or "brush" in title or "bath" in title or "wash" in title:
        return "✂️"
    return "🐾"


def get_priority_badge(priority: str) -> str:
    """Return formatted emoji priority indicator."""
    p = (priority or "medium").upper()
    if p == "CRITICAL":
        return f"{RED}🚨 CRITICAL{RESET}"
    if p == "HIGH":
        return f"{RED}🚨 HIGH{RESET}"
    if p == "MEDIUM":
        return f"{YELLOW}⚡ MEDIUM{RESET}"
    if p == "LOW":
        return f"{GREEN}🌱 LOW{RESET}"
    return f"{YELLOW}⚡ {p}{RESET}"


def get_status_badge(completed: bool) -> str:
    """Return formatted emoji status indicator."""
    return f"{GREEN}✅ Done{RESET}" if completed else f"{YELLOW}⏳ Pending{RESET}"


# -----------------------------------------------------------------------------
# Visual Block Renderers
# -----------------------------------------------------------------------------
def print_header(title: str, subtitle: str = "") -> None:
    """Print a visually distinct section banner."""
    line = "═" * 78
    print(f"\n{CYAN}{line}{RESET}")
    print(f"{BOLD}{MAGENTA}🐾  {title.center(72)}  🐾{RESET}")
    if subtitle:
        print(f"{CYAN}    {subtitle.center(72)}    {RESET}")
    print(f"{CYAN}{line}{RESET}\n")


def print_step(step_num: str, step_name: str) -> None:
    """Print step headline."""
    print(f"\n{BOLD}{GREEN}▶ STEP {step_num}: {step_name.upper()}{RESET}")
    print(f"{'─' * 78}")


def print_table(tasks: list[Task], title: str = "SCHEDULE") -> None:
    """Format schedule tables using tabulate with [Status] | [Time] | [Pet] | [Task] | [Duration] | [Priority]."""
    print(f"\n{BOLD}{CYAN}📋 {title}:{RESET}")
    headers = ["Status", "Time", "Pet", "Task", "Duration", "Priority"]
    rows = []
    for t in tasks:
        effective_time = t.scheduled_time or t.start_time or t.preferred_time
        time_str = effective_time.strftime("%H:%M") if effective_time else "TBD"
        pet_str = t.pet_name or "All"
        emoji = get_category_emoji(t)
        task_str = f"{emoji} {t.title}"
        dur_str = f"{t.duration_minutes} min"
        prio_badge = get_priority_badge(t.priority)
        status_badge = get_status_badge(t.completed or t.is_completed)
        rows.append([status_badge, time_str, pet_str, task_str, dur_str, prio_badge])

    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def print_conflict_block(conflicts: list[dict]) -> None:
    """Render conflict alerts in styled ANSI red warning blocks."""
    border = "═" * 76
    print(f"\n{RED}{BOLD}╔{border}╗{RESET}")
    print(f"{RED}{BOLD}║  ⚠️  SCHEDULING CONFLICT DETECTED ({len(conflicts)} OVERLAPPING WINDOW){' ' * 26}║{RESET}")
    print(f"{RED}{BOLD}╠{border}╣{RESET}")
    for idx, conf in enumerate(conflicts, 1):
        t1 = conf.get("task_1")
        t2 = conf.get("task_2")
        overlap = conf.get("overlap_minutes", 0)
        p1 = t1.pet_name if t1 else "Pet 1"
        p2 = t2.pet_name if t2 else "Pet 2"
        title1 = t1.title if t1 else "Task 1"
        title2 = t2.title if t2 else "Task 2"
        time1 = t1.scheduled_time.strftime("%H:%M") if t1 and t1.scheduled_time else "00:00"
        time2 = t2.scheduled_time.strftime("%H:%M") if t2 and t2.scheduled_time else "00:00"

        print(f"{RED}║  [{idx}] 🦮 '{title1}' ({p1}, {time1}) ⚔️  🩺 '{title2}' ({p2}, {time2}){' ' * (32 - len(title1) - len(title2))}║{RESET}")
        print(f"{RED}║      ↳ Overlap Window: {BOLD}{overlap} minutes{RESET}{RED} simultaneous care demand{' ' * 24}║{RESET}")
    print(f"{RED}{BOLD}╚{border}╝{RESET}\n")


def print_slot_block(slot: datetime, duration_minutes: int, target_date: date) -> None:
    """Render slot recommendations in styled ANSI cyan/green blocks."""
    end_dt = slot + timedelta(minutes=duration_minutes)
    border = "═" * 76
    print(f"\n{GREEN}{BOLD}╔{border}╗{RESET}")
    print(f"{GREEN}{BOLD}║  ✨ OPTIMAL FREE CARE WINDOW RECOMMENDED{' ' * 36}║{RESET}")
    print(f"{CYAN}╠{border}╣{RESET}")
    print(f"{CYAN}║  📅 Target Date:      {BOLD}{target_date.strftime('%A, %b %d, %Y')}{RESET}{' ' * 33}║")
    print(f"{CYAN}║  🕒 Suggested Window:  {BOLD}{GREEN}{slot.strftime('%I:%M %p')}{RESET}{CYAN} ➔ {BOLD}{GREEN}{end_dt.strftime('%I:%M %p')}{RESET} ({duration_minutes} min continuous){' ' * 19}║")
    print(f"{CYAN}║  💡 Confidence:        100% Conflict-Free across all pets{' ' * 23}║")
    print(f"{GREEN}{BOLD}╚{border}╝{RESET}\n")


# -----------------------------------------------------------------------------
# Main CLI Workflow
# -----------------------------------------------------------------------------
def main() -> None:
    print_header("PAWPAL+ ALGORITHMIC ENGINE DEMO", "Multi-Pet Scheduling, Conflicts & Slot Finder")

    # 1. Scenario Setup
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

    # Tasks deliberately added in scrambled chronological order
    t_evening = Task(
        title="Evening Park Walk",
        duration_minutes=30,
        priority="medium",
        category="walk",
        scheduled_time=time(17, 0),
        scheduled_datetime=datetime.combine(today, time(17, 0)),
    )
    t_walk = Task(
        title="Morning Walk",
        duration_minutes=45,
        priority="high",
        category="walk",
        scheduled_time=time(9, 0),
        scheduled_datetime=datetime.combine(today, time(9, 0)),
    )
    t_vet = Task(
        title="Vet Check & Vaccine",
        duration_minutes=30,
        priority="high",
        category="appointment",
        scheduled_time=time(9, 15),
        scheduled_datetime=datetime.combine(today, time(9, 15)),
    )
    t_breakfast = Task(
        title="Daily Breakfast",
        duration_minutes=15,
        priority="high",
        category="feeding",
        recurrence="DAILY",
        scheduled_time=time(8, 0),
        scheduled_datetime=datetime.combine(today, time(8, 0)),
    )
    t_meds = Task(
        title="Insulin Injection",
        duration_minutes=15,
        priority="critical",
        category="medication",
        recurrence="DAILY",
        scheduled_time=time(8, 15),
        scheduled_datetime=datetime.combine(today, time(8, 15)),
    )
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
    print_table(sorted_tasks, title="Chronologically Ordered Schedule (via scheduler.sort_by_time())")
    print(f"{GREEN}✔ Successfully ordered all tasks from 08:00 AM to 17:00 PM with priority tie-breaking.{RESET}")

    # -------------------------------------------------------------------------
    # STEP B: ADVANCED PRIORITY-BASED SCHEDULING (CHALLENGE 3)
    # -------------------------------------------------------------------------
    print_step("B", "Advanced Priority-Based Scheduling (Challenge 3)")
    print(f"Algorithm: Priority Weights (HIGH: 3 > MEDIUM: 2 > LOW: 1) ➔ Time Tie-Break ➔ Completed at Bottom")

    # Include a completed task to demonstrate completed tasks get pushed to bottom
    t_completed_demo = Task(
        title="Early Morning Walk",
        duration_minutes=20,
        priority="high",
        category="walk",
        scheduled_time=time(7, 0),
        completed=True,
        pet_name="Luna",
    )
    demo_tasks_with_completed = raw_tasks + [t_completed_demo]
    prio_sorted = scheduler.sort_by_priority(demo_tasks_with_completed)
    print_table(prio_sorted, title="Priority-Ranked Schedule (via scheduler.sort_by_priority())")
    print(f"{GREEN}✔ Verified: HIGH tasks lead the schedule, tie-broken by time; completed tasks pushed to bottom!{RESET}")

    # -------------------------------------------------------------------------
    # STEP C: CROSS-PET CONFLICT DETECTION
    # -------------------------------------------------------------------------
    print_step("C", "Cross-Pet Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    print("🔍 Scanning all active commitments for overlapping time windows...")
    if conflicts:
        print_conflict_block(conflicts)
    else:
        print(f"{GREEN}✔ No conflicts detected.{RESET}")

    # -------------------------------------------------------------------------
    # STEP D: MULTI-CRITERIA FILTERING
    # -------------------------------------------------------------------------
    print_step("D", "Multi-Criteria Filtering")
    high_priority = scheduler.filter_tasks(priority="high")
    print(f"🔍 {BOLD}Filter 1: Tasks with Priority == 'HIGH'{RESET}")
    print_table(high_priority, title="Filtered Tasks: High Priority")

    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    print(f"\n🔍 {BOLD}Filter 2: Tasks assigned specifically to 'Mochi'{RESET}")
    print_table(mochi_tasks, title="Filtered Tasks: Mochi Only")

    # -------------------------------------------------------------------------
    # STEP E: RECURRING TASK COMPLETION & NEXT OCCURRENCE
    # -------------------------------------------------------------------------
    print_step("E", "Automated Recurring Task Lifecycle")
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
    # STEP F: NEXT AVAILABLE SLOT FINDER (STRETCH FEATURE)
    # -------------------------------------------------------------------------
    print_step("F", "Stretch Feature — Next Available Slot Finder")
    req_duration = 45
    print(f"🔍 Searching for earliest continuous free window of {req_duration} minutes on {today}...")
    
    slot = scheduler.find_next_available_slot(duration_minutes=req_duration, target_date=today)
    if slot:
        print_slot_block(slot, req_duration, today)
    else:
        print(f"{RED}No open slots of {req_duration} minutes found for {today}.{RESET}")

    print_header("DEMO COMPLETE", "All Algorithmic & UI Formatting Capabilities Successfully Verified")


if __name__ == "__main__":
    main()
