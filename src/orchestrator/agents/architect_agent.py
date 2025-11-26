"""
Architect Agent - System design and architecture agent.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class ArchitectAgent(BaseAgent):
    """
    Architect Agent.

    Responsible for:
    - System design and architecture decisions
    - Technical specifications and documentation
    - Technology stack recommendations
    - Design pattern suggestions
    - Component interaction design
    - Scalability and performance planning
    """

    def __init__(self, name: str = "ArchitectAgent", enable_autogen: bool = False):
        """Initialize the Architect Agent."""
        system_message = (
            "You are a senior software architect with expertise in system design, architecture patterns, "
            "and technical decision-making. You excel at designing scalable, maintainable systems."
        )
        super().__init__(
            name=name,
            description=(
                "Architect agent responsible for system design, architecture decisions, "
                "technical specifications, and technology stack recommendations."
            ),
            capabilities=[
                AgentCapability.PLANNING,
                AgentCapability.EVALUATION,
            ],
            enable_autogen=enable_autogen,
            system_message=system_message,
        )
        self._design_artifacts: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Architect Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        if self.is_autogen_enabled:
            return await self._generate_autogen_response(message.content)
        
        content = message.content.lower()

        if "design" in content or "architecture" in content:
            return self._generate_design_response(message.content)
        elif "technology" in content or "stack" in content or "tech" in content:
            return self._generate_tech_stack_response(message.content)
        elif "scale" in content or "performance" in content:
            return self._generate_scalability_response(message.content)
        elif "pattern" in content:
            return self._generate_pattern_response(message.content)
        elif "component" in content or "module" in content:
            return self._generate_component_response(message.content)
        else:
            return (
                f"Architect Agent received: {message.content}. "
                "I can help with system design, architecture, technology stack, "
                "scalability planning, and design patterns."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Architect Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        if self.is_autogen_enabled:
            return await self._handle_task_with_autogen(task)
        
        task_type = getattr(task, "task_type", None)
        task_type_value = "unknown"
        if task_type is not None and hasattr(task_type, "value"):
            task_type_value = task_type.value

        if task_type_value in ("planning", "feature"):
            return await self._handle_architecture_task(task)
        else:
            return {
                "content": f"Analyzed architecture for: {task.title}",
                "success": True,
                "needs_correction": False,
            }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Architect can handle the task type."""
        return task_type in ("planning", "feature", "architecture", "design")

    async def _handle_architecture_task(self, task: Any) -> dict[str, Any]:
        """Handle an architecture task."""
        design_artifact = self._create_design_artifact(task)
        self._design_artifacts.append(design_artifact)

        return {
            "content": (
                f"Architecture design completed for '{task.title}'.\n"
                f"Components: {len(design_artifact['components'])}\n"
                f"Patterns: {', '.join(design_artifact['patterns'])}"
            ),
            "success": True,
            "artifacts": [design_artifact],
            "needs_correction": False,
        }

    def _create_design_artifact(self, task: Any) -> dict[str, Any]:
        """Create a design artifact for a task."""
        return {
            "type": "architecture_design",
            "task_id": task.id,
            "title": f"Architecture for {task.title}",
            "components": [
                {"name": "API Layer", "type": "interface", "responsibility": "HTTP endpoints"},
                {"name": "Service Layer", "type": "business_logic", "responsibility": "Core logic"},
                {"name": "Data Layer", "type": "persistence", "responsibility": "Data access"},
            ],
            "patterns": ["Repository", "Service", "Factory"],
            "technology_recommendations": {
                "framework": "FastAPI/Django",
                "database": "PostgreSQL",
                "cache": "Redis",
                "message_queue": "RabbitMQ",
            },
            "considerations": [
                "Horizontal scalability",
                "Stateless services",
                "Event-driven communication",
            ],
        }

    def _generate_design_response(self, request: str) -> str:
        """Generate a design response."""
        return (
            "System Design Analysis:\n\n"
            "1. **Architecture Overview**\n"
            "   - Microservices or Monolithic based on scale\n"
            "   - RESTful API design with OpenAPI specification\n"
            "   - Event-driven communication for decoupling\n\n"
            "2. **Component Structure**\n"
            "   - Clear separation of concerns\n"
            "   - Domain-driven design principles\n"
            "   - Interface-based abstractions\n\n"
            "3. **Data Architecture**\n"
            "   - Appropriate database selection\n"
            "   - Caching strategy\n"
            "   - Data consistency patterns\n\n"
            f"Analyzing request: {request[:100]}..."
        )

    def _generate_tech_stack_response(self, request: str) -> str:
        """Generate a technology stack response."""
        return (
            "Technology Stack Recommendations:\n\n"
            "**Backend:**\n"
            "- Python 3.10+ with FastAPI/Django\n"
            "- TypeScript with Node.js/Nest.js\n"
            "- Go for high-performance services\n\n"
            "**Frontend:**\n"
            "- React/Next.js for web applications\n"
            "- Vue.js/Nuxt.js as alternative\n\n"
            "**Database:**\n"
            "- PostgreSQL for relational data\n"
            "- MongoDB for document storage\n"
            "- Redis for caching and sessions\n\n"
            "**Infrastructure:**\n"
            "- Docker for containerization\n"
            "- Kubernetes for orchestration\n"
            "- Terraform for IaC"
        )

    def _generate_scalability_response(self, request: str) -> str:
        """Generate a scalability response."""
        return (
            "Scalability & Performance Analysis:\n\n"
            "**Horizontal Scaling:**\n"
            "- Stateless service design\n"
            "- Load balancer distribution\n"
            "- Database read replicas\n\n"
            "**Performance Optimization:**\n"
            "- Query optimization\n"
            "- Caching strategies (L1, L2, CDN)\n"
            "- Connection pooling\n"
            "- Async processing for heavy tasks\n\n"
            "**Resilience:**\n"
            "- Circuit breakers\n"
            "- Retry policies\n"
            "- Graceful degradation\n"
            "- Health checks and monitoring"
        )

    def _generate_pattern_response(self, request: str) -> str:
        """Generate a design pattern response."""
        return (
            "Recommended Design Patterns:\n\n"
            "**Creational:**\n"
            "- Factory for object creation\n"
            "- Singleton for shared resources\n"
            "- Builder for complex objects\n\n"
            "**Structural:**\n"
            "- Adapter for integration\n"
            "- Facade for simplified interfaces\n"
            "- Decorator for extensibility\n\n"
            "**Behavioral:**\n"
            "- Strategy for algorithms\n"
            "- Observer for events\n"
            "- Command for operations\n\n"
            "**Architectural:**\n"
            "- Repository for data access\n"
            "- CQRS for read/write separation\n"
            "- Event Sourcing for audit trails"
        )

    def _generate_component_response(self, request: str) -> str:
        """Generate a component design response."""
        return (
            "Component Design Guidelines:\n\n"
            "**Module Structure:**\n"
            "- Single responsibility principle\n"
            "- Loose coupling between components\n"
            "- High cohesion within components\n\n"
            "**Interface Design:**\n"
            "- Contract-first approach\n"
            "- Version-aware APIs\n"
            "- Clear error handling\n\n"
            "**Dependencies:**\n"
            "- Dependency injection\n"
            "- Interface segregation\n"
            "- Minimal external dependencies"
        )

    def get_design_artifacts(self) -> list[dict[str, Any]]:
        """Get all design artifacts created by this agent."""
        return self._design_artifacts.copy()
    
    async def _handle_task_with_autogen(self, task: Any) -> dict[str, Any]:
        """Handle a task using AutoGen LLM for intelligent architecture design."""
        task_prompt = (
            f"As a software architect, design the architecture for the following task:\n\n"
            f"Task: {task.title}\n"
            f"Description: {task.description}\n"
            f"Type: {getattr(task, 'task_type', 'unknown')}\n\n"
            "Please provide:\n1. System architecture\n2. Component design\n3. Technology recommendations\n4. Scalability considerations"
        )
        response = await self._generate_autogen_response(task_prompt)
        return {"content": response, "success": True, "artifacts": [], "needs_correction": False}
