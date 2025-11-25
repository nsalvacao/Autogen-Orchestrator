"""
QA Agent - Quality Assurance agent for testing and validation.
"""

from typing import Any

from orchestrator.agents.base_agent import BaseAgent
from orchestrator.contracts.agent_contract import AgentCapability, AgentMessage


class QAAgent(BaseAgent):
    """
    Quality Assurance Agent.

    Responsible for:
    - Test planning and strategy
    - Test case generation
    - Test execution
    - Bug reporting
    - Quality validation
    """

    def __init__(self, name: str = "QAAgent"):
        """Initialize the QA Agent."""
        super().__init__(
            name=name,
            description=(
                "Quality Assurance agent responsible for test planning, "
                "test case generation, execution, and quality validation."
            ),
            capabilities=[
                AgentCapability.TESTING,
                AgentCapability.EVALUATION,
            ],
        )
        self._test_results: list[dict[str, Any]] = []

    async def _process_message_impl(self, message: AgentMessage) -> str:
        """
        Process a message as the QA Agent.

        Args:
            message: The incoming message.

        Returns:
            Response content string.
        """
        content = message.content.lower()

        if "test" in content:
            return self._generate_test_response(message.content)
        elif "validate" in content or "verify" in content:
            return self._generate_validation_response(message.content)
        elif "bug" in content or "issue" in content:
            return self._generate_bug_report_response(message.content)
        elif "coverage" in content:
            return self._generate_coverage_response()
        else:
            return (
                f"QA Agent received: {message.content}. "
                "I can help with testing, validation, bug reporting, and coverage analysis."
            )

    async def _handle_task_impl(self, task: Any) -> dict[str, Any]:
        """
        Handle a task as the QA Agent.

        Args:
            task: The task to handle.

        Returns:
            Dictionary with task result.
        """
        task_type = getattr(task, "task_type", None)
        task_type_value = task_type.value if task_type else "unknown"

        if task_type_value == "testing":
            return await self._handle_testing_task(task)
        else:
            # QA can evaluate any task output
            return await self._evaluate_task_output(task)

    def _can_handle_impl(self, task_type: str) -> bool:
        """Check if QA can handle the task type."""
        return task_type in ("testing", "code_review", "evaluation")

    async def _handle_testing_task(self, task: Any) -> dict[str, Any]:
        """Handle a testing task."""
        test_results = self._generate_test_results(task)
        self._test_results.extend(test_results)

        passed = all(r.get("passed", False) for r in test_results)
        needs_correction = not passed

        result_msg = "All tests passed." if passed else "Some tests failed."
        return {
            "content": f"Testing completed for '{task.title}'. {result_msg}",
            "success": passed,
            "artifacts": [{"type": "test_results", "data": test_results}],
            "needs_correction": needs_correction,
            "correction_reason": "Test failures detected" if needs_correction else None,
        }

    async def _evaluate_task_output(self, task: Any) -> dict[str, Any]:
        """Evaluate the output of another task."""
        evaluation = {
            "meets_requirements": True,
            "quality_score": 0.85,
            "issues_found": [],
            "recommendations": [],
        }

        return {
            "content": f"Evaluation completed for '{task.title}'",
            "success": True,
            "artifacts": [{"type": "evaluation", "data": evaluation}],
            "needs_correction": False,
        }

    def _generate_test_results(self, task: Any) -> list[dict[str, Any]]:
        """Generate placeholder test results."""
        return [
            {
                "test_name": f"test_{task.title.lower().replace(' ', '_')}_basic",
                "passed": True,
                "duration_ms": 50,
            },
            {
                "test_name": f"test_{task.title.lower().replace(' ', '_')}_edge_cases",
                "passed": True,
                "duration_ms": 120,
            },
            {
                "test_name": f"test_{task.title.lower().replace(' ', '_')}_integration",
                "passed": True,
                "duration_ms": 250,
            },
        ]

    def _generate_test_response(self, request: str) -> str:
        """Generate a testing response."""
        return (
            "Test Strategy:\n"
            "1. Unit tests for individual components\n"
            "2. Integration tests for module interactions\n"
            "3. End-to-end tests for user workflows\n"
            "4. Performance tests if applicable\n"
            f"Request: {request[:100]}..."
        )

    def _generate_validation_response(self, request: str) -> str:
        """Generate a validation response."""
        return (
            "Validation Checklist:\n"
            "- [ ] Requirements coverage\n"
            "- [ ] Functional correctness\n"
            "- [ ] Edge case handling\n"
            "- [ ] Error handling\n"
            "- [ ] Performance benchmarks"
        )

    def _generate_bug_report_response(self, request: str) -> str:
        """Generate a bug report response."""
        return (
            "Bug Report Template:\n"
            "- Summary: Brief description\n"
            "- Steps to Reproduce: ...\n"
            "- Expected Behavior: ...\n"
            "- Actual Behavior: ...\n"
            "- Severity: Critical/High/Medium/Low"
        )

    def _generate_coverage_response(self) -> str:
        """Generate a coverage report response."""
        return (
            "Test Coverage Report:\n"
            "- Line coverage: Calculating...\n"
            "- Branch coverage: Calculating...\n"
            "- Function coverage: Calculating...\n"
            "- Uncovered areas: Identifying..."
        )
