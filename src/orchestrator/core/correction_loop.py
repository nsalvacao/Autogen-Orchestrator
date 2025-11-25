"""
Correction Loop - Implements iterative improvement through evaluation and correction.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from orchestrator.contracts.evaluation_contract import (
    EvaluationContract,
    EvaluationResult,
    EvaluationSeverity,
)
from orchestrator.core.task import Task, TaskStatus


class CorrectionStatus(str, Enum):
    """Status of a correction loop."""

    PENDING = "pending"
    EVALUATING = "evaluating"
    CORRECTING = "correcting"
    COMPLETED = "completed"
    MAX_ITERATIONS_REACHED = "max_iterations_reached"
    FAILED = "failed"


@dataclass
class CorrectionIteration:
    """A single iteration in a correction loop."""

    iteration_number: int
    evaluation_result: EvaluationResult
    correction_applied: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CorrectionLoopResult:
    """Result of a correction loop."""

    success: bool
    final_output: Any
    iterations: list[CorrectionIteration] = field(default_factory=list)
    total_iterations: int = 0
    status: CorrectionStatus = CorrectionStatus.COMPLETED
    metadata: dict[str, Any] = field(default_factory=dict)


class CorrectionLoop:
    """
    Implements iterative correction loops for task outputs.

    The correction loop evaluates outputs, identifies issues,
    and triggers corrections until quality criteria are met
    or maximum iterations are reached.
    """

    def __init__(
        self,
        evaluators: list[EvaluationContract] | None = None,
        max_iterations: int = 3,
        min_passing_score: float = 0.8,
    ):
        """
        Initialize the correction loop.

        Args:
            evaluators: List of evaluators to use.
            max_iterations: Maximum number of correction iterations.
            min_passing_score: Minimum score to consider output acceptable.
        """
        self._evaluators = evaluators or []
        self._max_iterations = max_iterations
        self._min_passing_score = min_passing_score
        self._correction_handlers: dict[str, Callable] = {}

    def add_evaluator(self, evaluator: EvaluationContract) -> None:
        """Add an evaluator to the loop."""
        self._evaluators.append(evaluator)

    def register_correction_handler(
        self, category: str, handler: Callable[[Any, EvaluationResult], Any]
    ) -> None:
        """
        Register a correction handler for a specific category.

        Args:
            category: The category of issues this handler addresses.
            handler: The correction function.
        """
        self._correction_handlers[category] = handler

    async def run(
        self,
        task: Task,
        initial_output: Any,
        context: dict[str, Any] | None = None,
    ) -> CorrectionLoopResult:
        """
        Run the correction loop on task output.

        Args:
            task: The task being corrected.
            initial_output: The initial output to evaluate and correct.
            context: Additional context for evaluation.

        Returns:
            CorrectionLoopResult with the final output and iteration history.
        """
        current_output = initial_output
        iterations: list[CorrectionIteration] = []
        context = context or {}

        for iteration_num in range(self._max_iterations):
            # Evaluate current output
            evaluation_results = await self._evaluate_all(current_output, context)
            combined_result = self._combine_results(evaluation_results)

            iteration = CorrectionIteration(
                iteration_number=iteration_num + 1,
                evaluation_result=combined_result,
            )

            # Check if output passes
            if combined_result.passed and combined_result.score >= self._min_passing_score:
                iterations.append(iteration)
                return CorrectionLoopResult(
                    success=True,
                    final_output=current_output,
                    iterations=iterations,
                    total_iterations=iteration_num + 1,
                    status=CorrectionStatus.COMPLETED,
                )

            # Check if correction is needed and possible
            if not combined_result.needs_correction:
                iterations.append(iteration)
                return CorrectionLoopResult(
                    success=combined_result.passed,
                    final_output=current_output,
                    iterations=iterations,
                    total_iterations=iteration_num + 1,
                    status=CorrectionStatus.COMPLETED,
                )

            # Apply corrections
            correction_applied = await self._apply_corrections(
                current_output, combined_result, context
            )
            iteration.correction_applied = correction_applied
            iterations.append(iteration)

            # Update task correction count
            task.correction_count += 1
            task.update_status(TaskStatus.NEEDS_CORRECTION)

        # Max iterations reached - update task status to reflect failure
        task.update_status(TaskStatus.FAILED)
        return CorrectionLoopResult(
            success=False,
            final_output=current_output,
            iterations=iterations,
            total_iterations=self._max_iterations,
            status=CorrectionStatus.MAX_ITERATIONS_REACHED,
        )

    async def _evaluate_all(
        self, output: Any, context: dict[str, Any]
    ) -> list[EvaluationResult]:
        """Evaluate output with all registered evaluators."""
        results = []
        for evaluator in self._evaluators:
            result = await evaluator.evaluate(output, context)
            results.append(result)
        return results

    def _combine_results(self, results: list[EvaluationResult]) -> EvaluationResult:
        """Combine multiple evaluation results into one."""
        if not results:
            return EvaluationResult(
                evaluator_name="combined",
                passed=True,
                score=1.0,
            )

        # Combine scores (average)
        avg_score = sum(r.score for r in results) / len(results)

        # Combine findings
        all_findings = []
        for result in results:
            all_findings.extend(result.findings)

        # Check if any evaluation failed
        passed = all(r.passed for r in results)

        # Check if any evaluation needs correction
        needs_correction = any(r.needs_correction for r in results)

        # Combine correction suggestions
        all_suggestions = []
        for result in results:
            all_suggestions.extend(result.correction_suggestions)

        return EvaluationResult(
            evaluator_name="combined",
            passed=passed,
            score=avg_score,
            findings=all_findings,
            needs_correction=needs_correction,
            correction_suggestions=all_suggestions,
        )

    async def _apply_corrections(
        self,
        output: Any,
        evaluation_result: EvaluationResult,
        context: dict[str, Any],
    ) -> str:
        """
        Apply corrections based on evaluation results.

        Returns a description of corrections applied.
        """
        corrections_applied = []

        for finding in evaluation_result.findings:
            if finding.severity in (EvaluationSeverity.ERROR, EvaluationSeverity.CRITICAL):
                handler = self._correction_handlers.get(finding.category)
                if handler:
                    # In a real implementation, this would modify the output
                    corrections_applied.append(
                        f"Applied correction for {finding.category}: {finding.message}"
                    )

        if not corrections_applied:
            corrections_applied.append("No automatic corrections available")

        return "; ".join(corrections_applied)


class CorrectionLoopFactory:
    """Factory for creating configured correction loops."""

    @staticmethod
    def create_default_loop() -> CorrectionLoop:
        """Create a correction loop with default configuration."""
        return CorrectionLoop(
            max_iterations=3,
            min_passing_score=0.8,
        )

    @staticmethod
    def create_strict_loop() -> CorrectionLoop:
        """Create a strict correction loop with more iterations and higher threshold."""
        return CorrectionLoop(
            max_iterations=5,
            min_passing_score=0.95,
        )

    @staticmethod
    def create_lenient_loop() -> CorrectionLoop:
        """Create a lenient correction loop with fewer iterations."""
        return CorrectionLoop(
            max_iterations=2,
            min_passing_score=0.6,
        )
