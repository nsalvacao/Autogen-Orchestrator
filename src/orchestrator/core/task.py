"""
Task - Defines the task structure and management for the orchestrator.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    """Status of a task in the orchestration system."""

    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    NEEDS_CORRECTION = "needs_correction"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Priority levels for tasks."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskType(str, Enum):
    """Types of tasks that can be processed."""

    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    SECURITY_REVIEW = "security_review"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    BUG_FIX = "bug_fix"
    FEATURE = "feature"


@dataclass
class TaskResult:
    """Result of task execution."""

    success: bool
    output: Any = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """
    Represents a task in the orchestration system.

    Tasks are the fundamental unit of work that agents process.
    They support hierarchical decomposition and tracking through
    the entire lifecycle.
    """

    title: str
    description: str
    task_type: TaskType = TaskType.DEVELOPMENT
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: str | None = None
    subtasks: list[str] = field(default_factory=list)  # List of subtask IDs
    assigned_agent: str | None = None
    dependencies: list[str] = field(default_factory=list)  # List of task IDs
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: TaskResult | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    correction_count: int = 0
    max_corrections: int = 3

    def can_start(self, completed_tasks: set[str]) -> bool:
        """
        Check if the task can be started based on dependencies.

        Args:
            completed_tasks: Set of completed task IDs.

        Returns:
            True if all dependencies are met.
        """
        return all(dep in completed_tasks for dep in self.dependencies)

    def is_terminal(self) -> bool:
        """Check if the task is in a terminal state."""
        return self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        )

    def needs_more_corrections(self) -> bool:
        """Check if the task can have more correction attempts."""
        return self.correction_count < self.max_corrections

    def update_status(self, new_status: TaskStatus) -> None:
        """
        Update the task status and timestamps.

        Args:
            new_status: The new status to set.
        """
        self.status = new_status
        self.updated_at = datetime.now()

        if new_status == TaskStatus.IN_PROGRESS and self.started_at is None:
            self.started_at = datetime.now()
        elif new_status == TaskStatus.COMPLETED:
            self.completed_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_task_id": self.parent_task_id,
            "subtasks": self.subtasks,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "correction_count": self.correction_count,
            "metadata": self.metadata,
        }


class TaskQueue:
    """
    Priority queue for task management.

    Handles task scheduling based on priority and dependencies.
    """

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._completed_tasks: set[str] = set()

    def add_task(self, task: Task) -> None:
        """Add a task to the queue."""
        self._tasks[task.id] = task

    def get_task(self, task_id: str) -> Task | None:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def get_next_task(self) -> Task | None:
        """
        Get the next task that is ready to be processed.

        Returns the highest priority task whose dependencies are met.
        """
        ready_tasks = [
            task
            for task in self._tasks.values()
            if task.status == TaskStatus.PENDING and task.can_start(self._completed_tasks)
        ]

        if not ready_tasks:
            return None

        # Sort by priority (CRITICAL > HIGH > MEDIUM > LOW)
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }

        ready_tasks.sort(key=lambda t: (priority_order[t.priority], t.created_at))
        return ready_tasks[0]

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed."""
        if task_id in self._tasks:
            self._tasks[task_id].update_status(TaskStatus.COMPLETED)
            self._completed_tasks.add(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks in the queue."""
        return list(self._tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self._tasks.values() if task.status == status]
