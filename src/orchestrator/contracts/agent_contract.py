"""
Agent Contract - Defines the interface for all agents in the orchestrator.

This module provides the abstract base class and protocols that all agents
must implement to participate in the orchestration system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AgentCapability(str, Enum):
    """Capabilities that an agent can have."""

    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    SECURITY_ANALYSIS = "security_analysis"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    TASK_DECOMPOSITION = "task_decomposition"
    EVALUATION = "evaluation"


@dataclass
class AgentMessage:
    """Message structure for agent communication."""

    sender: str
    recipient: str
    content: str
    message_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str | None = None


@dataclass
class AgentResponse:
    """Response structure from an agent."""

    agent_name: str
    content: str
    success: bool = True
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    needs_correction: bool = False
    correction_reason: str | None = None


class AgentContract(ABC):
    """
    Abstract base class defining the contract for all orchestrator agents.

    All agents in the system must implement this contract to ensure
    consistent behavior and interoperability.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the agent."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> list[AgentCapability]:
        """Return the list of capabilities this agent provides."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of the agent's purpose and responsibilities."""
        pass

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message and return a response.

        Args:
            message: The message to process.

        Returns:
            AgentResponse containing the result of processing.
        """
        pass

    @abstractmethod
    async def handle_task(self, task: Any) -> AgentResponse:
        """
        Handle an assigned task.

        Args:
            task: The task to handle.

        Returns:
            AgentResponse containing the result of the task.
        """
        pass

    @abstractmethod
    def can_handle(self, task_type: str) -> bool:
        """
        Check if this agent can handle a specific task type.

        Args:
            task_type: The type of task to check.

        Returns:
            True if the agent can handle the task, False otherwise.
        """
        pass

    async def initialize(self) -> None:
        """Initialize the agent. Override if needed."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the agent gracefully. Override if needed."""
        pass
