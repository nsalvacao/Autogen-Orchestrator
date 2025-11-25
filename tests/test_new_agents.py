"""Tests for new agents: ArchitectAgent, ResearchAgent, DevOpsAgent."""

import pytest

from orchestrator.agents import ArchitectAgent, DevOpsAgent, ResearchAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage
from orchestrator.core.task import Task, TaskType


class TestArchitectAgent:
    """Tests for ArchitectAgent."""

    @pytest.fixture
    def agent(self):
        return ArchitectAgent()

    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent.name == "ArchitectAgent"
        assert AgentCapability.PLANNING in agent.capabilities
        assert "architecture" in agent.description.lower()

    def test_can_handle_planning_task(self, agent):
        """Test that architect can handle planning tasks."""
        assert agent.can_handle("planning") is True
        assert agent.can_handle("architecture") is True
        assert agent.can_handle("design") is True
        assert agent.can_handle("testing") is False

    @pytest.mark.asyncio
    async def test_process_design_message(self, agent):
        """Test processing design-related messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="ArchitectAgent",
            content="Please design the system architecture for the new feature",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "architecture" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_tech_stack_message(self, agent):
        """Test processing technology stack messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="ArchitectAgent",
            content="What technology stack do you recommend?",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "technology" in response.content.lower() or "stack" in response.content.lower()

    @pytest.mark.asyncio
    async def test_handle_architecture_task(self, agent):
        """Test handling an architecture task."""
        task = Task(
            title="Design User Service",
            description="Design the architecture for user management",
            task_type=TaskType.PLANNING,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
        assert response.artifacts[0]["type"] == "architecture_design"

    def test_get_design_artifacts(self, agent):
        """Test getting design artifacts."""
        artifacts = agent.get_design_artifacts()
        assert isinstance(artifacts, list)


class TestResearchAgent:
    """Tests for ResearchAgent."""

    @pytest.fixture
    def agent(self):
        return ResearchAgent()

    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent.name == "ResearchAgent"
        assert AgentCapability.EVALUATION in agent.capabilities
        assert "research" in agent.description.lower()

    def test_can_handle_research_tasks(self, agent):
        """Test that research agent can handle appropriate tasks."""
        assert agent.can_handle("research") is True
        assert agent.can_handle("analysis") is True
        assert agent.can_handle("planning") is True
        assert agent.can_handle("development") is False

    @pytest.mark.asyncio
    async def test_process_research_message(self, agent):
        """Test processing research messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="ResearchAgent",
            content="Please research best practices for API design",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "research" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_comparison_message(self, agent):
        """Test processing comparison messages."""
        message = AgentMessage(
            sender="DevAgent",
            recipient="ResearchAgent",
            content="Compare Django vs FastAPI for this project",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "comparison" in response.content.lower() or "criteria" in response.content.lower()

    @pytest.mark.asyncio
    async def test_handle_research_task(self, agent):
        """Test handling a research task."""
        task = Task(
            title="Research Authentication Methods",
            description="Research modern authentication methods",
            task_type=TaskType.PLANNING,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
        assert response.artifacts[0]["type"] == "research_report"

    def test_get_knowledge_base(self, agent):
        """Test getting knowledge base."""
        kb = agent.get_knowledge_base()
        assert isinstance(kb, list)

    @pytest.mark.asyncio
    async def test_search_knowledge(self, agent):
        """Test searching knowledge after research."""
        task = Task(
            title="Research Testing",
            description="Research testing best practices",
            task_type=TaskType.PLANNING,
        )
        await agent.handle_task(task)

        results = agent.search_knowledge("testing")
        assert isinstance(results, list)


class TestDevOpsAgent:
    """Tests for DevOpsAgent."""

    @pytest.fixture
    def agent(self):
        return DevOpsAgent()

    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent.name == "DevOpsAgent"
        assert AgentCapability.PLANNING in agent.capabilities
        assert "devops" in agent.description.lower() or "ci/cd" in agent.description.lower()

    def test_can_handle_devops_tasks(self, agent):
        """Test that DevOps agent can handle appropriate tasks."""
        assert agent.can_handle("devops") is True
        assert agent.can_handle("deployment") is True
        assert agent.can_handle("planning") is True
        assert agent.can_handle("testing") is False

    @pytest.mark.asyncio
    async def test_process_pipeline_message(self, agent):
        """Test processing CI/CD pipeline messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="DevOpsAgent",
            content="Set up a CI/CD pipeline for the project",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "pipeline" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_deployment_message(self, agent):
        """Test processing deployment messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="DevOpsAgent",
            content="How should we deploy this to production?",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "deploy" in response.content.lower()

    @pytest.mark.asyncio
    async def test_handle_pipeline_task(self, agent):
        """Test handling a pipeline configuration task."""
        task = Task(
            title="Configure CI Pipeline",
            description="Set up continuous integration",
            task_type=TaskType.DEVELOPMENT,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
        assert response.artifacts[0]["type"] == "pipeline_config"

    def test_get_pipeline_configs(self, agent):
        """Test getting pipeline configurations."""
        configs = agent.get_pipeline_configs()
        assert isinstance(configs, list)
