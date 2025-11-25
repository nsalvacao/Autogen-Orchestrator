"""
DevOps Agent - CI/CD, deployment, and infrastructure management agent.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class DevOpsAgent(BaseAgent):
    """
    DevOps Agent.

    Responsible for:
    - CI/CD pipeline design and management
    - Infrastructure as Code (IaC)
    - Deployment automation
    - Environment management
    - Monitoring and alerting setup
    - Container orchestration
    """

    def __init__(self, name: str = "DevOpsAgent"):
        """Initialize the DevOps Agent."""
        super().__init__(
            name=name,
            description=(
                "DevOps agent responsible for CI/CD pipelines, infrastructure management, "
                "deployment automation, and operational excellence."
            ),
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.EVALUATION,
            ],
        )
        self._pipeline_configs: list[dict[str, Any]] = []
        self._infrastructure_state: dict[str, Any] = {}

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the DevOps Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        content = message.content.lower()

        if "pipeline" in content or "ci" in content or "cd" in content:
            return self._generate_pipeline_response(message.content)
        elif "deploy" in content or "release" in content:
            return self._generate_deployment_response(message.content)
        elif "infrastructure" in content or "iac" in content or "terraform" in content:
            return self._generate_infrastructure_response(message.content)
        elif "container" in content or "docker" in content or "kubernetes" in content:
            return self._generate_container_response(message.content)
        elif "monitor" in content or "alert" in content or "observability" in content:
            return self._generate_monitoring_response(message.content)
        else:
            return (
                f"DevOps Agent received: {message.content}. "
                "I can help with CI/CD pipelines, deployments, infrastructure, "
                "containers, and monitoring."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the DevOps Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        task_type = getattr(task, "task_type", None)
        task_type_value = "unknown"
        if task_type is not None and hasattr(task_type, "value"):
            task_type_value = task_type.value

        if task_type_value in ("development", "feature"):
            return await self._handle_pipeline_task(task)
        elif task_type_value == "planning":
            return await self._handle_infrastructure_task(task)
        else:
            return {
                "content": f"DevOps analysis completed for: {task.title}",
                "success": True,
                "needs_correction": False,
            }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if DevOps can handle the task type."""
        return task_type in ("planning", "development", "feature", "devops", "deployment")

    async def _handle_pipeline_task(self, task: Any) -> dict[str, Any]:
        """Handle a CI/CD pipeline task."""
        pipeline_config = self._create_pipeline_config(task)
        self._pipeline_configs.append(pipeline_config)

        return {
            "content": (
                f"CI/CD pipeline configured for '{task.title}'.\n"
                f"Stages: {len(pipeline_config['stages'])}\n"
                f"Triggers: {len(pipeline_config['triggers'])}"
            ),
            "success": True,
            "artifacts": [pipeline_config],
            "needs_correction": False,
        }

    async def _handle_infrastructure_task(self, task: Any) -> dict[str, Any]:
        """Handle an infrastructure task."""
        infra_config = self._create_infrastructure_config(task)

        return {
            "content": (
                f"Infrastructure configured for '{task.title}'.\n"
                f"Resources: {len(infra_config['resources'])}\n"
                f"Provider: {infra_config['provider']}"
            ),
            "success": True,
            "artifacts": [infra_config],
            "needs_correction": False,
        }

    def _create_pipeline_config(self, task: Any) -> dict[str, Any]:
        """Create a CI/CD pipeline configuration."""
        return {
            "type": "pipeline_config",
            "task_id": task.id,
            "name": f"Pipeline: {task.title}",
            "stages": [
                {
                    "name": "build",
                    "steps": ["checkout", "install_dependencies", "compile"],
                },
                {
                    "name": "test",
                    "steps": ["unit_tests", "integration_tests", "coverage"],
                },
                {
                    "name": "security",
                    "steps": ["sast", "dependency_check", "secrets_scan"],
                },
                {
                    "name": "deploy",
                    "steps": ["build_image", "push_registry", "deploy_staging"],
                },
            ],
            "triggers": [
                {"type": "push", "branches": ["main", "develop"]},
                {"type": "pull_request", "branches": ["main"]},
            ],
            "environment_variables": {
                "NODE_ENV": "production",
                "LOG_LEVEL": "info",
            },
        }

    def _create_infrastructure_config(self, task: Any) -> dict[str, Any]:
        """Create an infrastructure configuration."""
        return {
            "type": "infrastructure_config",
            "task_id": task.id,
            "provider": "aws",
            "resources": [
                {
                    "type": "compute",
                    "name": "app-server",
                    "config": {"instance_type": "t3.medium", "count": 2},
                },
                {
                    "type": "database",
                    "name": "primary-db",
                    "config": {"engine": "postgres", "size": "db.t3.small"},
                },
                {
                    "type": "cache",
                    "name": "redis-cache",
                    "config": {"engine": "redis", "size": "cache.t3.micro"},
                },
                {
                    "type": "load_balancer",
                    "name": "app-lb",
                    "config": {"type": "application", "scheme": "internet-facing"},
                },
            ],
            "networking": {
                "vpc_cidr": "10.0.0.0/16",
                "availability_zones": 2,
                "nat_gateways": True,
            },
        }

    def _generate_pipeline_response(self, request: str) -> str:
        """Generate a CI/CD pipeline response."""
        return (
            "CI/CD Pipeline Design:\n\n"
            "**Pipeline Stages:**\n"
            "1. Build: Compile and package\n"
            "2. Test: Unit, integration, e2e tests\n"
            "3. Security: SAST, dependency scanning\n"
            "4. Deploy: Staging -> Production\n\n"
            "**Best Practices:**\n"
            "- Fail fast on critical issues\n"
            "- Parallel execution where possible\n"
            "- Artifacts caching\n"
            "- Environment isolation\n\n"
            "**Tooling Options:**\n"
            "- GitHub Actions\n"
            "- GitLab CI\n"
            "- Jenkins\n"
            "- CircleCI"
        )

    def _generate_deployment_response(self, request: str) -> str:
        """Generate a deployment response."""
        return (
            "Deployment Strategy:\n\n"
            "**Deployment Patterns:**\n"
            "- Blue/Green: Zero-downtime switching\n"
            "- Canary: Gradual traffic shifting\n"
            "- Rolling: Incremental updates\n\n"
            "**Rollback Strategy:**\n"
            "- Automatic health checks\n"
            "- Quick rollback capability\n"
            "- Database migration handling\n\n"
            "**Environment Progression:**\n"
            "- Development -> Staging -> Production\n"
            "- Feature flags for controlled rollout\n"
            "- Smoke tests at each stage"
        )

    def _generate_infrastructure_response(self, request: str) -> str:
        """Generate an infrastructure response."""
        return (
            "Infrastructure as Code:\n\n"
            "**IaC Tools:**\n"
            "- Terraform for cloud resources\n"
            "- Pulumi for programmatic IaC\n"
            "- CloudFormation for AWS-native\n\n"
            "**Architecture Components:**\n"
            "- VPC with public/private subnets\n"
            "- Load balancers for traffic distribution\n"
            "- Auto-scaling groups\n"
            "- Managed databases\n\n"
            "**Security:**\n"
            "- Security groups and NACLs\n"
            "- IAM roles and policies\n"
            "- Encryption at rest and in transit"
        )

    def _generate_container_response(self, request: str) -> str:
        """Generate a container/Kubernetes response."""
        return (
            "Container Orchestration:\n\n"
            "**Docker:**\n"
            "- Multi-stage builds\n"
            "- Minimal base images\n"
            "- Security scanning\n\n"
            "**Kubernetes:**\n"
            "- Deployments and Services\n"
            "- ConfigMaps and Secrets\n"
            "- Ingress controllers\n"
            "- Horizontal Pod Autoscaler\n\n"
            "**Best Practices:**\n"
            "- Resource limits and requests\n"
            "- Liveness and readiness probes\n"
            "- Pod disruption budgets\n"
            "- Network policies"
        )

    def _generate_monitoring_response(self, request: str) -> str:
        """Generate a monitoring response."""
        return (
            "Monitoring & Observability:\n\n"
            "**Metrics:**\n"
            "- Prometheus for collection\n"
            "- Grafana for visualization\n"
            "- Custom application metrics\n\n"
            "**Logging:**\n"
            "- Centralized log aggregation\n"
            "- Structured logging (JSON)\n"
            "- Log retention policies\n\n"
            "**Tracing:**\n"
            "- OpenTelemetry integration\n"
            "- Distributed trace analysis\n"
            "- Performance bottleneck identification\n\n"
            "**Alerting:**\n"
            "- PagerDuty/OpsGenie integration\n"
            "- SLO-based alerting\n"
            "- Runbook automation"
        )

    def get_pipeline_configs(self) -> list[dict[str, Any]]:
        """Get all pipeline configurations."""
        return self._pipeline_configs.copy()
