"""
PM Agent - Project Manager agent for task planning and coordination.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class PMAgent(BaseAgent):
    """
    Project Manager Agent.

    Responsible for:
    - Task planning and decomposition
    - Priority assignment
    - Resource coordination
    - Progress tracking
    - Stakeholder communication
    """

    def __init__(self, name: str = "PMAgent", enable_autogen: bool = False):
        """Initialize the PM Agent."""
        system_message = (
            "You are a senior project manager with expertise in software development. "
            "You excel at task planning, decomposition, prioritization, and coordination. "
            "You understand dependencies, timelines, and how to allocate resources effectively."
        )
        super().__init__(
            name=name,
            description=(
                "Project Manager agent responsible for task planning, "
                "decomposition, priority assignment, and coordination between agents."
            ),
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.TASK_DECOMPOSITION,
                AgentCapability.EVALUATION,
            ],
            enable_autogen=enable_autogen,
            system_message=system_message,
        )
        self._managed_tasks: list[str] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the PM Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        # Try AutoGen first if enabled
        if self.is_autogen_enabled:
            return await self._generate_autogen_response(message.content)
        
        # Fallback to rule-based responses
        content = message.content.lower()

        if "plan" in content or "decompose" in content:
            return self._generate_planning_response(message.content)
        elif "status" in content or "progress" in content:
            return self._generate_status_response()
        elif "priority" in content:
            return self._generate_priority_response(message.content)
        else:
            return (
                f"PM Agent received: {message.content}. "
                "I can help with planning, status updates, and prioritization."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the PM Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        self._managed_tasks.append(task.id)

        # If AutoGen is enabled, use it for intelligent task decomposition
        if self.is_autogen_enabled:
            return await self._handle_task_with_autogen(task)
        
        # Fallback: Decompose the task into subtasks
        subtasks = self._decompose_task(task)

        return {
            "content": (
                f"Task '{task.title}' has been analyzed and "
                f"decomposed into {len(subtasks)} subtasks."
            ),
            "success": True,
            "artifacts": [{"type": "subtasks", "data": subtasks}],
            "metadata": {"original_task_id": task.id},
            "needs_correction": False,
        }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if PM can handle the task type."""
        return task_type in ("planning", "feature", "task_decomposition")

    def _generate_planning_response(self, request: str) -> str:
        """Generate a planning response."""
        return (
            "I'll create a plan for this request. The plan will include:\n"
            "1. Task breakdown and dependencies\n"
            "2. Priority assignments\n"
            "3. Agent assignments\n"
            "4. Timeline estimates\n"
            f"Request analyzed: {request[:100]}..."
        )

    def _generate_status_response(self) -> str:
        """Generate a status update response."""
        return (
            f"Project Status Update:\n"
            f"- Managed tasks: {len(self._managed_tasks)}\n"
            f"- Active conversations: In progress\n"
            f"- Overall status: On track"
        )

    def _generate_priority_response(self, request: str) -> str:
        """Generate a priority assessment response."""
        return (
            "Priority Assessment:\n"
            "Based on the request, I recommend:\n"
            "- Critical: Security-related items\n"
            "- High: Core functionality\n"
            "- Medium: Enhancements\n"
            "- Low: Documentation updates"
        )

    def _decompose_task(self, task: Any) -> list[dict[str, Any]]:
        """
        Decompose a task into subtasks.

        Placeholder implementation - in production, this would use
        intelligent decomposition based on task analysis.
        """
        return [
            {
                "title": f"Analysis for {task.title}",
                "type": "planning",
                "priority": "high",
            },
            {
                "title": f"Implementation for {task.title}",
                "type": "development",
                "priority": "high",
            },
            {
                "title": f"Testing for {task.title}",
                "type": "testing",
                "priority": "medium",
            },
            {
                "title": f"Documentation for {task.title}",
                "type": "documentation",
                "priority": "low",
            },
        ]
    
    async def _handle_task_with_autogen(self, task: Any) -> dict[str, Any]:
        """
        Handle a task using AutoGen LLM for intelligent planning.
        
        Args:
            task: The task to handle.
            
        Returns:
            Dictionary with task result.
        """
        task_prompt = (
            f"As a project manager, analyze and decompose the following task:\n\n"
            f"Task: {task.title}\n"
            f"Description: {task.description}\n"
            f"Type: {getattr(task, 'task_type', 'unknown')}\n"
            f"Priority: {getattr(task, 'priority', 'unknown')}\n\n"
            "Please provide:\n"
            "1. A detailed analysis of the task\n"
            "2. Breakdown into subtasks with priorities\n"
            "3. Suggested agent assignments\n"
            "4. Dependencies and timeline considerations"
        )
        
        response = await self._generate_autogen_response(task_prompt)
        
        return {
            "content": response,
            "success": True,
            "artifacts": [],
            "metadata": {"original_task_id": task.id},
            "needs_correction": False,
        }
