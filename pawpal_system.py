"""PawPal+ core system.

Core object-oriented domain model and scheduling engine for pet care management.
Implements Owner, Pet, Task, and Scheduler classes.
"""

from dataclasses import dataclass, field
import datetime as dt_module
from datetime import date, datetime, time, timedelta
import json
import os
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

class _PriorityWeightsDict(dict):
    """Dictionary supporting case-insensitive lookup and CRITICAL fallback."""

    def __getitem__(self, key: Any) -> int:
        if isinstance(key, str):
            k = key.upper()
            if k == "CRITICAL":
                return 4
            if k in self:
                return super().__getitem__(k)
        return super().__getitem__(key)

    def get(self, key: Any, default: Any = 2) -> Any:
        if isinstance(key, str):
            k = key.upper()
            if k == "CRITICAL":
                return 4
            if k in self:
                return super().get(k, default)
        return super().get(key, default)


PRIORITY_WEIGHTS: dict[str, int] = _PriorityWeightsDict({
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
})


def _task_effective_time(t: Any) -> time:
    """Extract a normalized datetime.time for chronological sorting."""
    sched = getattr(t, "scheduled_time", None)
    if isinstance(sched, datetime):
        return sched.time()
    if isinstance(sched, time):
        return sched
    s_dt = getattr(t, "scheduled_datetime", None)
    if isinstance(s_dt, datetime):
        return s_dt.time()
    start_t = getattr(t, "start_time", None)
    if isinstance(start_t, datetime):
        return start_t.time()
    if isinstance(start_t, time):
        return start_t
    pref_t = getattr(t, "preferred_time", None)
    if isinstance(pref_t, datetime):
        return pref_t.time()
    if isinstance(pref_t, time):
        return pref_t
    return time(23, 59, 59)


def add_minutes_to_time(base_time: time, minutes: int) -> time:
    """Helper to add minutes to a standard datetime.time object."""
    dt = datetime.combine(date.today(), base_time) + timedelta(minutes=minutes)
    return dt.time()


def _parse_time(val: Any) -> Optional[time]:
    """Parse time from an ISO string, time object, or datetime object."""
    if val is None:
        return None
    if isinstance(val, time):
        return val
    if isinstance(val, datetime):
        return val.time()
    val_str = str(val).strip()
    if not val_str:
        return None
    try:
        if "T" in val_str:
            return datetime.fromisoformat(val_str).time()
        return time.fromisoformat(val_str)
    except Exception:
        return None


def _parse_datetime(val: Any) -> Optional[datetime]:
    """Parse datetime from an ISO string or datetime object."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    val_str = str(val).strip()
    if not val_str:
        return None
    try:
        return datetime.fromisoformat(val_str)
    except Exception:
        return None


def _parse_time_or_datetime(val: Any) -> Optional[Union[time, datetime]]:
    """Parse either a time or a datetime from an ISO formatted string."""
    if val is None:
        return None
    if isinstance(val, (datetime, time)):
        return val
    val_str = str(val).strip()
    if not val_str:
        return None
    try:
        if "T" in val_str or "-" in val_str:
            return datetime.fromisoformat(val_str)
        return time.fromisoformat(val_str)
    except Exception:
        try:
            return time.fromisoformat(val_str)
        except Exception:
            return None


@dataclass
class Task:
    """A single unit of pet care: a walk, a feeding, a dose of medication, a vet visit."""

    title: str = ""
    duration_minutes: int = 30
    priority: str = "medium"  # "low" | "medium" | "high" | "critical"
    category: str = "general"  # "walk" | "feeding" | "medication" | "appointment" | ...
    preferred_time: time | None = None
    completed: bool = False
    start_time: time | None = None  # assigned by Scheduler, not by the user
    scheduled_time: time | None = None  # chronological scheduled time
    scheduled_datetime: datetime | None = None
    pet_name: str = ""
    description: str = ""
    recurrence: str = "NONE"  # "NONE" | "DAILY" | "WEEKLY"
    task_id: str = field(default_factory=lambda: uuid4().hex[:8])

    def __post_init__(self) -> None:
        if not self.title and self.description:
            self.title = self.description
        elif not self.description and self.title:
            self.description = self.title
        if self.scheduled_datetime is not None:
            if self.scheduled_time is None:
                self.scheduled_time = self.scheduled_datetime.time()
            if self.preferred_time is None:
                self.preferred_time = self.scheduled_datetime.time()
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

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create the next occurrence of a recurring task, or None if recurrence is NONE."""
        rec = self.recurrence.upper()
        if rec == "DAILY":
            days = 1
        elif rec == "WEEKLY":
            days = 7
        else:
            return None

        # Calculate next datetime
        if self.scheduled_datetime is not None:
            next_datetime = self.scheduled_datetime + timedelta(days=days)
        elif isinstance(self.scheduled_time, datetime):
            next_datetime = self.scheduled_time + timedelta(days=days)
        else:
            base_t = self.scheduled_time or self.preferred_time or time(8, 0)
            next_datetime = datetime.combine(date.today() + timedelta(days=days), base_t)

        # Calculate next scheduled_time
        if isinstance(self.scheduled_time, datetime):
            next_scheduled_time = self.scheduled_time + timedelta(days=days)
        elif self.scheduled_time is not None:
            next_scheduled_time = self.scheduled_time
        else:
            next_scheduled_time = next_datetime.time()

        next_task = Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            preferred_time=self.preferred_time,
            completed=False,
            start_time=None,
            scheduled_time=next_scheduled_time,
            scheduled_datetime=next_datetime,
            pet_name=self.pet_name,
            description=self.description,
            recurrence=self.recurrence,
        )
        return next_task

    def mark_complete(self) -> Optional["Task"]:
        """Flag this task as done for the day and return next occurrence if recurring."""
        self.completed = True
        return self.create_next_occurrence()

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

    def to_dict(self) -> dict[str, Any]:
        """Serialize Task to a dictionary for JSON persistence."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "preferred_time": self.preferred_time.isoformat() if self.preferred_time else None,
            "completed": self.completed,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "scheduled_datetime": self.scheduled_datetime.isoformat() if self.scheduled_datetime else None,
            "pet_name": self.pet_name,
            "recurrence": self.recurrence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Task":
        """Deserialize a Task from a dictionary using ISO formatted strings."""
        pref_t = _parse_time(data.get("preferred_time"))
        s_t = _parse_time(data.get("start_time"))
        sch_t = _parse_time_or_datetime(data.get("scheduled_time"))
        sch_dt = _parse_datetime(data.get("scheduled_datetime"))
        return cls(
            task_id=data.get("task_id", uuid4().hex[:8]),
            title=data.get("title", ""),
            description=data.get("description", ""),
            duration_minutes=int(data.get("duration_minutes", 30)),
            priority=data.get("priority", "medium"),
            category=data.get("category", "general"),
            preferred_time=pref_t,
            completed=bool(data.get("completed", False)),
            start_time=s_t,
            scheduled_time=sch_t,
            scheduled_datetime=sch_dt,
            pet_name=data.get("pet_name", ""),
            recurrence=data.get("recurrence", "NONE"),
        )



@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    breed: str = ""
    age_years: float = 0.0
    notes: str = ""
    pet_id: str = ""
    tasks: list[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.pet_id:
            self.pet_id = f"pet_{uuid4().hex[:6]}"

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

    def get_pending_tasks(self) -> list[Task]:
        """Return the tasks that are not yet marked complete (alias for pending_tasks)."""
        return self.pending_tasks()

    def complete_task(self, task_id: str | Any) -> Optional[Task]:
        """Mark task complete, automatically instantiate and append next occurrence if recurring."""
        target_id = task_id.task_id if hasattr(task_id, "task_id") else task_id
        for t in self.tasks:
            if t.task_id == target_id:
                t.completed = True
                next_t = t.create_next_occurrence()
                if next_t is not None:
                    if not next_t.pet_name:
                        next_t.pet_name = self.name
                    self.tasks.append(next_t)
                return next_t
        return None

    def to_dict(self) -> dict[str, Any]:
        """Serialize Pet to a dictionary for JSON persistence."""
        return {
            "pet_id": self.pet_id,
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age_years": self.age_years,
            "notes": self.notes,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pet":
        """Deserialize Pet from a dictionary."""
        pet = cls(
            pet_id=data.get("pet_id", ""),
            name=data.get("name", ""),
            species=data.get("species", "Other"),
            breed=data.get("breed", ""),
            age_years=float(data.get("age_years", 0.0)),
            notes=data.get("notes", ""),
        )
        for t_dict in data.get("tasks", []):
            pet.add_task(Task.from_dict(t_dict))
        return pet


@dataclass
class Owner:
    """The person doing the caring, plus the time constraints they are working within."""

    name: str
    email: str = ""
    contact: str = ""
    available_minutes: int = 120
    day_start: time = time(8, 0)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.email and self.contact:
            self.email = self.contact
        elif not self.contact and self.email:
            self.contact = self.email

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

    def to_dict(self) -> dict[str, Any]:
        """Serialize Owner profile and all pet commitments to a dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "contact": self.contact,
            "available_minutes": self.available_minutes,
            "day_start": self.day_start.isoformat(),
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Owner":
        """Deserialize Owner from a dictionary."""
        day_st = _parse_time(data.get("day_start")) or time(8, 0)
        owner = cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            contact=data.get("contact", ""),
            available_minutes=int(data.get("available_minutes", 120)),
            day_start=day_st,
        )
        for p_dict in data.get("pets", []):
            owner.add_pet(Pet.from_dict(p_dict))
        return owner

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Serialize owner profile and all pet commitments to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Load owner profile and all pet commitments from a JSON file.

        Handles missing files gracefully by returning a new or default Owner instance.
        """
        if not os.path.exists(filepath):
            return cls(
                name="Alex Carter",
                email="alex@example.com",
                contact="alex@example.com",
                available_minutes=180,
                day_start=time(8, 0),
            )
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception:
            return cls(
                name="Alex Carter",
                email="alex@example.com",
                contact="alex@example.com",
                available_minutes=180,
                day_start=time(8, 0),
            )


def save_to_json(owner: Owner, filepath: str = "data.json") -> None:
    """Save owner and all pets and tasks to a JSON file."""
    owner.save_to_json(filepath)


def load_from_json(filepath: str = "data.json") -> Owner:
    """Load owner and all pets and tasks from a JSON file.

    Handles missing or corrupted files gracefully by returning a new or default Owner instance.
    """
    return Owner.load_from_json(filepath)


@dataclass
class Scheduler:
    """Turns tasks across multiple pets into a time-ordered daily plan."""

    strategy: str = "priority_first"
    owner: Owner | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task directly to the scheduler."""
        self.tasks.append(task)

    def complete_task(self, task_id: str | Any) -> Optional[Task]:
        """Mark a task complete across owner's pets, appending next occurrence if recurring."""
        target_id = task_id.task_id if hasattr(task_id, "task_id") else task_id
        if self.owner is not None:
            for pet in self.owner.pets:
                for t in pet.tasks:
                    if t.task_id == target_id:
                        return pet.complete_task(target_id)
        for t in self.tasks:
            if t.task_id == target_id:
                t.completed = True
                next_t = t.create_next_occurrence()
                if next_t is not None:
                    self.tasks.append(next_t)
                return next_t
        return None

    def build_plan(self, owner: Owner | None = None, pets: list[Pet] | Pet | None = None) -> dict:
        """Build the day's plan across multiple pets (or a specified pet subset).

        Returns a dict shaped like:
            {"scheduled": [Task, ...], "skipped": [Task, ...], "minutes_used": int}
        """
        target_owner = owner or self.owner
        if target_owner is None:
            raise ValueError("No owner provided or attached to scheduler.")

        # Retrieve pending tasks
        if pets is None:
            tasks = target_owner.get_all_tasks(pending_only=True)
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
            if minutes_used + task.duration_minutes <= target_owner.available_minutes:
                scheduled.append(task)
                minutes_used += task.duration_minutes
            else:
                skipped.append(task)

        # Assign back-to-back start times from target_owner.day_start
        self.assign_times(scheduled, target_owner.day_start)

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
        base_start = target.day_start if isinstance(target, Owner) else (self.owner.day_start if self.owner else time(8, 0))
        cur_t = base_start
        for t in task_list:
            if t.scheduled_time is None:
                t.scheduled_time = t.start_time or t.preferred_time or cur_t
                cur_t = add_minutes_to_time(cur_t, t.duration_minutes)

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

    def collect_all_tasks(self) -> List[Task]:
        """Aggregate all tasks across all pets for the attached owner or scheduler tasks."""
        return self._resolve_tasks()

    def _resolve_tasks(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Resolve tasks from argument, attached owner, or scheduler task list."""
        if tasks is not None:
            return list(tasks)
        if self.owner is not None:
            return self.owner.get_all_tasks(pending_only=False)
        return list(self.tasks)

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by scheduled time, tie-breaking by priority weight descending."""
        task_list = self._resolve_tasks(tasks)
        return sorted(
            task_list,
            key=lambda t: (
                _task_effective_time(t),
                -PRIORITY_WEIGHTS.get(t.priority, 2),
            ),
        )

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority first, then by time, pushing completed tasks to bottom.

        Sorting Strategy:
        1. Incomplete tasks first, completed tasks pushed to bottom.
        2. Primary key: Priority weight descending (HIGH: 3 > MEDIUM: 2 > LOW: 1).
        3. Secondary key: Chronological scheduled_time ascending (earliest time first within same priority tier).
        """
        task_list = self._resolve_tasks(tasks)
        return sorted(
            task_list,
            key=lambda t: (
                1 if (t.completed or t.is_completed) else 0,
                -PRIORITY_WEIGHTS.get(t.priority, 2),
                _task_effective_time(t),
            ),
        )

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        is_completed: Optional[bool] = None,
        priority: Optional[str] = None,
    ) -> List[Task]:
        """Filter aggregated tasks across all pets by pet name, completion status, or priority tier."""
        task_list = self.owner.get_all_tasks(pending_only=False) if self.owner else list(self.tasks)
        filtered: List[Task] = []
        for t in task_list:
            if pet_name is not None and t.pet_name.lower() != pet_name.lower():
                continue
            if is_completed is not None and t.is_completed != is_completed:
                continue
            if priority is not None and t.priority.lower() != priority.lower():
                continue
            filtered.append(t)
        return filtered

    def find_next_available_slot(
        self,
        duration_minutes: int,
        target_date: Optional[date] = None,
        day_start: time = time(8, 0),
        day_end: time = time(20, 0),
        search_date: Optional[date] = None,
        work_day_start: Optional[time] = None,
        work_day_end: Optional[time] = None,
    ) -> Optional[datetime]:
        """Find the earliest continuous unbooked window of at least duration_minutes.

        Collects pending tasks for target_date across all pets, merges overlapping
        or contiguous busy intervals, and scans between day_start and day_end.
        """
        actual_date = target_date or search_date or date.today()
        actual_start = work_day_start or day_start
        actual_end = work_day_end or day_end

        needed = timedelta(minutes=duration_minutes)
        window_start = datetime.combine(actual_date, actual_start)
        window_end = datetime.combine(actual_date, actual_end)

        # Gather and filter non-completed tasks for this date across all pets
        day_tasks: List[tuple[Task, datetime]] = []
        for t in self.collect_all_tasks():
            if t.is_completed:
                continue

            if isinstance(t.scheduled_time, datetime):
                s_dt = t.scheduled_time
            elif t.scheduled_datetime is not None:
                s_dt = t.scheduled_datetime
            elif isinstance(t.scheduled_time, time):
                s_dt = datetime.combine(actual_date, t.scheduled_time)
            elif t.start_time is not None:
                s_dt = datetime.combine(actual_date, t.start_time)
            elif t.preferred_time is not None:
                s_dt = datetime.combine(actual_date, t.preferred_time)
            else:
                continue

            if s_dt.date() == actual_date:
                day_tasks.append((t, s_dt))

        # Sort tasks chronologically by scheduled start time
        day_tasks.sort(key=lambda item: item[1])

        # Merge overlapping or contiguous busy intervals
        busy_intervals: List[list[datetime]] = []
        for t, s_dt in day_tasks:
            start = max(s_dt, window_start)
            end = min(s_dt + timedelta(minutes=t.duration_minutes), window_end)
            if start < end:
                if not busy_intervals or busy_intervals[-1][1] < start:
                    busy_intervals.append([start, end])
                else:
                    busy_intervals[-1][1] = max(busy_intervals[-1][1], end)

        # Scan for the earliest continuous idle window
        current_time = window_start
        for b_start, b_end in busy_intervals:
            if b_start - current_time >= needed:
                return current_time
            current_time = max(current_time, b_end)

        if window_end - current_time >= needed:
            return current_time

        return None

    def detect_conflicts(
        self, tasks: Optional[List[Task]] = None
    ) -> List[Dict[str, Any]]:
        """Detect all pairwise overlapping time windows among pending tasks across all pets."""
        task_list = self._resolve_tasks(tasks)
        pending = [t for t in task_list if not t.completed]

        # Extract pending tasks with valid time windows
        timed_tasks: List[tuple[Task, datetime, datetime]] = []
        for t in pending:
            if t.scheduled_datetime is not None:
                start_dt = t.scheduled_datetime
            elif t.scheduled_time is not None:
                start_dt = datetime.combine(date.today(), t.scheduled_time)
            elif t.start_time is not None:
                start_dt = datetime.combine(date.today(), t.start_time)
            elif t.preferred_time is not None:
                start_dt = datetime.combine(date.today(), t.preferred_time)
            else:
                continue
            end_dt = start_dt + timedelta(minutes=t.duration_minutes)
            timed_tasks.append((t, start_dt, end_dt))

        # Sort by start_time for efficient O(n log n) conflict detection
        timed_tasks.sort(key=lambda item: item[1])

        conflicts: List[Dict[str, Any]] = []
        n = len(timed_tasks)
        for i in range(n):
            task_a, start_a, end_a = timed_tasks[i]
            for j in range(i + 1, n):
                task_b, start_b, end_b = timed_tasks[j]
                if start_b >= end_a:
                    break
                if start_a < end_b and start_b < end_a:
                    overlap_start = max(start_a, start_b)
                    overlap_end = min(end_a, end_b)
                    overlap_min = int((overlap_end - overlap_start).total_seconds() / 60)
                    if overlap_min > 0:
                        pet_a = task_a.pet_name or "All"
                        pet_b = task_b.pet_name or "All"
                        time_a = f"{start_a.strftime('%H:%M')} - {end_a.strftime('%H:%M')}"
                        time_b = f"{start_b.strftime('%H:%M')} - {end_b.strftime('%H:%M')}"
                        msg = (
                            f"[CONFLICT] '{task_a.title}' ({pet_a}, {time_a}) overlaps with "
                            f"'{task_b.title}' ({pet_b}, {time_b}) by {overlap_min} mins."
                        )
                        conflicts.append(
                            {
                                "task_1": task_a,
                                "task_2": task_b,
                                "overlap_minutes": overlap_min,
                                "warning_message": msg,
                            }
                        )

        return conflicts
