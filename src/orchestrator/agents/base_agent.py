"""
Base Agent - Abstract base implementation for all orchestrator agents.

This module provides a concrete base class that implements common
functionality shared by all agents.
"""

from abc import abstractmethod
from typing import Any

from orchestrator.contracts.agent_contract import (
    AgentCapability,
    AgentContract,
    AgentMessage,
    AgentResponse,
)


class BaseAgent(AgentContract):
    """
    Base implementation for orchestrator agents.

    Provides common functionality and structure for specialized agents.
    Subclasses should implement the abstract methods specific to their role.
    """

    def __init__(
        self,
        name: str,
        description: str,
        capabilities: list[AgentCapability],
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique name for the agent.
            description: Description of the agent's purpose.
            capabilities: List of capabilities this agent provides.
        """
        self._name = name
        self._description = description
        self._capabilities = capabilities
        # TODO: Add AutoGen AssistantAgent configuration when integrating with AutoGen
        self._initialized = False
        self._message_history: list[AgentMessage] = []

    @property
    def name(self) -> str:
        """Return the unique name of the agent."""
        return self._name

    @property
    def capabilities(self) -> list[AgentCapability]:
        """Return the list of capabilities this agent provides."""
        return self._capabilities

    @property
    def description(self) -> str:
        """Return a description of the agent's purpose and responsibilities."""
        return self._description

    @property
    def is_initialized(self) -> bool:
        """Check if the agent has been initialized."""
        return self._initialized

    async def initialize(self) -> None:
        """Initialize the agent."""
        # Placeholder for AutoGen agent initialization
        # In future, this will initialize the AutoGen AssistantAgent
        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the agent gracefully."""
        self._initialized = False

    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message and return a response.

        Args:
            message: The message to process.

        Returns:
            AgentResponse containing the result of processing.
        """
        self._message_history.append(message)

        # Delegate to subclass implementation
        response_content = await self._process_message_impl(message)

        return AgentResponse(
            agent_name=self.name,
            content=response_content,
            success=True,
            metadata={"message_id": message.correlation_id},
        )

    @abstractmethod
    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Implementation-specific message processing.

        Args:
            message: The message to process.

        Returns:
            The response content string.
        """
        pass

    async def handle_task(self, task: Any) -> AgentResponse:
        """
        Handle an assigned task.

        Args:
            task: The task to handle.

        Returns:
            AgentResponse containing the result of the task.
        """
        # Delegate to subclass implementation
        result = await self._handle_task_impl(task)

        return AgentResponse(
            agent_name=self.name,
            content=result.get("content", ""),
            success=result.get("success", True),
            artifacts=result.get("artifacts", []),
            metadata=result.get("metadata", {}),
            needs_correction=result.get("needs_correction", False),
            correction_reason=result.get("correction_reason"),
        )

    @abstractmethod
    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Implementation-specific task handling.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result information.
        """
        pass

    def can_handle(self, task_type: str) -> bool:
        """
        Check if this agent can handle a specific task type.

        Args:
            task_type: The type of task to check.

        Returns:
            True if the agent can handle the task, False otherwise.
        """
        return self._can_handle_impl(task_type)

    @abstractmethod
    def _can_handle_impl(self, task_type: str) -> bool:
        """
        Implementation-specific task type checking.

        Args:
            task_type: The type of task to check.

        Returns:
            True if the agent can handle the task.
        """
        pass

    def get_message_history(self) -> list[AgentMessage]:
        """Get the agent's message history."""
        return self._message_history.copy()
