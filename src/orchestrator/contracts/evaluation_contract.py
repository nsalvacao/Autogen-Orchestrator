"""
Evaluation Contract - Defines the interface for task and output evaluation.

This module provides the contract for evaluation mechanisms used in
correction loops and quality assurance processes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EvaluationStatus(str, Enum):
    """Status of an evaluation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationSeverity(str, Enum):
    """Severity levels for evaluation findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class EvaluationFinding:
    """A finding from an evaluation."""

    category: str
    message: str
    severity: EvaluationSeverity = EvaluationSeverity.INFO
    location: str | None = None
    suggestion: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result of an evaluation."""

    evaluator_name: str
    passed: bool
    score: float = 0.0  # 0.0 to 1.0
    findings: list[EvaluationFinding] = field(default_factory=list)
    needs_correction: bool = False
    correction_suggestions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class EvaluationContract(ABC):
    """
    Abstract base class defining the contract for evaluators.

    Evaluators assess the quality and correctness of agent outputs
    and determine if correction loops are needed.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this evaluator."""
        pass

    @property
    @abstractmethod
    def evaluation_criteria(self) -> list[str]:
        """Return the list of criteria this evaluator checks."""
        pass

    @abstractmethod
    async def evaluate(self, content: Any, context: dict[str, Any]) -> EvaluationResult:
        """
        Evaluate content against the defined criteria.

        Args:
            content: The content to evaluate.
            context: Additional context for evaluation.

        Returns:
            EvaluationResult containing the evaluation outcome.
        """
        pass

    @abstractmethod
    def should_trigger_correction(self, result: EvaluationResult) -> bool:
        """
        Determine if a correction loop should be triggered.

        Args:
            result: The evaluation result to check.

        Returns:
            True if correction is needed, False otherwise.
        """
        pass

    async def initialize(self) -> None:
        """Initialize the evaluator. Override if needed."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the evaluator gracefully. Override if needed."""
        pass
