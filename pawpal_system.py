"""PawPal+ core system.

Class skeleton generated from diagrams/uml.mmd. Attributes are final; method
bodies are stubs to be implemented one at a time (CLI-first, then wired into app.py).
"""

from dataclasses import dataclass, field
from datetime import time
from uuid import uuid4


@dataclass
class Task:
    """A single unit of pet care: a walk, a feeding, a dose of medication, a vet visit."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # "walk" | "feeding" | "medication" | "appointment" | ...
    preferred_time: time | None = None
    completed: bool = False
    start_time: time | None = None  # assigned by Scheduler, not by the user
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def weight(self) -> float:
        """Return a sortable score for this task. Higher means schedule it sooner."""
        raise NotImplementedError

    def mark_complete(self) -> None:
        """Flag this task as done for the day."""
        raise NotImplementedError

    def describe(self) -> str:
        """Return a one-line human-readable summary of this task."""
        raise NotImplementedError


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
        """Attach a new care task to this pet."""
        raise NotImplementedError

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by id. Return True if a task was removed."""
        raise NotImplementedError

    def update_task(self, task_id: str, fields: dict) -> Task:
        """Update the given attributes on a task and return it."""
        raise NotImplementedError

    def pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet marked complete."""
        raise NotImplementedError


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
        raise NotImplementedError

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Return True if a pet was removed."""
        raise NotImplementedError

    def get_pet(self, pet_name: str) -> Pet:
        """Look up one of this owner's pets by name."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Turns a pet's task list into a time-ordered daily plan the owner can actually follow."""

    strategy: str = "priority_first"

    def build_plan(self, owner: Owner, pet: Pet) -> dict:
        """Build the day's plan.

        Returns a dict shaped like:
            {"scheduled": [Task, ...], "skipped": [Task, ...], "minutes_used": int}
        """
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by scheduling importance. Does not mutate the input list."""
        raise NotImplementedError

    def filter_by_time(self, tasks: list[Task], budget: int) -> list[Task]:
        """Keep tasks that fit within the given minute budget; drop the rest."""
        raise NotImplementedError

    def assign_times(self, tasks: list[Task], day_start: time) -> list[Task]:
        """Set start_time on each task, laying them out back-to-back from day_start."""
        raise NotImplementedError

    def explain(self, plan: dict) -> str:
        """Explain the plan: what was scheduled, in what order, and what was cut."""
        raise NotImplementedError
