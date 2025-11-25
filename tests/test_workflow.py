"""Tests for workflow module."""

import pytest

from orchestrator.agents import DevAgent, PMAgent, QAAgent
from orchestrator.workflow.definition import (
    Workflow,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
    WorkflowTemplates,
)
from orchestrator.workflow.engine import WorkflowEngine


class TestWorkflowStep:
    """Tests for WorkflowStep."""

    def test_step_creation(self):
        """Test creating a workflow step."""
        step = WorkflowStep(
            name="test_step",
            step_type=WorkflowStepType.TASK,
            config={"agent": "DevAgent"},
        )

        assert step.name == "test_step"
        assert step.step_type == WorkflowStepType.TASK
        assert step.status == WorkflowStatus.PENDING
        assert step.id is not None

    def test_step_to_dict(self):
        """Test step serialization."""
        step = WorkflowStep(
            name="test_step",
            step_type=WorkflowStepType.TASK,
        )

        data = step.to_dict()

        assert data["name"] == "test_step"
        assert data["step_type"] == "task"
        assert data["status"] == "pending"


class TestWorkflow:
    """Tests for Workflow."""

    def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = Workflow(
            name="Test Workflow",
            description="A test workflow",
        )

        assert workflow.name == "Test Workflow"
        assert workflow.status == WorkflowStatus.PENDING
        assert len(workflow.steps) == 0

    def test_add_step(self):
        """Test adding steps to workflow."""
        workflow = Workflow(name="Test")
        step = WorkflowStep(name="step1", step_type=WorkflowStepType.TASK)

        workflow.add_step(step)

        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "step1"

    def test_get_step(self):
        """Test getting a step by ID."""
        workflow = Workflow(name="Test")
        step = WorkflowStep(name="step1", step_type=WorkflowStepType.TASK)
        workflow.add_step(step)

        found = workflow.get_step(step.id)

        assert found is not None
        assert found.name == "step1"

    def test_get_step_by_name(self):
        """Test getting a step by name."""
        workflow = Workflow(name="Test")
        step = WorkflowStep(name="step1", step_type=WorkflowStepType.TASK)
        workflow.add_step(step)

        found = workflow.get_step_by_name("step1")

        assert found is not None
        assert found.id == step.id

    def test_get_ready_steps(self):
        """Test getting ready steps based on dependencies."""
        workflow = Workflow(name="Test")

        step1 = WorkflowStep(name="step1", step_type=WorkflowStepType.TASK)
        step2 = WorkflowStep(
            name="step2",
            step_type=WorkflowStepType.TASK,
            dependencies=[step1.id],
        )

        workflow.add_step(step1)
        workflow.add_step(step2)

        # No steps completed - only step1 should be ready
        ready = workflow.get_ready_steps(set())
        assert len(ready) == 1
        assert ready[0].name == "step1"

        # Mark step1 as completed and check again
        step1.status = WorkflowStatus.COMPLETED
        ready = workflow.get_ready_steps({step1.id})
        assert len(ready) == 1
        assert ready[0].name == "step2"

    def test_workflow_to_dict(self):
        """Test workflow serialization."""
        workflow = Workflow(name="Test", description="Test desc")
        workflow.add_step(WorkflowStep(name="step1", step_type=WorkflowStepType.TASK))

        data = workflow.to_dict()

        assert data["name"] == "Test"
        assert data["description"] == "Test desc"
        assert len(data["steps"]) == 1

    def test_workflow_from_dict(self):
        """Test workflow deserialization."""
        data = {
            "name": "Test",
            "description": "Test desc",
            "steps": [
                {"name": "step1", "step_type": "task"},
            ],
        }

        workflow = Workflow.from_dict(data)

        assert workflow.name == "Test"
        assert len(workflow.steps) == 1
        assert workflow.steps[0].name == "step1"


class TestWorkflowTemplates:
    """Tests for workflow templates."""

    def test_feature_development_template(self):
        """Test feature development workflow template."""
        workflow = WorkflowTemplates.feature_development()

        assert workflow.name == "Feature Development"
        assert len(workflow.steps) > 0

        # Check that steps are properly ordered with dependencies
        step_names = [s.name for s in workflow.steps]
        assert "planning" in step_names
        assert "development" in step_names
        assert "testing" in step_names

    def test_bug_fix_template(self):
        """Test bug fix workflow template."""
        workflow = WorkflowTemplates.bug_fix()

        assert workflow.name == "Bug Fix"
        assert len(workflow.steps) > 0

        step_names = [s.name for s in workflow.steps]
        assert "research" in step_names
        assert "fix" in step_names
        assert "test" in step_names

    def test_code_review_template(self):
        """Test code review workflow template."""
        workflow = WorkflowTemplates.code_review()

        assert workflow.name == "Code Review"
        assert len(workflow.steps) > 0


class TestWorkflowEngine:
    """Tests for WorkflowEngine."""

    @pytest.fixture
    def engine(self):
        return WorkflowEngine()

    @pytest.fixture
    def engine_with_agents(self):
        engine = WorkflowEngine()
        engine.register_agent(PMAgent())
        engine.register_agent(DevAgent())
        engine.register_agent(QAAgent())
        return engine

    def test_engine_creation(self, engine):
        """Test engine creation."""
        assert engine is not None
        assert len(engine.get_running_workflows()) == 0

    def test_register_agent(self, engine):
        """Test registering agents."""
        agent = PMAgent()
        engine.register_agent(agent)

        # Agent should be registered
        assert "PMAgent" in engine._agents

    @pytest.mark.asyncio
    async def test_execute_simple_workflow(self, engine_with_agents):
        """Test executing a simple workflow."""
        workflow = Workflow(name="Simple Test")
        step = WorkflowStep(
            name="test_task",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "development",
                "agent": "DevAgent",
                "description": "Test task",
            },
        )
        workflow.add_step(step)

        result = await engine_with_agents.execute(workflow)

        assert result.success is True
        assert result.status == WorkflowStatus.COMPLETED
        assert step.id in result.step_results  # step_results uses step.id as key

    @pytest.mark.asyncio
    async def test_execute_workflow_with_dependencies(self, engine_with_agents):
        """Test executing workflow with step dependencies."""
        workflow = Workflow(name="Dependent Steps")

        step1 = WorkflowStep(
            name="first",
            step_type=WorkflowStepType.TASK,
            config={"task_type": "planning", "agent": "PMAgent"},
        )
        step2 = WorkflowStep(
            name="second",
            step_type=WorkflowStepType.TASK,
            config={"task_type": "development", "agent": "DevAgent"},
            dependencies=[step1.id],
        )

        workflow.add_step(step1)
        workflow.add_step(step2)

        result = await engine_with_agents.execute(workflow)

        assert result.success is True
        assert "first" in result.outputs
        assert "second" in result.outputs

    @pytest.mark.asyncio
    async def test_execute_wait_step(self, engine):
        """Test executing a wait step."""
        workflow = Workflow(name="Wait Test")
        step = WorkflowStep(
            name="wait",
            step_type=WorkflowStepType.WAIT,
            config={"seconds": 0.1},  # Short wait for testing
        )
        workflow.add_step(step)

        result = await engine.execute(workflow)

        assert result.success is True
        assert result.step_results[step.id]["waited_seconds"] == 0.1

    def test_get_workflow_result(self, engine):
        """Test getting workflow result."""
        result = engine.get_workflow_result("nonexistent")
        assert result is None

    def test_get_workflow_status(self, engine):
        """Test getting workflow status."""
        status = engine.get_workflow_status("nonexistent")
        assert status is None
