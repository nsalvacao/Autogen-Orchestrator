"""
Orchestrator - The main orchestration engine for multi-agent coordination.
"""

from dataclasses import dataclass, field
from typing import Any

from orchestrator.contracts.agent_contract import (
    AgentCapability,
    AgentContract,
    AgentMessage,
    AgentResponse,
)
from orchestrator.core.conversation import Conversation, ConversationManager, ConversationMode
from orchestrator.core.correction_loop import CorrectionLoopFactory
from orchestrator.core.task import Task, TaskQueue, TaskResult, TaskStatus, TaskType


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""

    name: str = "MetaOrchestrator"
    max_concurrent_tasks: int = 5
    max_conversation_turns: int = 50
    enable_correction_loops: bool = True
    correction_max_iterations: int = 3
    # Placeholder for LLM configuration - to be implemented with proper config management
    llm_config_placeholder: str = "NOT_CONFIGURED"
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """
    The main orchestration engine that coordinates multiple agents.

    The orchestrator is responsible for:
    - Managing agent registration and discovery
    - Task distribution based on agent capabilities
    - Dynamic conversation management
    - Evaluation and correction loops
    - Cross-agent communication
    """

    def __init__(self, config: OrchestratorConfig | None = None):
        """
        Initialize the orchestrator.

        Args:
            config: Optional configuration for the orchestrator.
        """
        self._config = config or OrchestratorConfig()
        self._agents: dict[str, AgentContract] = {}
        self._task_queue = TaskQueue()
        self._conversation_manager = ConversationManager()
        self._correction_loop = CorrectionLoopFactory.create_default_loop()
        self._capability_index: dict[AgentCapability, list[str]] = {}
        self._task_type_mapping: dict[TaskType, list[AgentCapability]] = {
            TaskType.PLANNING: [AgentCapability.PLANNING, AgentCapability.TASK_DECOMPOSITION],
            TaskType.DEVELOPMENT: [AgentCapability.CODING],
            TaskType.TESTING: [AgentCapability.TESTING],
            TaskType.SECURITY_REVIEW: [AgentCapability.SECURITY_ANALYSIS],
            TaskType.DOCUMENTATION: [AgentCapability.DOCUMENTATION],
            TaskType.CODE_REVIEW: [AgentCapability.CODE_REVIEW, AgentCapability.EVALUATION],
            TaskType.BUG_FIX: [AgentCapability.CODING, AgentCapability.TESTING],
            TaskType.FEATURE: [AgentCapability.PLANNING, AgentCapability.CODING],
        }
        self._is_running = False

    @property
    def config(self) -> OrchestratorConfig:
        """Return the orchestrator configuration."""
        return self._config

    @property
    def agents(self) -> dict[str, AgentContract]:
        """Return registered agents."""
        return self._agents.copy()

    @property
    def is_running(self) -> bool:
        """Check if the orchestrator is running."""
        return self._is_running

    def register_agent(self, agent: AgentContract) -> None:
        """
        Register an agent with the orchestrator.

        Args:
            agent: The agent to register.
        """
        self._agents[agent.name] = agent

        # Index agent capabilities
        for capability in agent.capabilities:
            if capability not in self._capability_index:
                self._capability_index[capability] = []
            if agent.name not in self._capability_index[capability]:
                self._capability_index[capability].append(agent.name)

    def unregister_agent(self, agent_name: str) -> None:
        """
        Unregister an agent from the orchestrator.

        Args:
            agent_name: The name of the agent to unregister.
        """
        if agent_name in self._agents:
            agent = self._agents[agent_name]

            # Remove from capability index
            for capability in agent.capabilities:
                if capability in self._capability_index:
                    if agent_name in self._capability_index[capability]:
                        self._capability_index[capability].remove(agent_name)

            del self._agents[agent_name]

    def get_agents_by_capability(self, capability: AgentCapability) -> list[AgentContract]:
        """
        Get all agents with a specific capability.

        Args:
            capability: The capability to search for.

        Returns:
            List of agents with the capability.
        """
        agent_names = self._capability_index.get(capability, [])
        return [self._agents[name] for name in agent_names if name in self._agents]

    def find_agents_for_task(self, task: Task) -> list[AgentContract]:
        """
        Find suitable agents for a task based on task type.

        Args:
            task: The task to find agents for.

        Returns:
            List of suitable agents.
        """
        required_capabilities = self._task_type_mapping.get(task.task_type, [])

        suitable_agents = []
        for capability in required_capabilities:
            agents = self.get_agents_by_capability(capability)
            for agent in agents:
                if agent not in suitable_agents and agent.can_handle(task.task_type.value):
                    suitable_agents.append(agent)

        return suitable_agents

    async def submit_task(self, task: Task) -> str:
        """
        Submit a task for processing.

        Args:
            task: The task to submit.

        Returns:
            The task ID.
        """
        self._task_queue.add_task(task)
        return task.id

    async def process_task(self, task: Task) -> TaskResult:
        """
        Process a single task.

        Args:
            task: The task to process.

        Returns:
            TaskResult containing the outcome.
        """
        # Find suitable agents
        agents = self.find_agents_for_task(task)

        if not agents:
            return TaskResult(
                success=False,
                error_message=f"No suitable agent found for task type: {task.task_type}",
            )

        # Assign to first suitable agent
        agent = agents[0]
        task.assigned_agent = agent.name
        task.update_status(TaskStatus.IN_PROGRESS)

        # Process the task
        response = await agent.handle_task(task)

        # Run correction loop if enabled and needed
        if self._config.enable_correction_loops and response.needs_correction:
            loop_result = await self._correction_loop.run(
                task=task,
                initial_output=response.content,
                context={"task": task.to_dict(), "agent": agent.name},
            )

            return TaskResult(
                success=loop_result.success,
                output=loop_result.final_output,
                metadata={
                    "correction_iterations": loop_result.total_iterations,
                    "correction_status": loop_result.status.value,
                },
            )

        return TaskResult(
            success=response.success,
            output=response.content,
            artifacts=response.artifacts,
        )

    async def run_task_loop(self) -> None:
        """
        Run the main task processing loop.

        Processes tasks from the queue until stopped.
        """
        self._is_running = True

        while self._is_running:
            task = self._task_queue.get_next_task()

            if task is None:
                # No tasks ready, could add a small delay in production
                break

            task.update_status(TaskStatus.QUEUED)
            result = await self.process_task(task)
            task.result = result

            if result.success:
                self._task_queue.mark_completed(task.id)
            else:
                task.update_status(TaskStatus.FAILED)

    def stop(self) -> None:
        """Stop the task processing loop."""
        self._is_running = False

    async def create_conversation(
        self,
        topic: str,
        participant_names: list[str],
        mode: ConversationMode = ConversationMode.DYNAMIC,
        task_id: str | None = None,
    ) -> Conversation:
        """
        Create a new conversation between agents.

        Args:
            topic: The conversation topic.
            participant_names: Names of agents to include.
            mode: The conversation mode.
            task_id: Optional associated task ID.

        Returns:
            The created conversation.
        """
        # Validate participants
        valid_participants = [
            name for name in participant_names if name in self._agents
        ]

        return self._conversation_manager.create_conversation(
            topic=topic,
            participants=valid_participants,
            mode=mode,
            task_id=task_id,
        )

    async def send_message(
        self,
        conversation_id: str,
        sender: str,
        recipient: str,
        content: str,
    ) -> AgentResponse | None:
        """
        Send a message in a conversation.

        Args:
            conversation_id: The conversation ID.
            sender: The sender agent name.
            recipient: The recipient agent name.
            content: The message content.

        Returns:
            AgentResponse from the recipient, or None if failed.
        """
        conversation = self._conversation_manager.get_conversation(conversation_id)
        if conversation is None or not conversation.is_active():
            return None

        if recipient not in self._agents:
            return None

        message = AgentMessage(
            sender=sender,
            recipient=recipient,
            content=content,
            metadata={"conversation_id": conversation_id},
        )

        recipient_agent = self._agents[recipient]
        response = await recipient_agent.process_message(message)

        return response

    async def broadcast_message(
        self,
        conversation_id: str,
        sender: str,
        content: str,
    ) -> list[AgentResponse]:
        """
        Broadcast a message to all participants in a conversation.

        Args:
            conversation_id: The conversation ID.
            sender: The sender agent name.
            content: The message content.

        Returns:
            List of responses from all participants.
        """
        conversation = self._conversation_manager.get_conversation(conversation_id)
        if conversation is None or not conversation.is_active():
            return []

        responses = []
        for participant in conversation.participants:
            if participant != sender and participant in self._agents:
                response = await self.send_message(
                    conversation_id, sender, participant, content
                )
                if response:
                    responses.append(response)

        return responses

    async def start(self) -> None:
        """Start the orchestrator and initialize all agents."""
        for agent in self._agents.values():
            await agent.initialize()
        self._is_running = True

    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all agents."""
        self._is_running = False
        for agent in self._agents.values():
            await agent.shutdown()

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            "name": self._config.name,
            "is_running": self._is_running,
            "agents_count": len(self._agents),
            "agents": list(self._agents.keys()),
            "pending_tasks": len(
                self._task_queue.get_tasks_by_status(TaskStatus.PENDING)
            ),
            "active_conversations": len(
                self._conversation_manager.get_active_conversations()
            ),
        }
