"""
Docs Agent - Documentation agent for generating and maintaining documentation.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class DocsAgent(BaseAgent):
    """
    Documentation Agent.

    Responsible for:
    - Documentation generation
    - API documentation
    - User guides and tutorials
    - Code comments and docstrings
    - README maintenance
    """

    def __init__(self, name: str = "DocsAgent"):
        """Initialize the Docs Agent."""
        super().__init__(
            name=name,
            description=(
                "Documentation agent responsible for generating and maintaining "
                "documentation, API docs, user guides, and code documentation."
            ),
            capabilities=[
                AgentCapability.DOCUMENTATION,
            ],
        )
        self._documentation_artifacts: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Docs Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        content = message.content.lower()

        if "api" in content:
            return self._generate_api_doc_response(message.content)
        elif "readme" in content:
            return self._generate_readme_response(message.content)
        elif "guide" in content or "tutorial" in content:
            return self._generate_guide_response(message.content)
        elif "docstring" in content or "comment" in content:
            return self._generate_code_doc_response(message.content)
        else:
            return (
                f"Docs Agent received: {message.content}. "
                "I can help with API docs, READMEs, user guides, and code documentation."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Docs Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        task_type = getattr(task, "task_type", None)
        task_type_value = task_type.value if task_type else "unknown"

        if task_type_value == "documentation":
            return await self._handle_documentation_task(task)
        else:
            # Generate documentation for any task
            return await self._generate_task_documentation(task)

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Docs can handle the task type."""
        return task_type in ("documentation",)

    async def _handle_documentation_task(self, task: Any) -> dict[str, Any]:
        """Handle a documentation task."""
        doc_artifact = self._generate_documentation(task)
        self._documentation_artifacts.append(doc_artifact)

        return {
            "content": f"Documentation generated for '{task.title}'",
            "success": True,
            "artifacts": [doc_artifact],
            "needs_correction": False,
        }

    async def _generate_task_documentation(self, task: Any) -> dict[str, Any]:
        """Generate documentation for a task."""
        doc_artifact = {
            "type": "documentation",
            "format": "markdown",
            "content": self._create_doc_content(task),
        }

        return {
            "content": f"Task documentation created for '{task.title}'",
            "success": True,
            "artifacts": [doc_artifact],
            "needs_correction": False,
        }

    def _generate_documentation(self, task: Any) -> dict[str, Any]:
        """Generate documentation artifact."""
        return {
            "type": "documentation",
            "format": "markdown",
            "filename": f"{task.title.lower().replace(' ', '_')}_docs.md",
            "content": self._create_doc_content(task),
        }

    def _create_doc_content(self, task: Any) -> str:
        """Create documentation content for a task."""
        return f"""# {task.title}

## Overview
{task.description}

## Details
This documentation was auto-generated for task: {task.id}

### Task Type
{getattr(task, 'task_type', 'N/A')}

### Priority
{getattr(task, 'priority', 'N/A')}

## Usage
*Documentation to be expanded based on implementation details.*

## Related
- Dependencies: {getattr(task, 'dependencies', [])}
- Subtasks: {getattr(task, 'subtasks', [])}
"""

    def _generate_api_doc_response(self, request: str) -> str:
        """Generate an API documentation response."""
        return (
            "API Documentation Structure:\n"
            "1. Endpoint descriptions\n"
            "2. Request/Response schemas\n"
            "3. Authentication requirements\n"
            "4. Example requests\n"
            "5. Error codes and handling"
        )

    def _generate_readme_response(self, request: str) -> str:
        """Generate a README response."""
        return (
            "README Template:\n"
            "- Project title and description\n"
            "- Installation instructions\n"
            "- Quick start guide\n"
            "- Configuration options\n"
            "- Contributing guidelines\n"
            "- License information"
        )

    def _generate_guide_response(self, request: str) -> str:
        """Generate a user guide response."""
        return (
            "User Guide Outline:\n"
            "1. Getting Started\n"
            "2. Basic Concepts\n"
            "3. Step-by-step Tutorials\n"
            "4. Advanced Features\n"
            "5. Troubleshooting\n"
            "6. FAQ"
        )

    def _generate_code_doc_response(self, request: str) -> str:
        """Generate a code documentation response."""
        return (
            "Code Documentation Standards:\n"
            "- Module-level docstrings\n"
            "- Class documentation\n"
            "- Function/method docstrings\n"
            "- Inline comments for complex logic\n"
            "- Type hints and annotations"
        )
