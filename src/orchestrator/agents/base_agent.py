"""
Base Agent - Abstract base implementation for all orchestrator agents.

This module provides a concrete base class that implements common
functionality shared by all agents.
"""

import os
from abc import abstractmethod
from typing import Any

from orchestrator.contracts.agent_contract import (
    AgentCapability,
    AgentContract,
    AgentMessage,
    AgentResponse,
)

# AutoGen imports (optional - gracefully handle if not available)
try:
    from autogen import AssistantAgent, config_list_from_json
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    AssistantAgent = None


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
        enable_autogen: bool = False,
        system_message: str | None = None,
    ):
        """
        Initialize the base agent.

        Args:
            name: Unique name for the agent.
            description: Description of the agent's purpose.
            capabilities: List of capabilities this agent provides.
            enable_autogen: Whether to enable AutoGen LLM integration.
            system_message: Optional system message for the AutoGen agent.
        """
        self._name = name
        self._description = description
        self._capabilities = capabilities
        self._enable_autogen = enable_autogen and AUTOGEN_AVAILABLE
        self._autogen_agent: Any = None
        self._system_message = system_message or self._get_default_system_message()
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
        if self._enable_autogen and AUTOGEN_AVAILABLE:
            # Initialize AutoGen AssistantAgent
            llm_config = self._get_llm_config()
            if llm_config:
                self._autogen_agent = AssistantAgent(
                    name=self._name,
                    system_message=self._system_message,
                    llm_config=llm_config,
                )
        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown the agent gracefully."""
        self._autogen_agent = None
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

    def _get_llm_config(self) -> dict[str, Any] | None:
        """
        Get LLM configuration for AutoGen.
        
        Returns:
            LLM config dictionary or None if not configured.
        """
        api_key = os.environ.get("ORCHESTRATOR_LLM_API_KEY")
        if not api_key:
            return None
        
        model = os.environ.get("ORCHESTRATOR_LLM_MODEL", "gpt-4")
        max_tokens = int(os.environ.get("ORCHESTRATOR_LLM_MAX_TOKENS", "4096"))
        temperature = float(os.environ.get("ORCHESTRATOR_LLM_TEMPERATURE", "0.7"))
        
        return {
            "config_list": [
                {
                    "model": model,
                    "api_key": api_key,
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
    
    def _get_default_system_message(self) -> str:
        """
        Get the default system message for the agent.
        
        Returns:
            Default system message string.
        """
        return (
            f"You are {self._name}, an AI assistant specialized in {self._description}. "
            f"Your capabilities include: {', '.join(cap.value for cap in self._capabilities)}. "
            "Provide helpful, accurate, and professional responses."
        )
    
    @property
    def is_autogen_enabled(self) -> bool:
        """Check if AutoGen integration is enabled."""
        return self._enable_autogen and self._autogen_agent is not None
    
    async def _generate_autogen_response(self, prompt: str) -> str:
        """
        Generate a response using AutoGen LLM.
        
        Args:
            prompt: The prompt to send to the LLM.
            
        Returns:
            The generated response string.
        """
        if not self.is_autogen_enabled:
            return "AutoGen is not enabled or configured."
        
        try:
            # Use AutoGen's generate_reply method
            # Note: This is a simplified implementation
            # In production, you'd want more sophisticated conversation handling
            response = self._autogen_agent.generate_reply(
                messages=[{"role": "user", "content": prompt}]
            )
            
            if isinstance(response, str):
                return response
            elif isinstance(response, dict) and "content" in response:
                return response["content"]
            else:
                return str(response)
        except Exception as e:
            return f"Error generating AutoGen response: {str(e)}"
