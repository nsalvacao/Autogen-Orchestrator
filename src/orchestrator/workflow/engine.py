"""
Workflow Engine - Executes workflows by coordinating agents and steps.

The workflow engine processes workflow definitions, managing step execution,
dependencies, and error handling.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from orchestrator.contracts.agent_contract import AgentContract
from orchestrator.core.task import Task, TaskType
from orchestrator.workflow.definition import (
    Workflow,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
)


@dataclass
class WorkflowExecutionResult:
    """Result of a workflow execution."""

    workflow_id: str
    success: bool
    status: WorkflowStatus
    outputs: dict[str, Any] = field(default_factory=dict)
    step_results: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    execution_time_ms: float = 0.0


class WorkflowEngine:
    """
    Engine for executing workflows.

    The workflow engine processes workflow definitions, executing steps
    in the correct order based on dependencies, and coordinating
    multiple agents.
    """

    def __init__(
        self,
        agents: dict[str, AgentContract] | None = None,
        max_parallel_steps: int = 5,
    ):
        """
        Initialize the workflow engine.

        Args:
            agents: Dictionary of available agents.
            max_parallel_steps: Maximum number of steps to run in parallel.
        """
        self._agents = agents or {}
        self._max_parallel_steps = max_parallel_steps
        self._running_workflows: dict[str, Workflow] = {}
        self._workflow_results: dict[str, WorkflowExecutionResult] = {}

    def register_agent(self, agent: AgentContract) -> None:
        """Register an agent with the engine."""
        self._agents[agent.name] = agent

    def register_agents(self, agents: dict[str, AgentContract]) -> None:
        """Register multiple agents with the engine."""
        self._agents.update(agents)

    async def execute(
        self,
        workflow: Workflow,
        inputs: dict[str, Any] | None = None,
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow.

        Args:
            workflow: The workflow to execute.
            inputs: Input variables for the workflow.

        Returns:
            WorkflowExecutionResult containing the execution outcome.
        """
        start_time = datetime.now()
        workflow.started_at = start_time
        workflow.status = WorkflowStatus.RUNNING
        self._running_workflows[workflow.id] = workflow

        # Initialize workflow variables with inputs
        if inputs:
            workflow.variables.update(inputs)

        completed_steps: set[str] = set()
        step_results: dict[str, Any] = {}
        outputs: dict[str, Any] = {}

        try:
            while True:
                # Get steps that are ready to execute
                ready_steps = workflow.get_ready_steps(completed_steps)

                if not ready_steps:
                    # Check if all steps are done
                    pending = [
                        s for s in workflow.steps
                        if s.status == WorkflowStatus.PENDING
                    ]
                    if not pending:
                        break
                    else:
                        # Steps waiting on failed dependencies
                        failed_deps = [
                            s for s in workflow.steps
                            if s.status == WorkflowStatus.FAILED
                        ]
                        if failed_deps:
                            raise Exception(
                                f"Workflow blocked: steps failed: "
                                f"{[s.name for s in failed_deps]}"
                            )
                        break

                # Execute ready steps (with parallelism limit)
                tasks = []
                for step in ready_steps[: self._max_parallel_steps]:
                    tasks.append(self._execute_step(step, workflow))

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for i, result in enumerate(results):
                    step = ready_steps[i]
                    if isinstance(result, Exception):
                        step.status = WorkflowStatus.FAILED
                        step.error = str(result)
                        step_results[step.id] = {"error": str(result)}
                    else:
                        step.status = WorkflowStatus.COMPLETED
                        step.result = result
                        step_results[step.id] = result
                        completed_steps.add(step.id)

                        # Collect outputs from completed steps
                        if result and isinstance(result, dict):
                            outputs[step.name] = result

            # Check final status
            failed_steps = [
                s for s in workflow.steps if s.status == WorkflowStatus.FAILED
            ]

            if failed_steps:
                workflow.status = WorkflowStatus.FAILED
                success = False
                error_msg = f"Steps failed: {[s.name for s in failed_steps]}"
            else:
                workflow.status = WorkflowStatus.COMPLETED
                success = True
                error_msg = None

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            success = False
            error_msg = str(e)

        end_time = datetime.now()
        workflow.completed_at = end_time
        execution_time = (end_time - start_time).total_seconds() * 1000

        result = WorkflowExecutionResult(
            workflow_id=workflow.id,
            success=success,
            status=workflow.status,
            outputs=outputs,
            step_results=step_results,
            error_message=error_msg,
            started_at=start_time,
            completed_at=end_time,
            execution_time_ms=execution_time,
        )

        self._workflow_results[workflow.id] = result
        del self._running_workflows[workflow.id]

        return result

    async def _execute_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """
        Execute a single workflow step.

        Args:
            step: The step to execute.
            workflow: The parent workflow.

        Returns:
            Step execution result.
        """
        step.status = WorkflowStatus.RUNNING
        step.started_at = datetime.now()

        try:
            if step.step_type == WorkflowStepType.TASK:
                result = await self._execute_task_step(step, workflow)
            elif step.step_type == WorkflowStepType.AGENT_ACTION:
                result = await self._execute_agent_action_step(step, workflow)
            elif step.step_type == WorkflowStepType.CONVERSATION:
                result = await self._execute_conversation_step(step, workflow)
            elif step.step_type == WorkflowStepType.CONDITION:
                result = await self._execute_condition_step(step, workflow)
            elif step.step_type == WorkflowStepType.PARALLEL:
                result = await self._execute_parallel_step(step, workflow)
            elif step.step_type == WorkflowStepType.WAIT:
                result = await self._execute_wait_step(step, workflow)
            else:
                result = {"status": "completed", "step_type": step.step_type.value}

            step.completed_at = datetime.now()
            return result

        except Exception as e:
            step.error = str(e)
            raise

    async def _execute_task_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a task step."""
        config = step.config
        agent_name = config.get("agent")
        task_type = config.get("task_type", "development")
        description = config.get("description", step.name)

        if agent_name and agent_name in self._agents:
            agent = self._agents[agent_name]

            # Create a task for the agent
            task = Task(
                title=step.name,
                description=description,
                task_type=TaskType(task_type),
            )

            response = await agent.handle_task(task)

            return {
                "success": response.success,
                "content": response.content,
                "agent": agent_name,
                "artifacts": response.artifacts,
            }
        else:
            return {
                "success": True,
                "content": f"Task step '{step.name}' completed (no agent assigned)",
                "agent": None,
            }

    async def _execute_agent_action_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a direct agent action step."""
        config = step.config
        agent_name = config.get("agent")
        action = config.get("action", "process")

        if agent_name and agent_name in self._agents:
            # Agent is available, direct processing would go here
            return {
                "success": True,
                "agent": agent_name,
                "action": action,
            }
        else:
            return {
                "success": False,
                "error": f"Agent '{agent_name}' not found",
            }

    async def _execute_conversation_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a conversation step."""
        config = step.config
        participants = config.get("participants", [])
        topic = config.get("topic", "Discussion")

        # Placeholder for conversation execution
        # In full implementation, this would use ConversationManager
        return {
            "success": True,
            "topic": topic,
            "participants": participants,
            "turns": 0,  # Would be populated by actual conversation
        }

    async def _execute_condition_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a conditional step."""
        condition = step.condition
        # Placeholder for condition evaluation
        # In full implementation, this would evaluate the condition expression
        result = True  # Default to true

        return {
            "success": True,
            "condition": condition,
            "result": result,
        }

    async def _execute_parallel_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a parallel step (multiple sub-steps in parallel)."""
        config = step.config
        sub_steps = config.get("steps", [])

        # Placeholder for parallel execution
        return {
            "success": True,
            "sub_steps_count": len(sub_steps),
        }

    async def _execute_wait_step(
        self,
        step: WorkflowStep,
        workflow: Workflow,
    ) -> dict[str, Any]:
        """Execute a wait step."""
        config = step.config
        wait_seconds = config.get("seconds", 0)

        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        return {
            "success": True,
            "waited_seconds": wait_seconds,
        }

    def get_workflow_status(self, workflow_id: str) -> WorkflowStatus | None:
        """Get the status of a workflow."""
        if workflow_id in self._running_workflows:
            return self._running_workflows[workflow_id].status
        if workflow_id in self._workflow_results:
            return self._workflow_results[workflow_id].status
        return None

    def get_workflow_result(self, workflow_id: str) -> WorkflowExecutionResult | None:
        """Get the result of a completed workflow."""
        return self._workflow_results.get(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        if workflow_id in self._running_workflows:
            workflow = self._running_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            return True
        return False

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow."""
        if workflow_id in self._running_workflows:
            workflow = self._running_workflows[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            return True
        return False

    def get_running_workflows(self) -> list[str]:
        """Get IDs of currently running workflows."""
        return list(self._running_workflows.keys())
