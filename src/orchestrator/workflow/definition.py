"""
Workflow Definition - Defines the structure of workflows.

Workflows are sequences of steps that coordinate multiple agents
to accomplish complex tasks.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepType(str, Enum):
    """Types of workflow steps."""

    TASK = "task"  # Execute a task
    AGENT_ACTION = "agent_action"  # Direct agent action
    CONVERSATION = "conversation"  # Multi-agent conversation
    CONDITION = "condition"  # Conditional branching
    PARALLEL = "parallel"  # Parallel execution
    LOOP = "loop"  # Iteration
    WAIT = "wait"  # Wait for external event
    APPROVAL = "approval"  # Human approval gate


@dataclass
class WorkflowStep:
    """
    A single step in a workflow.

    Steps can be tasks, agent actions, conditions, or control flow elements.
    """

    name: str
    step_type: WorkflowStepType
    config: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: list[str] = field(default_factory=list)  # Step IDs this depends on
    timeout_seconds: int | None = None
    retry_count: int = 0
    max_retries: int = 3
    on_failure: str | None = None  # Step ID to jump to on failure
    condition: str | None = None  # Condition expression for conditional steps
    metadata: dict[str, Any] = field(default_factory=dict)

    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: Any = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert step to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "step_type": self.step_type.value,
            "config": self.config,
            "dependencies": self.dependencies,
            "timeout_seconds": self.timeout_seconds,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


@dataclass
class Workflow:
    """
    A workflow definition containing a sequence of steps.

    Workflows define complex multi-step processes that coordinate
    multiple agents to accomplish a goal.
    """

    name: str
    description: str = ""
    steps: list[WorkflowStep] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    variables: dict[str, Any] = field(default_factory=dict)  # Workflow-level variables
    input_schema: dict[str, Any] = field(default_factory=dict)  # Expected input schema
    output_schema: dict[str, Any] = field(default_factory=dict)  # Expected output schema
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: WorkflowStep) -> None:
        """Add a step to the workflow."""
        self.steps.append(step)

    def get_step(self, step_id: str) -> WorkflowStep | None:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_step_by_name(self, name: str) -> WorkflowStep | None:
        """Get a step by name."""
        for step in self.steps:
            if step.name == name:
                return step
        return None

    def get_ready_steps(self, completed_steps: set[str]) -> list[WorkflowStep]:
        """
        Get steps that are ready to execute.

        A step is ready if all its dependencies have been completed.

        Args:
            completed_steps: Set of completed step IDs.

        Returns:
            List of steps ready for execution.
        """
        ready = []
        for step in self.steps:
            if step.status != WorkflowStatus.PENDING:
                continue
            if all(dep in completed_steps for dep in step.dependencies):
                ready.append(step)
        return ready

    def to_dict(self) -> dict[str, Any]:
        """Convert workflow to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "status": self.status.value,
            "steps": [step.to_dict() for step in self.steps],
            "variables": self.variables,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Workflow":
        """Create a workflow from dictionary."""
        steps = []
        for step_data in data.get("steps", []):
            step = WorkflowStep(
                id=step_data.get("id", str(uuid.uuid4())),
                name=step_data["name"],
                step_type=WorkflowStepType(step_data["step_type"]),
                config=step_data.get("config", {}),
                dependencies=step_data.get("dependencies", []),
                timeout_seconds=step_data.get("timeout_seconds"),
                metadata=step_data.get("metadata", {}),
            )
            steps.append(step)

        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            steps=steps,
            variables=data.get("variables", {}),
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            metadata=data.get("metadata", {}),
        )


class WorkflowTemplates:
    """Pre-built workflow templates for common scenarios."""

    @staticmethod
    def feature_development() -> Workflow:
        """Create a feature development workflow template."""
        workflow = Workflow(
            name="Feature Development",
            description="Standard workflow for developing a new feature",
        )

        # Planning step
        planning = WorkflowStep(
            name="planning",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "planning",
                "agent": "PMAgent",
                "description": "Plan and decompose the feature into tasks",
            },
        )
        workflow.add_step(planning)

        # Architecture step
        architecture = WorkflowStep(
            name="architecture",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "planning",
                "agent": "ArchitectAgent",
                "description": "Design the architecture for the feature",
            },
            dependencies=[planning.id],
        )
        workflow.add_step(architecture)

        # Development step
        development = WorkflowStep(
            name="development",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "development",
                "agent": "DevAgent",
                "description": "Implement the feature",
            },
            dependencies=[architecture.id],
        )
        workflow.add_step(development)

        # Parallel testing and security review
        testing = WorkflowStep(
            name="testing",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "testing",
                "agent": "QAAgent",
                "description": "Test the implementation",
            },
            dependencies=[development.id],
        )
        workflow.add_step(testing)

        security = WorkflowStep(
            name="security_review",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "security_review",
                "agent": "SecurityAgent",
                "description": "Security review of the implementation",
            },
            dependencies=[development.id],
        )
        workflow.add_step(security)

        # Documentation
        documentation = WorkflowStep(
            name="documentation",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "documentation",
                "agent": "DocsAgent",
                "description": "Document the feature",
            },
            dependencies=[testing.id, security.id],
        )
        workflow.add_step(documentation)

        return workflow

    @staticmethod
    def bug_fix() -> Workflow:
        """Create a bug fix workflow template."""
        workflow = Workflow(
            name="Bug Fix",
            description="Standard workflow for fixing a bug",
        )

        # Research step
        research = WorkflowStep(
            name="research",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "planning",
                "agent": "ResearchAgent",
                "description": "Research the bug and identify root cause",
            },
        )
        workflow.add_step(research)

        # Fix step
        fix = WorkflowStep(
            name="fix",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "bug_fix",
                "agent": "DevAgent",
                "description": "Implement the fix",
            },
            dependencies=[research.id],
        )
        workflow.add_step(fix)

        # Test step
        test = WorkflowStep(
            name="test",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "testing",
                "agent": "QAAgent",
                "description": "Test the fix",
            },
            dependencies=[fix.id],
        )
        workflow.add_step(test)

        return workflow

    @staticmethod
    def code_review() -> Workflow:
        """Create a code review workflow template."""
        workflow = Workflow(
            name="Code Review",
            description="Standard workflow for code review",
        )

        # Multi-agent conversation for review
        review_conversation = WorkflowStep(
            name="review_discussion",
            step_type=WorkflowStepType.CONVERSATION,
            config={
                "participants": ["DevAgent", "QAAgent", "SecurityAgent"],
                "topic": "Code Review Discussion",
                "mode": "dynamic",
            },
        )
        workflow.add_step(review_conversation)

        # Security check
        security = WorkflowStep(
            name="security_check",
            step_type=WorkflowStepType.TASK,
            config={
                "task_type": "security_review",
                "agent": "SecurityAgent",
                "description": "Security analysis of the code",
            },
            dependencies=[review_conversation.id],
        )
        workflow.add_step(security)

        return workflow
