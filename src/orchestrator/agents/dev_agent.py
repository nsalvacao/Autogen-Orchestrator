"""
Dev Agent - Developer agent for code generation and implementation.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class DevAgent(BaseAgent):
    """
    Developer Agent.

    Responsible for:
    - Code generation and implementation
    - Code modification and refactoring
    - Bug fixing
    - Code review participation
    """

    def __init__(self, name: str = "DevAgent", enable_autogen: bool = False):
        """Initialize the Dev Agent."""
        system_message = (
            "You are a senior software developer with expertise in multiple programming languages. "
            "You excel at code generation, bug fixing, code review, and refactoring. "
            "You write clean, maintainable, and well-tested code following best practices."
        )
        super().__init__(
            name=name,
            description=(
                "Developer agent responsible for code generation, implementation, "
                "bug fixing, and code review."
            ),
            capabilities=[
                AgentCapability.CODING,
                AgentCapability.CODE_REVIEW,
            ],
            enable_autogen=enable_autogen,
            system_message=system_message,
        )
        self._code_artifacts: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the Dev Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        # Try AutoGen first if enabled
        if self.is_autogen_enabled:
            return await self._generate_autogen_response(message.content)
        
        # Fallback to rule-based responses
        content = message.content.lower()

        if "implement" in content or "code" in content or "write" in content:
            return self._generate_implementation_response(message.content)
        elif "review" in content:
            return self._generate_review_response(message.content)
        elif "fix" in content or "bug" in content:
            return self._generate_bugfix_response(message.content)
        elif "refactor" in content:
            return self._generate_refactor_response(message.content)
        else:
            return (
                f"Dev Agent received: {message.content}. "
                "I can help with implementation, code review, bug fixes, and refactoring."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the Dev Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        # If AutoGen is enabled, use it for more intelligent task handling
        if self.is_autogen_enabled:
            return await self._handle_task_with_autogen(task)
        
        # Fallback to rule-based handling
        task_type = getattr(task, "task_type", None)
        task_type_value = task_type.value if task_type else "unknown"

        if task_type_value == "development":
            return await self._handle_development_task(task)
        elif task_type_value == "bug_fix":
            return await self._handle_bugfix_task(task)
        elif task_type_value == "code_review":
            return await self._handle_review_task(task)
        else:
            return {
                "content": f"Processed task: {task.title}",
                "success": True,
                "needs_correction": False,
            }

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if Dev can handle the task type."""
        return task_type in ("development", "bug_fix", "code_review", "feature")

    async def _handle_development_task(self, task: Any) -> dict[str, Any]:
        """Handle a development task."""
        # Placeholder implementation
        code_artifact = {
            "type": "code",
            "filename": f"{task.title.lower().replace(' ', '_')}.py",
            "content": f"# Implementation for: {task.title}\n# TODO: Implement functionality",
            "language": "python",
        }
        self._code_artifacts.append(code_artifact)

        return {
            "content": f"Implementation completed for '{task.title}'",
            "success": True,
            "artifacts": [code_artifact],
            "needs_correction": False,
        }

    async def _handle_bugfix_task(self, task: Any) -> dict[str, Any]:
        """Handle a bug fix task."""
        return {
            "content": f"Bug fix applied for '{task.title}'",
            "success": True,
            "artifacts": [{"type": "patch", "description": f"Fix for {task.title}"}],
            "needs_correction": False,
        }

    async def _handle_review_task(self, task: Any) -> dict[str, Any]:
        """Handle a code review task."""
        return {
            "content": f"Code review completed for '{task.title}'",
            "success": True,
            "artifacts": [{"type": "review", "findings": [], "approved": True}],
            "needs_correction": False,
        }

    def _generate_implementation_response(self, request: str) -> str:
        """Generate an implementation response."""
        return (
            "I'll implement the requested functionality.\n"
            "Steps:\n"
            "1. Analyze requirements\n"
            "2. Design the solution\n"
            "3. Write the code\n"
            "4. Add unit tests\n"
            f"Request: {request[:100]}..."
        )

    def _generate_review_response(self, request: str) -> str:
        """Generate a code review response."""
        return (
            "Code Review Analysis:\n"
            "- Code style: Checking...\n"
            "- Logic errors: Analyzing...\n"
            "- Performance: Evaluating...\n"
            "- Security: Scanning...\n"
            "Will provide detailed feedback."
        )

    def _generate_bugfix_response(self, request: str) -> str:
        """Generate a bug fix response."""
        return (
            "Bug Fix Process:\n"
            "1. Reproduce the issue\n"
            "2. Identify root cause\n"
            "3. Develop fix\n"
            "4. Test thoroughly\n"
            "5. Submit for review"
        )

    def _generate_refactor_response(self, request: str) -> str:
        """Generate a refactoring response."""
        return (
            "Refactoring Plan:\n"
            "1. Identify code smells\n"
            "2. Plan safe transformations\n"
            "3. Apply changes incrementally\n"
            "4. Verify behavior preservation\n"
            "5. Update tests as needed"
        )
    
    async def _handle_task_with_autogen(self, task: Any) -> dict[str, Any]:
        """
        Handle a task using AutoGen LLM.
        
        Args:
            task: The task to handle.
            
        Returns:
            Dictionary with task result.
        """
        task_prompt = (
            f"Task: {task.title}\n"
            f"Description: {task.description}\n"
            f"Type: {getattr(task, 'task_type', 'unknown')}\n"
            f"Priority: {getattr(task, 'priority', 'unknown')}\n\n"
            "Please provide a detailed response for this task."
        )
        
        response = await self._generate_autogen_response(task_prompt)
        
        return {
            "content": response,
            "success": True,
            "artifacts": [],
            "needs_correction": False,
        }
