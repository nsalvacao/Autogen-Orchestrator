"""Tests for the agent implementations."""

import pytest

from orchestrator.agents import (
    DevAgent,
    DocsAgent,
    PMAgent,
    QAAgent,
    SecurityAgent,
)
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage
from orchestrator.core.task import Task, TaskType


class TestPMAgent:
    """Tests for the PM Agent."""

    @pytest.fixture
    def agent(self):
        return PMAgent()

    def test_agent_properties(self, agent):
        """Test PM agent properties."""
        assert agent.name == "PMAgent"
        assert AgentCapability.PLANNING in agent.capabilities
        assert AgentCapability.TASK_DECOMPOSITION in agent.capabilities

    def test_can_handle_planning(self, agent):
        """Test PM can handle planning tasks."""
        assert agent.can_handle("planning") is True
        assert agent.can_handle("feature") is True
        assert agent.can_handle("testing") is False

    @pytest.mark.asyncio
    async def test_process_message_planning(self, agent):
        """Test processing a planning message."""
        message = AgentMessage(
            sender="user",
            recipient="PMAgent",
            content="Please plan the new feature implementation",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.agent_name == "PMAgent"
        assert "plan" in response.content.lower()

    @pytest.mark.asyncio
    async def test_handle_task(self, agent):
        """Test handling a planning task."""
        task = Task(
            title="New Feature",
            description="Implement new feature",
            task_type=TaskType.PLANNING,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0


class TestDevAgent:
    """Tests for the Dev Agent."""

    @pytest.fixture
    def agent(self):
        return DevAgent()

    def test_agent_properties(self, agent):
        """Test Dev agent properties."""
        assert agent.name == "DevAgent"
        assert AgentCapability.CODING in agent.capabilities
        assert AgentCapability.CODE_REVIEW in agent.capabilities

    def test_can_handle_development(self, agent):
        """Test Dev can handle development tasks."""
        assert agent.can_handle("development") is True
        assert agent.can_handle("bug_fix") is True
        assert agent.can_handle("documentation") is False

    @pytest.mark.asyncio
    async def test_process_message_implementation(self, agent):
        """Test processing an implementation message."""
        message = AgentMessage(
            sender="user",
            recipient="DevAgent",
            content="Please implement the user authentication module",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.agent_name == "DevAgent"

    @pytest.mark.asyncio
    async def test_handle_development_task(self, agent):
        """Test handling a development task."""
        task = Task(
            title="Auth Module",
            description="Implement authentication",
            task_type=TaskType.DEVELOPMENT,
        )

        response = await agent.handle_task(task)

        assert response.success is True


class TestQAAgent:
    """Tests for the QA Agent."""

    @pytest.fixture
    def agent(self):
        return QAAgent()

    def test_agent_properties(self, agent):
        """Test QA agent properties."""
        assert agent.name == "QAAgent"
        assert AgentCapability.TESTING in agent.capabilities
        assert AgentCapability.EVALUATION in agent.capabilities

    def test_can_handle_testing(self, agent):
        """Test QA can handle testing tasks."""
        assert agent.can_handle("testing") is True
        assert agent.can_handle("development") is False

    @pytest.mark.asyncio
    async def test_process_message_testing(self, agent):
        """Test processing a testing message."""
        message = AgentMessage(
            sender="user",
            recipient="QAAgent",
            content="Please test the new feature",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.agent_name == "QAAgent"

    @pytest.mark.asyncio
    async def test_handle_testing_task(self, agent):
        """Test handling a testing task."""
        task = Task(
            title="Feature Tests",
            description="Test new feature",
            task_type=TaskType.TESTING,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0


class TestSecurityAgent:
    """Tests for the Security Agent."""

    @pytest.fixture
    def agent(self):
        return SecurityAgent()

    def test_agent_properties(self, agent):
        """Test Security agent properties."""
        assert agent.name == "SecurityAgent"
        assert AgentCapability.SECURITY_ANALYSIS in agent.capabilities

    def test_can_handle_security(self, agent):
        """Test Security can handle security tasks."""
        assert agent.can_handle("security_review") is True
        assert agent.can_handle("development") is False

    @pytest.mark.asyncio
    async def test_process_message_security(self, agent):
        """Test processing a security message."""
        message = AgentMessage(
            sender="user",
            recipient="SecurityAgent",
            content="Please scan for vulnerabilities",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.agent_name == "SecurityAgent"

    @pytest.mark.asyncio
    async def test_handle_security_task(self, agent):
        """Test handling a security review task."""
        task = Task(
            title="Security Review",
            description="Review code security",
            task_type=TaskType.SECURITY_REVIEW,
        )

        response = await agent.handle_task(task)

        assert response.success is True


class TestDocsAgent:
    """Tests for the Docs Agent."""

    @pytest.fixture
    def agent(self):
        return DocsAgent()

    def test_agent_properties(self, agent):
        """Test Docs agent properties."""
        assert agent.name == "DocsAgent"
        assert AgentCapability.DOCUMENTATION in agent.capabilities

    def test_can_handle_documentation(self, agent):
        """Test Docs can handle documentation tasks."""
        assert agent.can_handle("documentation") is True
        assert agent.can_handle("development") is False

    @pytest.mark.asyncio
    async def test_process_message_docs(self, agent):
        """Test processing a documentation message."""
        message = AgentMessage(
            sender="user",
            recipient="DocsAgent",
            content="Please create API documentation",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert response.agent_name == "DocsAgent"

    @pytest.mark.asyncio
    async def test_handle_documentation_task(self, agent):
        """Test handling a documentation task."""
        task = Task(
            title="API Docs",
            description="Create API documentation",
            task_type=TaskType.DOCUMENTATION,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
