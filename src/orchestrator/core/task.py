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
    RETRYING = "retrying"
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


class RetryStrategy(str, Enum):
    """Retry strategies for failed tasks."""

    NONE = "none"
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryConfig:
    """Configuration for task retry behavior."""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    retry_on_errors: list[str] = field(default_factory=list)  # Empty = retry on all errors

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt: The current attempt number (1-based).

        Returns:
            Delay in seconds before the next retry.
        """
        if self.strategy == RetryStrategy.NONE:
            return 0.0
        elif self.strategy == RetryStrategy.IMMEDIATE:
            return 0.0
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.base_delay_seconds * attempt
        else:  # EXPONENTIAL
            delay = self.base_delay_seconds * (2 ** (attempt - 1))

        return min(delay, self.max_delay_seconds)

    def should_retry(self, error_message: str | None) -> bool:
        """
        Check if a retry should be attempted based on the error.

        Args:
            error_message: The error message from the failed attempt.

        Returns:
            True if the error is retryable, False otherwise.
        """
        if self.strategy == RetryStrategy.NONE:
            return False

        if not self.retry_on_errors:
            return True  # Retry on all errors if no specific errors configured

        if error_message is None:
            return True

        return any(err.lower() in error_message.lower() for err in self.retry_on_errors)


@dataclass
class RetryState:
    """Tracks the retry state of a task."""

    attempt: int = 0
    last_error: str | None = None
    last_attempt_at: datetime | None = None
    next_retry_at: datetime | None = None
    errors: list[dict[str, Any]] = field(default_factory=list)

    def record_attempt(self, error_message: str | None = None) -> None:
        """
        Record a retry attempt.

        Args:
            error_message: The error message if the attempt failed.
        """
        self.attempt += 1
        self.last_error = error_message
        self.last_attempt_at = datetime.now()
        if error_message:
            self.errors.append({
                "attempt": self.attempt,
                "error": error_message,
                "timestamp": datetime.now().isoformat(),
            })

    def can_retry(self, config: RetryConfig) -> bool:
        """
        Check if more retries are allowed.

        Args:
            config: The retry configuration.

        Returns:
            True if more retries are allowed.
        """
        return self.attempt < config.max_retries and config.should_retry(self.last_error)

    def to_dict(self) -> dict[str, Any]:
        """Convert retry state to dictionary representation."""
        return {
            "attempt": self.attempt,
            "last_error": self.last_error,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "next_retry_at": self.next_retry_at.isoformat() if self.next_retry_at else None,
            "errors": self.errors,
        }


@dataclass
class TaskResult:
    """Result of task execution."""

    success: bool
    output: Any = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    error_message: str | None = None
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    retryable: bool = True  # Indicates if the failure is retryable


@dataclass
class Task:
    """
    Represents a task in the orchestration system.

    Tasks are the fundamental unit of work that agents process.
    They support hierarchical decomposition and tracking through
    the entire lifecycle. Includes retry and recovery capabilities.
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
    # Retry and recovery fields
    retry_config: RetryConfig = field(default_factory=RetryConfig)
    retry_state: RetryState = field(default_factory=RetryState)

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

    def can_retry(self) -> bool:
        """
        Check if the task can be retried.

        Returns:
            True if retry is possible based on configuration and state.
        """
        return self.retry_state.can_retry(self.retry_config)

    def record_failure(self, error_message: str | None = None) -> None:
        """
        Record a task failure and prepare for potential retry.

        Args:
            error_message: The error message from the failed execution.
        """
        self.retry_state.record_attempt(error_message)
        self.updated_at = datetime.now()

        if self.can_retry():
            delay = self.retry_config.calculate_delay(self.retry_state.attempt)
            from datetime import timedelta
            self.retry_state.next_retry_at = datetime.now() + timedelta(seconds=delay)
            self.status = TaskStatus.RETRYING
        else:
            self.status = TaskStatus.FAILED
            self.result = TaskResult(
                success=False,
                error_message=error_message,
                metadata={"retry_state": self.retry_state.to_dict()},
            )

    def reset_for_retry(self) -> None:
        """Reset the task state for a retry attempt."""
        if self.status == TaskStatus.RETRYING:
            self.status = TaskStatus.PENDING
            self.retry_state.next_retry_at = None
            self.updated_at = datetime.now()

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
            "retry_config": {
                "strategy": self.retry_config.strategy.value,
                "max_retries": self.retry_config.max_retries,
                "base_delay_seconds": self.retry_config.base_delay_seconds,
                "max_delay_seconds": self.retry_config.max_delay_seconds,
            },
            "retry_state": self.retry_state.to_dict(),
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

    def mark_failed(self, task_id: str, error_message: str | None = None) -> bool:
        """
        Mark a task as failed and handle retry logic.

        Args:
            task_id: The ID of the task that failed.
            error_message: The error message from the failure.

        Returns:
            True if the task will be retried, False if it's permanently failed.
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        task.record_failure(error_message)
        return task.status == TaskStatus.RETRYING

    def get_tasks_ready_for_retry(self) -> list[Task]:
        """
        Get tasks that are ready to be retried.

        Returns:
            List of tasks whose retry delay has elapsed.
        """
        now = datetime.now()
        return [
            task
            for task in self._tasks.values()
            if task.status == TaskStatus.RETRYING
            and task.retry_state.next_retry_at is not None
            and task.retry_state.next_retry_at <= now
        ]

    def process_retries(self) -> list[str]:
        """
        Process tasks ready for retry, resetting them to PENDING.

        Returns:
            List of task IDs that were reset for retry.
        """
        retried_tasks = []
        for task in self.get_tasks_ready_for_retry():
            task.reset_for_retry()
            retried_tasks.append(task.id)
        return retried_tasks

    def get_failed_tasks(self) -> list[Task]:
        """Get all permanently failed tasks."""
        return self.get_tasks_by_status(TaskStatus.FAILED)

    def get_retrying_tasks(self) -> list[Task]:
        """Get all tasks waiting for retry."""
        return self.get_tasks_by_status(TaskStatus.RETRYING)

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks in the queue."""
        return list(self._tasks.values())

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get all tasks with a specific status."""
        return [task for task in self._tasks.values() if task.status == status]


@dataclass
class TaskTemplate:
    """
    Reusable task template with variable substitution.

    Templates allow defining reusable task patterns that can be
    instantiated with different values for common development scenarios.
    """

    name: str
    description_template: str
    task_type: TaskType = TaskType.DEVELOPMENT
    priority: TaskPriority = TaskPriority.MEDIUM
    variables: dict[str, Any] = field(default_factory=dict)  # Default variable values
    retry_config: RetryConfig | None = None
    max_corrections: int = 3
    metadata_template: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def create_task(
        self,
        title: str,
        variables: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> Task:
        """
        Create a task from this template.

        Args:
            title: The title for the task.
            variables: Variables to substitute in templates.
            **overrides: Additional overrides for task fields.

        Returns:
            A new Task instance based on this template.
        """
        # Merge default variables with provided variables
        merged_vars = {**self.variables, **(variables or {})}

        # Substitute variables in description
        description = self._substitute_variables(
            self.description_template, merged_vars
        )

        # Substitute variables in metadata
        metadata = {}
        for key, value in self.metadata_template.items():
            if isinstance(value, str):
                metadata[key] = self._substitute_variables(value, merged_vars)
            else:
                metadata[key] = value

        # Add template info to metadata
        metadata["template_name"] = self.name
        metadata["template_variables"] = merged_vars

        # Create the task
        task_kwargs: dict[str, Any] = {
            "title": title,
            "description": description,
            "task_type": overrides.get("task_type", self.task_type),
            "priority": overrides.get("priority", self.priority),
            "max_corrections": overrides.get("max_corrections", self.max_corrections),
            "metadata": {**metadata, **overrides.get("metadata", {})},
        }

        if self.retry_config:
            task_kwargs["retry_config"] = overrides.get("retry_config", self.retry_config)

        if "dependencies" in overrides:
            task_kwargs["dependencies"] = overrides["dependencies"]

        return Task(**task_kwargs)

    def _substitute_variables(
        self, template: str, variables: dict[str, Any]
    ) -> str:
        """
        Substitute variables in a template string.

        Variables are specified as ${variable_name} in the template.

        Args:
            template: The template string.
            variables: Variable values to substitute.

        Returns:
            The template with variables substituted.
        """
        result = template
        for key, value in variables.items():
            placeholder = f"${{{key}}}"
            result = result.replace(placeholder, str(value))
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary representation."""
        return {
            "name": self.name,
            "description_template": self.description_template,
            "task_type": self.task_type.value,
            "priority": self.priority.value,
            "variables": self.variables,
            "max_corrections": self.max_corrections,
            "metadata_template": self.metadata_template,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskTemplate":
        """Create a template from dictionary."""
        retry_config = None
        if "retry_config" in data:
            retry_data = data["retry_config"]
            retry_config = RetryConfig(
                strategy=RetryStrategy(retry_data.get("strategy", "exponential")),
                max_retries=retry_data.get("max_retries", 3),
                base_delay_seconds=retry_data.get("base_delay_seconds", 1.0),
                max_delay_seconds=retry_data.get("max_delay_seconds", 60.0),
            )

        return cls(
            name=data["name"],
            description_template=data["description_template"],
            task_type=TaskType(data.get("task_type", "development")),
            priority=TaskPriority(data.get("priority", "medium")),
            variables=data.get("variables", {}),
            retry_config=retry_config,
            max_corrections=data.get("max_corrections", 3),
            metadata_template=data.get("metadata_template", {}),
            tags=data.get("tags", []),
        )


class TaskTemplateLibrary:
    """
    Library of reusable task templates.

    Provides storage and retrieval of task templates for common
    development scenarios.
    """

    def __init__(self):
        self._templates: dict[str, TaskTemplate] = {}

    def add_template(self, template: TaskTemplate) -> None:
        """Add a template to the library."""
        self._templates[template.name] = template

    def get_template(self, name: str) -> TaskTemplate | None:
        """Get a template by name."""
        return self._templates.get(name)

    def remove_template(self, name: str) -> bool:
        """Remove a template from the library."""
        if name in self._templates:
            del self._templates[name]
            return True
        return False

    def list_templates(self) -> list[str]:
        """List all template names."""
        return list(self._templates.keys())

    def get_templates_by_tag(self, tag: str) -> list[TaskTemplate]:
        """Get templates with a specific tag."""
        return [t for t in self._templates.values() if tag in t.tags]

    def get_templates_by_type(self, task_type: TaskType) -> list[TaskTemplate]:
        """Get templates for a specific task type."""
        return [t for t in self._templates.values() if t.task_type == task_type]

    def create_task_from_template(
        self,
        template_name: str,
        title: str,
        variables: dict[str, Any] | None = None,
        **overrides: Any,
    ) -> Task | None:
        """
        Create a task from a named template.

        Args:
            template_name: Name of the template to use.
            title: Title for the new task.
            variables: Variables to substitute.
            **overrides: Additional task field overrides.

        Returns:
            A new Task, or None if template not found.
        """
        template = self.get_template(template_name)
        if template is None:
            return None
        return template.create_task(title, variables, **overrides)

    def to_dict(self) -> dict[str, Any]:
        """Convert library to dictionary."""
        return {
            "templates": {
                name: template.to_dict()
                for name, template in self._templates.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskTemplateLibrary":
        """Create a library from dictionary."""
        library = cls()
        for name, template_data in data.get("templates", {}).items():
            template_data["name"] = name
            library.add_template(TaskTemplate.from_dict(template_data))
        return library


class TaskTemplates:
    """Pre-built task templates for common scenarios."""

    @staticmethod
    def feature_implementation() -> TaskTemplate:
        """Template for implementing a new feature."""
        return TaskTemplate(
            name="feature_implementation",
            description_template=(
                "Implement the ${feature_name} feature.\n\n"
                "Requirements:\n${requirements}\n\n"
                "Acceptance Criteria:\n${acceptance_criteria}"
            ),
            task_type=TaskType.FEATURE,
            priority=TaskPriority.HIGH,
            variables={
                "feature_name": "unnamed feature",
                "requirements": "No requirements specified",
                "acceptance_criteria": "Feature works as expected",
            },
            metadata_template={
                "component": "${component}",
                "epic": "${epic}",
            },
            tags=["development", "feature"],
        )

    @staticmethod
    def bug_fix() -> TaskTemplate:
        """Template for fixing a bug."""
        return TaskTemplate(
            name="bug_fix",
            description_template=(
                "Fix bug: ${bug_description}\n\n"
                "Steps to reproduce:\n${steps_to_reproduce}\n\n"
                "Expected behavior: ${expected_behavior}\n"
                "Actual behavior: ${actual_behavior}"
            ),
            task_type=TaskType.BUG_FIX,
            priority=TaskPriority.HIGH,
            variables={
                "bug_description": "Bug description not provided",
                "steps_to_reproduce": "1. Steps not provided",
                "expected_behavior": "Expected behavior not provided",
                "actual_behavior": "Actual behavior not provided",
            },
            tags=["bug", "fix"],
        )

    @staticmethod
    def code_review() -> TaskTemplate:
        """Template for code review tasks."""
        return TaskTemplate(
            name="code_review",
            description_template=(
                "Review code for: ${review_scope}\n\n"
                "Focus areas:\n${focus_areas}\n\n"
                "PR/Branch: ${branch_or_pr}"
            ),
            task_type=TaskType.CODE_REVIEW,
            priority=TaskPriority.MEDIUM,
            variables={
                "review_scope": "Code changes",
                "focus_areas": "- Code quality\n- Security\n- Performance",
                "branch_or_pr": "Not specified",
            },
            tags=["review", "quality"],
        )

    @staticmethod
    def security_audit() -> TaskTemplate:
        """Template for security audit tasks."""
        return TaskTemplate(
            name="security_audit",
            description_template=(
                "Perform security audit for: ${audit_scope}\n\n"
                "Audit checklist:\n"
                "- Authentication and authorization\n"
                "- Input validation\n"
                "- Data protection\n"
                "- Dependency vulnerabilities\n\n"
                "Additional focus: ${additional_focus}"
            ),
            task_type=TaskType.SECURITY_REVIEW,
            priority=TaskPriority.HIGH,
            variables={
                "audit_scope": "Application components",
                "additional_focus": "None specified",
            },
            tags=["security", "audit"],
        )

    @staticmethod
    def api_endpoint() -> TaskTemplate:
        """Template for implementing an API endpoint."""
        return TaskTemplate(
            name="api_endpoint",
            description_template=(
                "Implement API endpoint: ${method} ${endpoint}\n\n"
                "Description: ${endpoint_description}\n\n"
                "Request schema:\n${request_schema}\n\n"
                "Response schema:\n${response_schema}\n\n"
                "Authentication: ${auth_required}"
            ),
            task_type=TaskType.DEVELOPMENT,
            priority=TaskPriority.MEDIUM,
            variables={
                "method": "GET",
                "endpoint": "/api/resource",
                "endpoint_description": "API endpoint",
                "request_schema": "No schema provided",
                "response_schema": "No schema provided",
                "auth_required": "Yes",
            },
            metadata_template={
                "api_version": "${api_version}",
            },
            tags=["api", "development", "backend"],
        )

    @staticmethod
    def database_migration() -> TaskTemplate:
        """Template for database migration tasks."""
        return TaskTemplate(
            name="database_migration",
            description_template=(
                "Create database migration: ${migration_name}\n\n"
                "Changes:\n${migration_changes}\n\n"
                "Rollback strategy: ${rollback_strategy}\n\n"
                "Impact assessment: ${impact_assessment}"
            ),
            task_type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
            variables={
                "migration_name": "unnamed_migration",
                "migration_changes": "No changes specified",
                "rollback_strategy": "Standard rollback",
                "impact_assessment": "No assessment provided",
            },
            tags=["database", "migration", "data"],
        )

    @staticmethod
    def test_suite() -> TaskTemplate:
        """Template for creating test suites."""
        return TaskTemplate(
            name="test_suite",
            description_template=(
                "Create test suite for: ${test_subject}\n\n"
                "Test types: ${test_types}\n\n"
                "Coverage target: ${coverage_target}%\n\n"
                "Test scenarios:\n${test_scenarios}"
            ),
            task_type=TaskType.TESTING,
            priority=TaskPriority.MEDIUM,
            variables={
                "test_subject": "Component",
                "test_types": "Unit, Integration",
                "coverage_target": "80",
                "test_scenarios": "- Happy path\n- Edge cases\n- Error handling",
            },
            tags=["testing", "quality"],
        )

    @staticmethod
    def documentation() -> TaskTemplate:
        """Template for documentation tasks."""
        return TaskTemplate(
            name="documentation",
            description_template=(
                "Create/update documentation for: ${doc_subject}\n\n"
                "Documentation type: ${doc_type}\n\n"
                "Target audience: ${target_audience}\n\n"
                "Topics to cover:\n${topics}"
            ),
            task_type=TaskType.DOCUMENTATION,
            priority=TaskPriority.LOW,
            variables={
                "doc_subject": "Component",
                "doc_type": "Technical documentation",
                "target_audience": "Developers",
                "topics": "- Overview\n- API reference\n- Examples",
            },
            tags=["documentation"],
        )

    @classmethod
    def get_default_library(cls) -> TaskTemplateLibrary:
        """Get a library with all default templates."""
        library = TaskTemplateLibrary()
        library.add_template(cls.feature_implementation())
        library.add_template(cls.bug_fix())
        library.add_template(cls.code_review())
        library.add_template(cls.security_audit())
        library.add_template(cls.api_endpoint())
        library.add_template(cls.database_migration())
        library.add_template(cls.test_suite())
        library.add_template(cls.documentation())
        return library
