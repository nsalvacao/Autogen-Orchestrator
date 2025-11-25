"""Tests for the Orchestrator class."""

import pytest

from orchestrator.agents import DevAgent, DocsAgent, PMAgent, QAAgent, SecurityAgent
from orchestrator.contracts.agent_contract import AgentCapability
from orchestrator.core.conversation import ConversationMode
from orchestrator.core.orchestrator import Orchestrator, OrchestratorConfig
from orchestrator.core.task import Task, TaskType


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestratorConfig()

        assert config.name == "MetaOrchestrator"
        assert config.max_concurrent_tasks == 5
        assert config.enable_correction_loops is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = OrchestratorConfig(
            name="CustomOrchestrator",
            max_concurrent_tasks=10,
            enable_correction_loops=False,
        )

        assert config.name == "CustomOrchestrator"
        assert config.max_concurrent_tasks == 10
        assert config.enable_correction_loops is False


class TestOrchestrator:
    """Tests for the Orchestrator class."""

    @pytest.fixture
    def orchestrator(self):
        return Orchestrator()

    @pytest.fixture
    def orchestrator_with_agents(self):
        orch = Orchestrator()
        orch.register_agent(PMAgent())
        orch.register_agent(DevAgent())
        orch.register_agent(QAAgent())
        orch.register_agent(SecurityAgent())
        orch.register_agent(DocsAgent())
        return orch

    def test_orchestrator_creation(self, orchestrator):
        """Test orchestrator creation."""
        assert orchestrator is not None
        assert orchestrator.is_running is False
        assert len(orchestrator.agents) == 0

    def test_register_agent(self, orchestrator):
        """Test agent registration."""
        pm_agent = PMAgent()
        orchestrator.register_agent(pm_agent)

        assert "PMAgent" in orchestrator.agents
        assert orchestrator.agents["PMAgent"] == pm_agent

    def test_unregister_agent(self, orchestrator_with_agents):
        """Test agent unregistration."""
        orchestrator_with_agents.unregister_agent("PMAgent")

        assert "PMAgent" not in orchestrator_with_agents.agents

    def test_get_agents_by_capability(self, orchestrator_with_agents):
        """Test finding agents by capability."""
        coding_agents = orchestrator_with_agents.get_agents_by_capability(
            AgentCapability.CODING
        )

        assert len(coding_agents) >= 1
        assert any(a.name == "DevAgent" for a in coding_agents)

    def test_find_agents_for_task(self, orchestrator_with_agents):
        """Test finding agents for a task."""
        task = Task(
            title="Development Task",
            description="Build feature",
            task_type=TaskType.DEVELOPMENT,
        )

        agents = orchestrator_with_agents.find_agents_for_task(task)

        assert len(agents) >= 1
        assert any(a.name == "DevAgent" for a in agents)

    @pytest.mark.asyncio
    async def test_submit_task(self, orchestrator_with_agents):
        """Test task submission."""
        task = Task(
            title="Test Task",
            description="A test task",
        )

        task_id = await orchestrator_with_agents.submit_task(task)

        assert task_id == task.id

    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator_with_agents):
        """Test task processing."""
        task = Task(
            title="Development Task",
            description="Build feature",
            task_type=TaskType.DEVELOPMENT,
        )

        result = await orchestrator_with_agents.process_task(task)

        assert result.success is True
        assert task.assigned_agent is not None

    @pytest.mark.asyncio
    async def test_process_task_no_suitable_agent(self, orchestrator):
        """Test task processing when no agent can handle it."""
        task = Task(
            title="Task",
            description="Test",
            task_type=TaskType.DEVELOPMENT,
        )

        result = await orchestrator.process_task(task)

        assert result.success is False
        assert "No suitable agent" in result.error_message

    @pytest.mark.asyncio
    async def test_create_conversation(self, orchestrator_with_agents):
        """Test conversation creation."""
        conversation = await orchestrator_with_agents.create_conversation(
            topic="Feature Discussion",
            participant_names=["PMAgent", "DevAgent"],
            mode=ConversationMode.DYNAMIC,
        )

        assert conversation is not None
        assert conversation.topic == "Feature Discussion"
        assert "PMAgent" in conversation.participants
        assert "DevAgent" in conversation.participants

    @pytest.mark.asyncio
    async def test_start_and_shutdown(self, orchestrator_with_agents):
        """Test orchestrator start and shutdown."""
        await orchestrator_with_agents.start()
        assert orchestrator_with_agents.is_running is True

        await orchestrator_with_agents.shutdown()
        assert orchestrator_with_agents.is_running is False

    def test_get_status(self, orchestrator_with_agents):
        """Test getting orchestrator status."""
        status = orchestrator_with_agents.get_status()

        assert status["name"] == "MetaOrchestrator"
        assert status["agents_count"] == 5
        assert "PMAgent" in status["agents"]
        assert "DevAgent" in status["agents"]
