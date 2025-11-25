"""Tests for DataAgent."""

import pytest

from orchestrator.agents import DataAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage
from orchestrator.core.task import Task, TaskType


class TestDataAgent:
    """Tests for DataAgent."""

    @pytest.fixture
    def agent(self):
        return DataAgent()

    def test_agent_creation(self, agent):
        """Test agent creation."""
        assert agent.name == "DataAgent"
        assert AgentCapability.PLANNING in agent.capabilities
        assert AgentCapability.EVALUATION in agent.capabilities
        assert "data" in agent.description.lower()

    def test_can_handle_data_tasks(self, agent):
        """Test that Data agent can handle appropriate tasks."""
        assert agent.can_handle("data") is True
        assert agent.can_handle("database") is True
        assert agent.can_handle("planning") is True
        assert agent.can_handle("development") is True
        assert agent.can_handle("testing") is False

    @pytest.mark.asyncio
    async def test_process_modeling_message(self, agent):
        """Test processing data modeling messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="DataAgent",
            content="Design the data model for the user management system",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "model" in response.content.lower() or "entity" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_database_message(self, agent):
        """Test processing database messages."""
        message = AgentMessage(
            sender="DevAgent",
            recipient="DataAgent",
            content="What database should we use for this project?",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "database" in response.content.lower() or "sql" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_pipeline_message(self, agent):
        """Test processing ETL/pipeline messages."""
        message = AgentMessage(
            sender="DevOpsAgent",
            recipient="DataAgent",
            content="Design an ETL pipeline for our analytics",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "pipeline" in response.content.lower() or "etl" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_analysis_message(self, agent):
        """Test processing data analysis messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="DataAgent",
            content="We need data analysis for user engagement metrics",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "analysis" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_quality_message(self, agent):
        """Test processing data quality messages."""
        message = AgentMessage(
            sender="QAAgent",
            recipient="DataAgent",
            content="How do we ensure data quality and validation?",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "quality" in response.content.lower() or "validation" in response.content.lower()

    @pytest.mark.asyncio
    async def test_process_generic_message(self, agent):
        """Test processing generic messages."""
        message = AgentMessage(
            sender="PMAgent",
            recipient="DataAgent",
            content="Hello, can you help with our project?",
        )

        response = await agent.process_message(message)

        assert response.success is True
        assert "data agent" in response.content.lower()

    @pytest.mark.asyncio
    async def test_handle_data_modeling_task(self, agent):
        """Test handling a data modeling task."""
        task = Task(
            title="Design User Data Model",
            description="Create the data model for user management",
            task_type=TaskType.PLANNING,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
        assert response.artifacts[0]["type"] == "data_model"
        assert "entities" in response.artifacts[0]
        assert "relationships" in response.artifacts[0]

    @pytest.mark.asyncio
    async def test_handle_pipeline_task(self, agent):
        """Test handling a data pipeline task."""
        task = Task(
            title="Configure Data Pipeline",
            description="Set up ETL pipeline for analytics",
            task_type=TaskType.DEVELOPMENT,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0
        assert response.artifacts[0]["type"] == "pipeline_config"
        assert "stages" in response.artifacts[0]
        assert "sources" in response.artifacts[0]

    @pytest.mark.asyncio
    async def test_handle_feature_task(self, agent):
        """Test handling a feature task."""
        task = Task(
            title="Implement Analytics Feature",
            description="Add analytics data feature",
            task_type=TaskType.FEATURE,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert len(response.artifacts) > 0

    @pytest.mark.asyncio
    async def test_handle_generic_task(self, agent):
        """Test handling a generic task."""
        task = Task(
            title="Review Data Architecture",
            description="Review current data architecture",
            task_type=TaskType.CODE_REVIEW,
        )

        response = await agent.handle_task(task)

        assert response.success is True
        assert "data analysis" in response.content.lower()

    def test_get_data_models(self, agent):
        """Test getting data models."""
        models = agent.get_data_models()
        assert isinstance(models, list)

    def test_get_pipeline_configs(self, agent):
        """Test getting pipeline configurations."""
        configs = agent.get_pipeline_configs()
        assert isinstance(configs, list)

    @pytest.mark.asyncio
    async def test_data_models_accumulate(self, agent):
        """Test that data models accumulate across tasks."""
        task1 = Task(
            title="Design Model 1",
            description="First data model",
            task_type=TaskType.PLANNING,
        )
        task2 = Task(
            title="Design Model 2",
            description="Second data model",
            task_type=TaskType.PLANNING,
        )

        await agent.handle_task(task1)
        await agent.handle_task(task2)

        models = agent.get_data_models()
        assert len(models) == 2

    @pytest.mark.asyncio
    async def test_pipeline_configs_accumulate(self, agent):
        """Test that pipeline configs accumulate across tasks."""
        task1 = Task(
            title="Pipeline 1",
            description="First pipeline",
            task_type=TaskType.DEVELOPMENT,
        )
        task2 = Task(
            title="Pipeline 2",
            description="Second pipeline",
            task_type=TaskType.DEVELOPMENT,
        )

        await agent.handle_task(task1)
        await agent.handle_task(task2)

        configs = agent.get_pipeline_configs()
        assert len(configs) == 2

    @pytest.mark.asyncio
    async def test_initialize_and_shutdown(self, agent):
        """Test agent initialization and shutdown."""
        assert not agent.is_initialized

        await agent.initialize()
        assert agent.is_initialized

        await agent.shutdown()
        assert not agent.is_initialized

    def test_custom_name(self):
        """Test agent with custom name."""
        custom_agent = DataAgent(name="CustomDataAgent")
        assert custom_agent.name == "CustomDataAgent"
