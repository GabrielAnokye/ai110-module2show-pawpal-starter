"""PawPal+ core system.

Core object-oriented domain model and scheduling engine for pet care management.
Implements Owner, Pet, Task, and Scheduler classes.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Any
from uuid import uuid4

PRIORITY_WEIGHTS: dict[str, float] = {
    "critical": 40.0,
    "high": 30.0,
    "medium": 20.0,
    "low": 10.0,
}


def add_minutes_to_time(base_time: time, minutes: int) -> time:
    """Helper to add minutes to a standard datetime.time object."""
    dt = datetime.combine(date.today(), base_time) + timedelta(minutes=minutes)
    return dt.time()


@dataclass
class Task:
    """A single unit of pet care: a walk, a feeding, a dose of medication, a vet visit."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high" | "critical"
    category: str = "general"  # "walk" | "feeding" | "medication" | "appointment" | ...
    preferred_time: time | None = None
    completed: bool = False
    start_time: time | None = None  # assigned by Scheduler, not by the user
    scheduled_time: time | None = None  # chronological scheduled time
    pet_name: str = ""
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def __post_init__(self) -> None:
        if self.scheduled_time is None and self.start_time is not None:
            self.scheduled_time = self.start_time
        elif self.start_time is None and self.scheduled_time is not None:
            self.start_time = self.scheduled_time
        elif self.scheduled_time is None and self.preferred_time is not None:
            self.scheduled_time = self.preferred_time

    @property
    def is_completed(self) -> bool:
        """Alias property for completion status."""
        return self.completed

    @is_completed.setter
    def is_completed(self, val: bool) -> None:
        self.completed = val

    def weight(self) -> float:
        """Return a sortable score for this task. Higher means schedule it sooner."""
        base = PRIORITY_WEIGHTS.get(self.priority.lower(), 20.0)
        # Small boost for time-critical care such as medication
        if self.category.lower() == "medication":
            base += 5.0
        return base

    def mark_complete(self) -> None:
        """Flag this task as done for the day."""
        self.completed = True

    def mark_pending(self) -> None:
        """Flag this task as pending/not completed."""
        self.completed = False

    def describe(self) -> str:
        """Return a one-line human-readable summary of this task."""
        effective_time = self.scheduled_time or self.start_time
        time_str = f" at {effective_time.strftime('%H:%M')}" if effective_time else ""
        pet_str = f" for {self.pet_name}" if self.pet_name else ""
        status = " [DONE]" if self.completed else ""
        return (
            f"[{self.priority.upper()}] {self.title}{pet_str} "
            f"({self.duration_minutes} min){time_str}{status}"
        )


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet and associate the pet name."""
        if not task.pet_name:
            task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str | Any) -> bool:
        """Remove a task by id or Task instance. Return True if a task was removed."""
        target_id = task_id.task_id if hasattr(task_id, "task_id") else task_id
        initial_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.task_id != target_id]
        return len(self.tasks) < initial_len

    def update_task(self, task_id: str, fields: dict) -> Task:
        """Update the given attributes on a task and return it."""
        for t in self.tasks:
            if t.task_id == task_id:
                for k, v in fields.items():
                    if hasattr(t, k):
                        setattr(t, k, v)
                return t
        raise KeyError(f"Task with id '{task_id}' not found on pet '{self.name}'")

    def pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet marked complete."""
        return [t for t in self.tasks if not t.completed]


@dataclass
class Owner:
    """The person doing the caring, plus the time constraints they are working within."""

    name: str
    email: str = ""
    available_minutes: int = 120
    day_start: time = time(8, 0)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Return True if a pet was removed."""
        initial_len = len(self.pets)
        self.pets = [p for p in self.pets if p.name.lower() != pet_name.lower()]
        return len(self.pets) < initial_len

    def get_pet(self, pet_name: str) -> Pet:
        """Look up one of this owner's pets by name."""
        for p in self.pets:
            if p.name.lower() == pet_name.lower():
                return p
        raise KeyError(f"Pet '{pet_name}' not found for owner '{self.name}'")

    def get_all_tasks(self, pending_only: bool = True) -> list[Task]:
        """Retrieve all tasks across all pets belonging to this owner."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            tasks = pet.pending_tasks() if pending_only else pet.tasks
            all_tasks.extend(tasks)
        return all_tasks


@dataclass
class Scheduler:
    """Turns tasks across multiple pets into a time-ordered daily plan."""

    strategy: str = "priority_first"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task directly to the scheduler."""
        self.tasks.append(task)

    def build_plan(self, owner: Owner, pets: list[Pet] | Pet | None = None) -> dict:
        """Build the day's plan across multiple pets (or a specified pet subset).

        Returns a dict shaped like:
            {"scheduled": [Task, ...], "skipped": [Task, ...], "minutes_used": int}
        """
        # Retrieve pending tasks
        if pets is None:
            tasks = owner.get_all_tasks(pending_only=True)
        elif isinstance(pets, Pet):
            tasks = pets.pending_tasks()
        else:
            tasks = [t for p in pets for t in p.pending_tasks()]

        # Sort tasks according to strategy
        sorted_tasks = self.sort_tasks(tasks)

        scheduled: list[Task] = []
        skipped: list[Task] = []
        minutes_used = 0

        # Filter and partition tasks based on available time budget
        for task in sorted_tasks:
            if minutes_used + task.duration_minutes <= owner.available_minutes:
                scheduled.append(task)
                minutes_used += task.duration_minutes
            else:
                skipped.append(task)

        # Assign back-to-back start times from owner.day_start
        self.assign_times(scheduled, owner.day_start)

        return {
            "scheduled": scheduled,
            "skipped": skipped,
            "minutes_used": minutes_used,
        }

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by scheduling importance. Does not mutate the input list."""
        if self.strategy == "duration_first":
            return sorted(tasks, key=lambda t: t.duration_minutes)
        # Default: priority_first using task.weight() descending
        return sorted(tasks, key=lambda t: t.weight(), reverse=True)

    def filter_by_time(self, tasks: list[Task], budget: int) -> list[Task]:
        """Keep tasks that fit within the given minute budget; drop the rest."""
        result: list[Task] = []
        minutes_used = 0
        for task in tasks:
            if minutes_used + task.duration_minutes <= budget:
                result.append(task)
                minutes_used += task.duration_minutes
        return result

    def assign_times(self, tasks: list[Task], day_start: time) -> list[Task]:
        """Set start_time and scheduled_time on each task, laying them out back-to-back from day_start."""
        current_time = day_start
        for task in tasks:
            task.start_time = current_time
            task.scheduled_time = current_time
            current_time = add_minutes_to_time(current_time, task.duration_minutes)
        return tasks

    def get_daily_schedule(
        self, target: Owner | Pet | list[Task] | None = None
    ) -> list[Task]:
        """Retrieve and return a list of tasks strictly sorted chronologically by scheduled_time.

        Accepts an Owner, Pet, list of Tasks, or defaults to tasks added directly to the scheduler.
        """
        if target is None:
            task_list = list(self.tasks)
        elif isinstance(target, Owner):
            task_list = target.get_all_tasks(pending_only=False)
        elif isinstance(target, Pet):
            task_list = list(target.tasks)
        elif isinstance(target, list):
            task_list = list(target)
        else:
            task_list = []

        # Ensure each task has a scheduled_time if start_time or preferred_time exists
        for t in task_list:
            if t.scheduled_time is None:
                t.scheduled_time = t.start_time or t.preferred_time

        return sorted(task_list, key=lambda t: t.scheduled_time or time(0, 0))

    def explain(self, plan: dict) -> str:
        """Explain the plan: what was scheduled, in what order, and what was cut."""
        lines = []
        scheduled: list[Task] = plan.get("scheduled", [])
        skipped: list[Task] = plan.get("skipped", [])
        minutes_used: int = plan.get("minutes_used", 0)

        lines.append(
            f"Plan Summary: {len(scheduled)} tasks scheduled ({minutes_used} min used), "
            f"{len(skipped)} skipped."
        )

        if scheduled:
            lines.append("\nScheduled Tasks:")
            for idx, t in enumerate(scheduled, 1):
                lines.append(f"  {idx}. {t.describe()}")

        if skipped:
            lines.append("\nSkipped Tasks (exceeded time budget):")
            for idx, t in enumerate(skipped, 1):
                lines.append(f"  • {t.describe()}")

        return "\n".join(lines)
