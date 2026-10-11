"""PawPal+ CLI Demo Script.

Demonstrates end-to-end multi-pet scheduling functionality using
the core object-oriented classes from pawpal_system.py.
"""

from datetime import time
from pawpal_system import Owner, Pet, Scheduler, Task


def print_banner(title: str) -> None:
    """Print a visually distinct section banner."""
    line = "=" * 70
    print(f"\n{line}")
    print(f"🐾  {title.center(64)}  🐾")
    print(f"{line}\n")


def print_schedule_table(scheduled_tasks: list[Task]) -> None:
    """Format and print scheduled tasks in a clean tabular layout."""
    header = f"{'Start Time':<12} | {'Pet':<10} | {'Priority':<10} | {'Duration':<10} | {'Task Description'}"
    divider = "-" * 70
    print(header)
    print(divider)
    for task in scheduled_tasks:
        time_str = task.start_time.strftime("%H:%M") if task.start_time else "TBD"
        pet_str = task.pet_name or "All"
        prio_str = task.priority.upper()
        dur_str = f"{task.duration_minutes} min"
        print(f"{time_str:<12} | {pet_str:<10} | {prio_str:<10} | {dur_str:<10} | {task.title}")
    print(divider)


def main() -> None:
    print_banner("PAWPAL+ DAILY CARE SCHEDULER")

    # 1. Create an Owner with a 90-minute daily time budget starting at 08:00 AM
    owner = Owner(
        name="Jordan Lee",
        email="jordan@example.com",
        available_minutes=90,
        day_start=time(8, 0),
    )
    print(f"👤 Owner Registered: {owner.name}")
    print(f"⏰ Daily Time Budget: {owner.available_minutes} minutes (Starting at {owner.day_start.strftime('%H:%M')})\n")

    # 2. Create two pets
    cat = Pet(name="Mochi", species="Cat", breed="Scottish Fold", age_years=4.0)
    dog = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age_years=2.5)

    owner.add_pet(cat)
    owner.add_pet(dog)
    print(f"🐶 Registered Pets: {dog.name} ({dog.breed}) and 🐱 {cat.name} ({cat.breed})\n")

    # 3. Add care tasks across both pets with diverse priorities and durations
    cat.add_task(
        Task(
            title="Insulin Injection",
            duration_minutes=15,
            priority="critical",
            category="medication",
            preferred_time=time(8, 0),
        )
    )
    dog.add_task(
        Task(
            title="Morning Walk",
            duration_minutes=30,
            priority="high",
            category="walk",
            preferred_time=time(8, 30),
        )
    )
    dog.add_task(
        Task(
            title="Breakfast Feeding",
            duration_minutes=15,
            priority="high",
            category="feeding",
            preferred_time=time(9, 0),
        )
    )
    cat.add_task(
        Task(
            title="Brushing & Coat Care",
            duration_minutes=20,
            priority="medium",
            category="grooming",
        )
    )
    dog.add_task(
        Task(
            title="Agility Park Play",
            duration_minutes=40,
            priority="low",
            category="enrichment",
        )
    )

    print(f"📋 Total Tasks Added: {len(owner.get_all_tasks())} pending across all pets.\n")

    # 4. Run the scheduler across all pets
    scheduler = Scheduler(strategy="priority_first")
    print(f"🧠 Building schedule using strategy: '{scheduler.strategy}'...\n")

    plan = scheduler.build_plan(owner)
    scheduled = plan["scheduled"]
    skipped = plan["skipped"]
    minutes_used = plan["minutes_used"]

    # 5. Display the scheduled itinerary
    print("📅 TODAY'S ITINERARY:")
    print_schedule_table(scheduled)

    # 6. Display skipped tasks if any
    if skipped:
        print("\n⚠️  SKIPPED TASKS (Exceeded Owner's 90-minute Budget):")
        for task in skipped:
            print(f"  • [{task.priority.upper()}] {task.title} for {task.pet_name} ({task.duration_minutes} min)")

    # 7. Print summary and scheduler explanation
    print(f"\n📊 Summary: {len(scheduled)} tasks scheduled ({minutes_used}/{owner.available_minutes} min), {len(skipped)} skipped.")
    remaining = owner.available_minutes - minutes_used
    print(f"⏳ Remaining Time Buffer: {remaining} min\n")
    print("=" * 70)


if __name__ == "__main__":
    main()
