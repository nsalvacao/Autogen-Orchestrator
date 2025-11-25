"""Tests for the Task and TaskQueue classes."""

from orchestrator.core.task import (
    Task,
    TaskPriority,
    TaskQueue,
    TaskStatus,
    TaskType,
)


class TestTask:
    """Tests for the Task class."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            title="Test Task",
            description="A test task description",
        )

        assert task.title == "Test Task"
        assert task.description == "A test task description"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM
        assert task.task_type == TaskType.DEVELOPMENT
        assert task.id is not None

    def test_task_with_custom_priority(self):
        """Test task creation with custom priority."""
        task = Task(
            title="Critical Task",
            description="A critical task",
            priority=TaskPriority.CRITICAL,
        )

        assert task.priority == TaskPriority.CRITICAL

    def test_task_can_start_no_dependencies(self):
        """Test task can start without dependencies."""
        task = Task(
            title="Independent Task",
            description="No dependencies",
        )

        assert task.can_start(set()) is True

    def test_task_can_start_with_dependencies(self):
        """Test task start based on dependencies."""
        task = Task(
            title="Dependent Task",
            description="Has dependencies",
            dependencies=["task-1", "task-2"],
        )

        assert task.can_start(set()) is False
        assert task.can_start({"task-1"}) is False
        assert task.can_start({"task-1", "task-2"}) is True

    def test_task_is_terminal(self):
        """Test terminal status detection."""
        task = Task(title="Task", description="Test")

        assert task.is_terminal() is False

        task.update_status(TaskStatus.COMPLETED)
        assert task.is_terminal() is True

        task.update_status(TaskStatus.FAILED)
        assert task.is_terminal() is True

        task.update_status(TaskStatus.CANCELLED)
        assert task.is_terminal() is True

    def test_task_update_status(self):
        """Test status updates and timestamps."""
        task = Task(title="Task", description="Test")
        original_updated = task.updated_at

        task.update_status(TaskStatus.IN_PROGRESS)

        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        assert task.updated_at >= original_updated

    def test_task_to_dict(self):
        """Test task serialization to dictionary."""
        task = Task(
            title="Test Task",
            description="A test task",
            task_type=TaskType.TESTING,
            priority=TaskPriority.HIGH,
        )

        task_dict = task.to_dict()

        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "A test task"
        assert task_dict["task_type"] == "testing"
        assert task_dict["priority"] == "high"
        assert task_dict["status"] == "pending"

    def test_task_needs_more_corrections(self):
        """Test correction count tracking."""
        task = Task(title="Task", description="Test", max_corrections=3)

        assert task.needs_more_corrections() is True

        task.correction_count = 2
        assert task.needs_more_corrections() is True

        task.correction_count = 3
        assert task.needs_more_corrections() is False


class TestTaskQueue:
    """Tests for the TaskQueue class."""

    def test_add_and_get_task(self):
        """Test adding and retrieving tasks."""
        queue = TaskQueue()
        task = Task(title="Task", description="Test")

        queue.add_task(task)
        retrieved = queue.get_task(task.id)

        assert retrieved is not None
        assert retrieved.id == task.id

    def test_get_next_task_no_tasks(self):
        """Test getting next task when queue is empty."""
        queue = TaskQueue()
        assert queue.get_next_task() is None

    def test_get_next_task_priority_order(self):
        """Test that higher priority tasks are returned first."""
        queue = TaskQueue()

        low_task = Task(
            title="Low Priority",
            description="Low",
            priority=TaskPriority.LOW,
        )
        high_task = Task(
            title="High Priority",
            description="High",
            priority=TaskPriority.HIGH,
        )
        critical_task = Task(
            title="Critical Priority",
            description="Critical",
            priority=TaskPriority.CRITICAL,
        )

        queue.add_task(low_task)
        queue.add_task(high_task)
        queue.add_task(critical_task)

        next_task = queue.get_next_task()
        assert next_task is not None
        assert next_task.priority == TaskPriority.CRITICAL

    def test_get_next_task_respects_dependencies(self):
        """Test that tasks with unmet dependencies are not returned."""
        queue = TaskQueue()

        task_a = Task(
            title="Task A",
            description="Independent",
            priority=TaskPriority.LOW,
        )
        task_b = Task(
            title="Task B",
            description="Depends on A",
            priority=TaskPriority.CRITICAL,
            dependencies=[task_a.id],
        )

        queue.add_task(task_a)
        queue.add_task(task_b)

        # Should get task_a first (task_b has unmet dependencies)
        next_task = queue.get_next_task()
        assert next_task is not None
        assert next_task.id == task_a.id

    def test_mark_completed(self):
        """Test marking tasks as completed."""
        queue = TaskQueue()
        task = Task(title="Task", description="Test")

        queue.add_task(task)
        queue.mark_completed(task.id)

        retrieved = queue.get_task(task.id)
        assert retrieved is not None
        assert retrieved.status == TaskStatus.COMPLETED

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        queue = TaskQueue()

        for i in range(3):
            queue.add_task(Task(title=f"Task {i}", description="Test"))

        all_tasks = queue.get_all_tasks()
        assert len(all_tasks) == 3

    def test_get_tasks_by_status(self):
        """Test filtering tasks by status."""
        queue = TaskQueue()

        task1 = Task(title="Task 1", description="Test")
        task2 = Task(title="Task 2", description="Test")
        task3 = Task(title="Task 3", description="Test")

        queue.add_task(task1)
        queue.add_task(task2)
        queue.add_task(task3)

        task1.update_status(TaskStatus.IN_PROGRESS)
        task2.update_status(TaskStatus.COMPLETED)

        pending = queue.get_tasks_by_status(TaskStatus.PENDING)
        assert len(pending) == 1

        in_progress = queue.get_tasks_by_status(TaskStatus.IN_PROGRESS)
        assert len(in_progress) == 1
