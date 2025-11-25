"""Tests for the Task and TaskQueue classes."""

from orchestrator.core.task import (
    RetryConfig,
    RetryState,
    RetryStrategy,
    Task,
    TaskPriority,
    TaskQueue,
    TaskStatus,
    TaskTemplate,
    TaskTemplateLibrary,
    TaskTemplates,
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


class TestRetryConfig:
    """Tests for the RetryConfig class."""

    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.max_retries == 3
        assert config.base_delay_seconds == 1.0
        assert config.max_delay_seconds == 60.0

    def test_calculate_delay_immediate(self):
        """Test immediate strategy returns zero delay."""
        config = RetryConfig(strategy=RetryStrategy.IMMEDIATE)
        assert config.calculate_delay(1) == 0.0
        assert config.calculate_delay(5) == 0.0

    def test_calculate_delay_none(self):
        """Test none strategy returns zero delay."""
        config = RetryConfig(strategy=RetryStrategy.NONE)
        assert config.calculate_delay(1) == 0.0

    def test_calculate_delay_linear(self):
        """Test linear backoff calculation."""
        config = RetryConfig(strategy=RetryStrategy.LINEAR, base_delay_seconds=2.0)
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(3) == 6.0

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation."""
        config = RetryConfig(strategy=RetryStrategy.EXPONENTIAL, base_delay_seconds=1.0)
        assert config.calculate_delay(1) == 1.0
        assert config.calculate_delay(2) == 2.0
        assert config.calculate_delay(3) == 4.0
        assert config.calculate_delay(4) == 8.0

    def test_calculate_delay_respects_max(self):
        """Test that delay is capped at max_delay_seconds."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay_seconds=10.0,
            max_delay_seconds=30.0,
        )
        assert config.calculate_delay(5) == 30.0

    def test_should_retry_all_errors(self):
        """Test retry on all errors when no specific errors configured."""
        config = RetryConfig()
        assert config.should_retry("Connection error") is True
        assert config.should_retry("Timeout") is True
        assert config.should_retry(None) is True

    def test_should_retry_specific_errors(self):
        """Test retry only on specific errors."""
        config = RetryConfig(retry_on_errors=["timeout", "connection"])
        assert config.should_retry("Connection error occurred") is True
        assert config.should_retry("Request timeout") is True
        assert config.should_retry("Authentication failed") is False

    def test_should_retry_none_strategy(self):
        """Test no retry with NONE strategy."""
        config = RetryConfig(strategy=RetryStrategy.NONE)
        assert config.should_retry("Any error") is False


class TestRetryState:
    """Tests for the RetryState class."""

    def test_initial_state(self):
        """Test initial retry state."""
        state = RetryState()
        assert state.attempt == 0
        assert state.last_error is None
        assert state.errors == []

    def test_record_attempt(self):
        """Test recording an attempt."""
        state = RetryState()
        state.record_attempt("Error message")

        assert state.attempt == 1
        assert state.last_error == "Error message"
        assert state.last_attempt_at is not None
        assert len(state.errors) == 1

    def test_record_multiple_attempts(self):
        """Test recording multiple attempts."""
        state = RetryState()
        state.record_attempt("Error 1")
        state.record_attempt("Error 2")

        assert state.attempt == 2
        assert state.last_error == "Error 2"
        assert len(state.errors) == 2

    def test_can_retry(self):
        """Test checking if retry is allowed."""
        config = RetryConfig(max_retries=3)
        state = RetryState()

        assert state.can_retry(config) is True

        state.record_attempt("Error")
        state.record_attempt("Error")
        assert state.can_retry(config) is True

        state.record_attempt("Error")
        assert state.can_retry(config) is False

    def test_to_dict(self):
        """Test converting state to dictionary."""
        state = RetryState()
        state.record_attempt("Test error")

        state_dict = state.to_dict()
        assert state_dict["attempt"] == 1
        assert state_dict["last_error"] == "Test error"
        assert len(state_dict["errors"]) == 1


class TestTaskRetry:
    """Tests for task retry functionality."""

    def test_task_has_retry_config(self):
        """Test that tasks have retry configuration."""
        task = Task(title="Task", description="Test")
        assert task.retry_config is not None
        assert task.retry_state is not None

    def test_task_with_custom_retry_config(self):
        """Test task creation with custom retry config."""
        config = RetryConfig(max_retries=5, strategy=RetryStrategy.LINEAR)
        task = Task(title="Task", description="Test", retry_config=config)

        assert task.retry_config.max_retries == 5
        assert task.retry_config.strategy == RetryStrategy.LINEAR

    def test_can_retry(self):
        """Test task can_retry method."""
        task = Task(title="Task", description="Test")
        assert task.can_retry() is True

        # Exhaust retries
        for _ in range(3):
            task.retry_state.record_attempt("Error")

        assert task.can_retry() is False

    def test_record_failure_with_retry(self):
        """Test recording failure triggers retry."""
        task = Task(title="Task", description="Test")
        task.record_failure("Test error")

        assert task.status == TaskStatus.RETRYING
        assert task.retry_state.attempt == 1
        assert task.retry_state.next_retry_at is not None

    def test_record_failure_no_retry_after_max(self):
        """Test task fails permanently after max retries."""
        config = RetryConfig(max_retries=2)
        task = Task(title="Task", description="Test", retry_config=config)

        task.record_failure("Error 1")
        assert task.status == TaskStatus.RETRYING

        task.record_failure("Error 2")
        assert task.status == TaskStatus.FAILED
        assert task.result is not None
        assert task.result.success is False

    def test_reset_for_retry(self):
        """Test resetting task for retry."""
        task = Task(title="Task", description="Test")
        task.record_failure("Error")
        assert task.status == TaskStatus.RETRYING

        task.reset_for_retry()
        assert task.status == TaskStatus.PENDING
        assert task.retry_state.next_retry_at is None

    def test_task_to_dict_includes_retry_info(self):
        """Test that to_dict includes retry information."""
        task = Task(title="Task", description="Test")
        task.record_failure("Test error")

        task_dict = task.to_dict()
        assert "retry_config" in task_dict
        assert "retry_state" in task_dict
        assert task_dict["retry_config"]["strategy"] == "exponential"


class TestTaskQueueRetry:
    """Tests for TaskQueue retry functionality."""

    def test_mark_failed_triggers_retry(self):
        """Test that mark_failed triggers retry for retryable tasks."""
        queue = TaskQueue()
        task = Task(title="Task", description="Test")
        queue.add_task(task)

        will_retry = queue.mark_failed(task.id, "Test error")

        assert will_retry is True
        assert task.status == TaskStatus.RETRYING

    def test_mark_failed_permanent_after_max(self):
        """Test permanent failure after max retries."""
        queue = TaskQueue()
        config = RetryConfig(max_retries=1)
        task = Task(title="Task", description="Test", retry_config=config)
        queue.add_task(task)

        queue.mark_failed(task.id, "Error 1")
        will_retry = queue.mark_failed(task.id, "Error 2")

        assert will_retry is False
        assert task.status == TaskStatus.FAILED

    def test_mark_failed_unknown_task(self):
        """Test mark_failed with unknown task ID."""
        queue = TaskQueue()
        result = queue.mark_failed("unknown-id", "Error")
        assert result is False

    def test_get_tasks_ready_for_retry(self):
        """Test getting tasks ready for retry."""
        queue = TaskQueue()
        task = Task(
            title="Task",
            description="Test",
            retry_config=RetryConfig(base_delay_seconds=0.0),
        )
        queue.add_task(task)
        queue.mark_failed(task.id, "Error")

        # Task should be ready immediately with 0 delay
        ready = queue.get_tasks_ready_for_retry()
        assert len(ready) == 1
        assert ready[0].id == task.id

    def test_get_tasks_ready_for_retry_respects_delay(self):
        """Test that tasks with future retry time are not returned."""
        queue = TaskQueue()
        task = Task(
            title="Task",
            description="Test",
            retry_config=RetryConfig(base_delay_seconds=3600.0),  # 1 hour
        )
        queue.add_task(task)
        queue.mark_failed(task.id, "Error")

        ready = queue.get_tasks_ready_for_retry()
        assert len(ready) == 0

    def test_process_retries(self):
        """Test processing retries resets tasks to PENDING."""
        queue = TaskQueue()
        task = Task(
            title="Task",
            description="Test",
            retry_config=RetryConfig(base_delay_seconds=0.0),
        )
        queue.add_task(task)
        queue.mark_failed(task.id, "Error")

        retried_ids = queue.process_retries()

        assert task.id in retried_ids
        assert task.status == TaskStatus.PENDING

    def test_get_failed_tasks(self):
        """Test getting permanently failed tasks."""
        queue = TaskQueue()
        config = RetryConfig(max_retries=0)  # No retries
        task = Task(title="Task", description="Test", retry_config=config)
        queue.add_task(task)

        queue.mark_failed(task.id, "Error")

        failed = queue.get_failed_tasks()
        assert len(failed) == 1
        assert failed[0].id == task.id

    def test_get_retrying_tasks(self):
        """Test getting tasks waiting for retry."""
        queue = TaskQueue()
        task = Task(title="Task", description="Test")
        queue.add_task(task)

        queue.mark_failed(task.id, "Error")

        retrying = queue.get_retrying_tasks()
        assert len(retrying) == 1
        assert retrying[0].id == task.id


class TestTaskTemplate:
    """Tests for TaskTemplate class."""

    def test_template_creation(self):
        """Test creating a task template."""
        template = TaskTemplate(
            name="test_template",
            description_template="Test task for ${component}",
            task_type=TaskType.DEVELOPMENT,
            priority=TaskPriority.HIGH,
        )

        assert template.name == "test_template"
        assert template.task_type == TaskType.DEVELOPMENT
        assert template.priority == TaskPriority.HIGH

    def test_create_task_from_template(self):
        """Test creating a task from template."""
        template = TaskTemplate(
            name="test_template",
            description_template="Test task for ${component}",
            task_type=TaskType.DEVELOPMENT,
        )

        task = template.create_task(
            title="Test Task",
            variables={"component": "UserService"},
        )

        assert task.title == "Test Task"
        assert task.description == "Test task for UserService"
        assert task.task_type == TaskType.DEVELOPMENT
        assert "template_name" in task.metadata

    def test_variable_substitution(self):
        """Test variable substitution in templates."""
        template = TaskTemplate(
            name="test",
            description_template="${var1} and ${var2}",
            variables={"var1": "default1", "var2": "default2"},
        )

        task = template.create_task(
            title="Test",
            variables={"var1": "custom1"},
        )

        assert task.description == "custom1 and default2"

    def test_metadata_template(self):
        """Test metadata template substitution."""
        template = TaskTemplate(
            name="test",
            description_template="Test",
            metadata_template={"component": "${component}"},
        )

        task = template.create_task(
            title="Test",
            variables={"component": "MyComponent"},
        )

        assert task.metadata["component"] == "MyComponent"

    def test_create_task_with_overrides(self):
        """Test creating task with field overrides."""
        template = TaskTemplate(
            name="test",
            description_template="Test",
            priority=TaskPriority.LOW,
        )

        task = template.create_task(
            title="Test",
            priority=TaskPriority.CRITICAL,
        )

        assert task.priority == TaskPriority.CRITICAL

    def test_template_to_dict(self):
        """Test converting template to dictionary."""
        template = TaskTemplate(
            name="test",
            description_template="Test ${var}",
            tags=["tag1", "tag2"],
        )

        template_dict = template.to_dict()

        assert template_dict["name"] == "test"
        assert template_dict["description_template"] == "Test ${var}"
        assert template_dict["tags"] == ["tag1", "tag2"]

    def test_template_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            "name": "test",
            "description_template": "Test template",
            "task_type": "testing",
            "priority": "high",
            "tags": ["test"],
        }

        template = TaskTemplate.from_dict(data)

        assert template.name == "test"
        assert template.task_type == TaskType.TESTING
        assert template.priority == TaskPriority.HIGH

    def test_template_with_retry_config(self):
        """Test template with retry configuration."""
        config = RetryConfig(max_retries=5)
        template = TaskTemplate(
            name="test",
            description_template="Test",
            retry_config=config,
        )

        task = template.create_task(title="Test")

        assert task.retry_config.max_retries == 5


class TestTaskTemplateLibrary:
    """Tests for TaskTemplateLibrary class."""

    def test_add_and_get_template(self):
        """Test adding and retrieving templates."""
        library = TaskTemplateLibrary()
        template = TaskTemplate(name="test", description_template="Test")

        library.add_template(template)
        retrieved = library.get_template("test")

        assert retrieved is not None
        assert retrieved.name == "test"

    def test_remove_template(self):
        """Test removing a template."""
        library = TaskTemplateLibrary()
        template = TaskTemplate(name="test", description_template="Test")

        library.add_template(template)
        result = library.remove_template("test")

        assert result is True
        assert library.get_template("test") is None

    def test_remove_nonexistent_template(self):
        """Test removing a nonexistent template."""
        library = TaskTemplateLibrary()
        result = library.remove_template("nonexistent")
        assert result is False

    def test_list_templates(self):
        """Test listing template names."""
        library = TaskTemplateLibrary()
        library.add_template(TaskTemplate(name="a", description_template="A"))
        library.add_template(TaskTemplate(name="b", description_template="B"))

        names = library.list_templates()

        assert "a" in names
        assert "b" in names

    def test_get_templates_by_tag(self):
        """Test filtering templates by tag."""
        library = TaskTemplateLibrary()
        library.add_template(
            TaskTemplate(name="t1", description_template="T1", tags=["dev"])
        )
        library.add_template(
            TaskTemplate(name="t2", description_template="T2", tags=["test"])
        )
        library.add_template(
            TaskTemplate(name="t3", description_template="T3", tags=["dev", "test"])
        )

        dev_templates = library.get_templates_by_tag("dev")

        assert len(dev_templates) == 2

    def test_get_templates_by_type(self):
        """Test filtering templates by task type."""
        library = TaskTemplateLibrary()
        library.add_template(
            TaskTemplate(
                name="t1",
                description_template="T1",
                task_type=TaskType.DEVELOPMENT,
            )
        )
        library.add_template(
            TaskTemplate(
                name="t2",
                description_template="T2",
                task_type=TaskType.TESTING,
            )
        )

        dev_templates = library.get_templates_by_type(TaskType.DEVELOPMENT)

        assert len(dev_templates) == 1
        assert dev_templates[0].name == "t1"

    def test_create_task_from_template_name(self):
        """Test creating task from template name."""
        library = TaskTemplateLibrary()
        template = TaskTemplate(
            name="test",
            description_template="Test for ${item}",
        )
        library.add_template(template)

        task = library.create_task_from_template(
            "test",
            title="My Task",
            variables={"item": "component"},
        )

        assert task is not None
        assert task.description == "Test for component"

    def test_create_task_from_nonexistent_template(self):
        """Test creating task from nonexistent template."""
        library = TaskTemplateLibrary()
        task = library.create_task_from_template("nonexistent", title="Test")
        assert task is None

    def test_library_to_dict(self):
        """Test converting library to dictionary."""
        library = TaskTemplateLibrary()
        library.add_template(TaskTemplate(name="test", description_template="Test"))

        library_dict = library.to_dict()

        assert "templates" in library_dict
        assert "test" in library_dict["templates"]

    def test_library_from_dict(self):
        """Test creating library from dictionary."""
        data = {
            "templates": {
                "test": {
                    "name": "test",
                    "description_template": "Test template",
                }
            }
        }

        library = TaskTemplateLibrary.from_dict(data)
        template = library.get_template("test")

        assert template is not None
        assert template.description_template == "Test template"


class TestTaskTemplates:
    """Tests for pre-built TaskTemplates."""

    def test_feature_implementation_template(self):
        """Test feature implementation template."""
        template = TaskTemplates.feature_implementation()

        assert template.name == "feature_implementation"
        assert template.task_type == TaskType.FEATURE
        assert "development" in template.tags

        task = template.create_task(
            title="Add Login",
            variables={
                "feature_name": "User Login",
                "requirements": "OAuth2 support",
                "acceptance_criteria": "Users can log in",
            },
        )

        assert "User Login" in task.description
        assert "OAuth2 support" in task.description

    def test_bug_fix_template(self):
        """Test bug fix template."""
        template = TaskTemplates.bug_fix()

        assert template.name == "bug_fix"
        assert template.task_type == TaskType.BUG_FIX

        task = template.create_task(
            title="Fix Login Bug",
            variables={
                "bug_description": "Login fails on Safari",
                "steps_to_reproduce": "1. Open Safari\n2. Try to login",
                "expected_behavior": "User logs in",
                "actual_behavior": "Error displayed",
            },
        )

        assert "Safari" in task.description

    def test_code_review_template(self):
        """Test code review template."""
        template = TaskTemplates.code_review()

        assert template.name == "code_review"
        assert template.task_type == TaskType.CODE_REVIEW

    def test_security_audit_template(self):
        """Test security audit template."""
        template = TaskTemplates.security_audit()

        assert template.name == "security_audit"
        assert template.task_type == TaskType.SECURITY_REVIEW
        assert "security" in template.tags

    def test_api_endpoint_template(self):
        """Test API endpoint template."""
        template = TaskTemplates.api_endpoint()

        assert template.name == "api_endpoint"
        assert "api" in template.tags

        task = template.create_task(
            title="Create Users Endpoint",
            variables={
                "method": "POST",
                "endpoint": "/api/v1/users",
                "endpoint_description": "Create a new user",
            },
        )

        assert "POST" in task.description
        assert "/api/v1/users" in task.description

    def test_database_migration_template(self):
        """Test database migration template."""
        template = TaskTemplates.database_migration()

        assert template.name == "database_migration"
        assert "database" in template.tags

    def test_test_suite_template(self):
        """Test test suite template."""
        template = TaskTemplates.test_suite()

        assert template.name == "test_suite"
        assert template.task_type == TaskType.TESTING

    def test_documentation_template(self):
        """Test documentation template."""
        template = TaskTemplates.documentation()

        assert template.name == "documentation"
        assert template.task_type == TaskType.DOCUMENTATION

    def test_get_default_library(self):
        """Test getting default template library."""
        library = TaskTemplates.get_default_library()

        assert len(library.list_templates()) == 8
        assert library.get_template("feature_implementation") is not None
        assert library.get_template("bug_fix") is not None
        assert library.get_template("code_review") is not None
