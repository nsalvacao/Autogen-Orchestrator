"""
Data Agent - Data modeling, database design, and data pipeline management agent.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class DataAgent(BaseAgent):
    """
    Data Agent.

    Responsible for:
    - Data modeling and schema design
    - Database design and optimization
    - Data pipeline architecture
    - Data analysis and insights
    - ETL/ELT process design
    - Data quality and validation
    """

    def __init__(self, name: str = "DataAgent"):
        """Initialize the Data Agent."""
        super().__init__(
            name=name,
            description=(
                "Data agent responsible for data modeling, database design, "
                "data pipeline management, and data analysis."
            ),
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.EVALUATION,
            ],
        )
        self._data_models: list[dict[str, Any]] = []
        self._pipeline_configs: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Data Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        content = message.content.lower()

        if "model" in content or "schema" in content:
            return self._generate_modeling_response(message.content)
        elif "database" in content or "sql" in content or "nosql" in content:
            return self._generate_database_response(message.content)
        elif "pipeline" in content or "etl" in content or "elt" in content:
            return self._generate_pipeline_response(message.content)
        elif "analysis" in content or "analytics" in content or "insight" in content:
            return self._generate_analysis_response(message.content)
        elif "quality" in content or "validation" in content:
            return self._generate_quality_response(message.content)
        else:
            return (
                f"Data Agent received: {message.content}. "
                "I can help with data modeling, database design, data pipelines, "
                "data analysis, and data quality."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Data Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        task_type = getattr(task, "task_type", None)
        task_type_value = "unknown"
        if task_type is not None and hasattr(task_type, "value"):
            task_type_value = task_type.value

        if task_type_value in ("planning", "feature"):
            return await self._handle_data_modeling_task(task)
        elif task_type_value == "development":
            return await self._handle_pipeline_task(task)
        else:
            return {
                "content": f"Data analysis completed for: {task.title}",
                "success": True,
                "needs_correction": False,
            }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Data Agent can handle the task type."""
        return task_type in ("planning", "development", "feature", "data", "database")

    async def _handle_data_modeling_task(self, task: Any) -> dict[str, Any]:
        """Handle a data modeling task."""
        data_model = self._create_data_model(task)
        self._data_models.append(data_model)

        return {
            "content": (
                f"Data model created for '{task.title}'.\n"
                f"Entities: {len(data_model['entities'])}\n"
                f"Relationships: {len(data_model['relationships'])}"
            ),
            "success": True,
            "artifacts": [data_model],
            "needs_correction": False,
        }

    async def _handle_pipeline_task(self, task: Any) -> dict[str, Any]:
        """Handle a data pipeline task."""
        pipeline_config = self._create_pipeline_config(task)
        self._pipeline_configs.append(pipeline_config)

        return {
            "content": (
                f"Data pipeline configured for '{task.title}'.\n"
                f"Stages: {len(pipeline_config['stages'])}\n"
                f"Data sources: {len(pipeline_config['sources'])}"
            ),
            "success": True,
            "artifacts": [pipeline_config],
            "needs_correction": False,
        }

    def _create_data_model(self, task: Any) -> dict[str, Any]:
        """Create a data model artifact for a task."""
        return {
            "type": "data_model",
            "task_id": task.id,
            "title": f"Data Model for {task.title}",
            "entities": [
                {
                    "name": "User",
                    "attributes": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "email", "type": "string", "unique": True},
                        {"name": "name", "type": "string"},
                        {"name": "created_at", "type": "timestamp"},
                    ],
                },
                {
                    "name": "Organization",
                    "attributes": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "name", "type": "string"},
                        {"name": "settings", "type": "jsonb"},
                    ],
                },
                {
                    "name": "Project",
                    "attributes": [
                        {"name": "id", "type": "uuid", "primary_key": True},
                        {"name": "name", "type": "string"},
                        {"name": "description", "type": "text"},
                        {"name": "status", "type": "enum"},
                    ],
                },
            ],
            "relationships": [
                {
                    "from": "User",
                    "to": "Organization",
                    "type": "many_to_many",
                    "through": "UserOrganization",
                },
                {
                    "from": "Project",
                    "to": "Organization",
                    "type": "many_to_one",
                },
            ],
            "indexes": [
                {"entity": "User", "columns": ["email"], "type": "unique"},
                {"entity": "Project", "columns": ["organization_id", "status"]},
            ],
        }

    def _create_pipeline_config(self, task: Any) -> dict[str, Any]:
        """Create a data pipeline configuration."""
        return {
            "type": "pipeline_config",
            "task_id": task.id,
            "name": f"Pipeline: {task.title}",
            "sources": [
                {"name": "primary_db", "type": "postgresql", "mode": "incremental"},
                {"name": "events", "type": "kafka", "mode": "streaming"},
                {"name": "external_api", "type": "rest_api", "mode": "batch"},
            ],
            "stages": [
                {
                    "name": "extract",
                    "operations": ["connect", "read", "validate_schema"],
                },
                {
                    "name": "transform",
                    "operations": ["clean", "normalize", "enrich", "aggregate"],
                },
                {
                    "name": "load",
                    "operations": ["validate", "write", "index"],
                },
            ],
            "destination": {
                "type": "data_warehouse",
                "engine": "snowflake",
                "schema": "analytics",
            },
            "schedule": {
                "frequency": "hourly",
                "retry_policy": {"max_retries": 3, "backoff": "exponential"},
            },
            "quality_checks": [
                {"type": "completeness", "threshold": 0.99},
                {"type": "uniqueness", "columns": ["id"]},
                {"type": "freshness", "max_delay_hours": 2},
            ],
        }

    def _generate_modeling_response(self, request: str) -> str:
        """Generate a data modeling response."""
        return (
            "Data Modeling Guidelines:\n\n"
            "1. **Entity Design**\n"
            "   - Clear entity identification\n"
            "   - Appropriate attribute types\n"
            "   - Primary and foreign keys\n\n"
            "2. **Normalization**\n"
            "   - Third Normal Form (3NF) for OLTP\n"
            "   - Denormalization for read-heavy workloads\n"
            "   - Star/Snowflake schema for analytics\n\n"
            "3. **Best Practices**\n"
            "   - Consistent naming conventions\n"
            "   - Audit columns (created_at, updated_at)\n"
            "   - Soft deletes for data retention\n\n"
            f"Analyzing request: {request[:100]}..."
        )

    def _generate_database_response(self, request: str) -> str:
        """Generate a database design response."""
        return (
            "Database Design Recommendations:\n\n"
            "**SQL Databases:**\n"
            "- PostgreSQL for complex queries and ACID\n"
            "- MySQL for read-heavy workloads\n"
            "- SQLite for embedded applications\n\n"
            "**NoSQL Databases:**\n"
            "- MongoDB for document storage\n"
            "- Redis for caching and sessions\n"
            "- Cassandra for high write throughput\n"
            "- Elasticsearch for full-text search\n\n"
            "**Considerations:**\n"
            "- Indexing strategies\n"
            "- Partitioning for large tables\n"
            "- Connection pooling\n"
            "- Replication and failover"
        )

    def _generate_pipeline_response(self, request: str) -> str:
        """Generate a data pipeline response."""
        return (
            "Data Pipeline Architecture:\n\n"
            "**ETL vs ELT:**\n"
            "- ETL: Transform before loading (traditional)\n"
            "- ELT: Load then transform (modern cloud)\n\n"
            "**Pipeline Components:**\n"
            "- Sources: Databases, APIs, files, streams\n"
            "- Processing: Spark, Flink, dbt\n"
            "- Storage: Data lake, warehouse\n"
            "- Orchestration: Airflow, Prefect, Dagster\n\n"
            "**Best Practices:**\n"
            "- Idempotent operations\n"
            "- Schema evolution handling\n"
            "- Data lineage tracking\n"
            "- Incremental processing"
        )

    def _generate_analysis_response(self, request: str) -> str:
        """Generate a data analysis response."""
        return (
            "Data Analysis Guidelines:\n\n"
            "**Analysis Types:**\n"
            "- Descriptive: What happened?\n"
            "- Diagnostic: Why did it happen?\n"
            "- Predictive: What will happen?\n"
            "- Prescriptive: What should we do?\n\n"
            "**Tools & Techniques:**\n"
            "- SQL for structured queries\n"
            "- Python (pandas, numpy) for analysis\n"
            "- Visualization (matplotlib, seaborn)\n"
            "- Statistical methods\n\n"
            "**Deliverables:**\n"
            "- Data insights report\n"
            "- Dashboards and visualizations\n"
            "- Recommendations"
        )

    def _generate_quality_response(self, request: str) -> str:
        """Generate a data quality response."""
        return (
            "Data Quality Framework:\n\n"
            "**Quality Dimensions:**\n"
            "- Accuracy: Data correctness\n"
            "- Completeness: No missing values\n"
            "- Consistency: Uniform across sources\n"
            "- Timeliness: Data freshness\n"
            "- Uniqueness: No duplicates\n\n"
            "**Validation Strategies:**\n"
            "- Schema validation\n"
            "- Business rule checks\n"
            "- Statistical anomaly detection\n"
            "- Cross-reference validation\n\n"
            "**Tools:**\n"
            "- Great Expectations\n"
            "- dbt tests\n"
            "- Custom validation scripts"
        )

    def get_data_models(self) -> list[dict[str, Any]]:
        """Get all data models created by this agent."""
        return self._data_models.copy()

    def get_pipeline_configs(self) -> list[dict[str, Any]]:
        """Get all pipeline configurations created by this agent."""
        return self._pipeline_configs.copy()
