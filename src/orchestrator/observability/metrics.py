"""
Metrics - Metrics collection for observability.

Provides metrics collection and aggregation for monitoring
orchestrator performance and health.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MetricType(str, Enum):
    """Types of metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """A single metric data point."""

    name: str
    metric_type: MetricType
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricSummary:
    """Summary statistics for a metric."""

    name: str
    count: int
    total: float
    min_value: float
    max_value: float
    avg_value: float


class MetricsCollector:
    """
    Collects and aggregates metrics for the orchestrator.

    This is a placeholder implementation that provides basic
    in-memory metrics collection. Future implementations will
    integrate with external metrics systems like Prometheus.

    Metrics collected:
    - Task processing times
    - Agent response times
    - Conversation turn counts
    - Correction loop iterations
    - Error rates
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self._metrics: list[Metric] = []
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}

    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Increment a counter metric.

        Args:
            name: Counter name.
            value: Value to add.
            labels: Optional labels.
        """
        key = self._make_key(name, labels)
        self._counters[key] = self._counters.get(key, 0.0) + value

        self._metrics.append(
            Metric(
                name=name,
                metric_type=MetricType.COUNTER,
                value=self._counters[key],
                labels=labels or {},
            )
        )

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Set a gauge metric.

        Args:
            name: Gauge name.
            value: Gauge value.
            labels: Optional labels.
        """
        key = self._make_key(name, labels)
        self._gauges[key] = value

        self._metrics.append(
            Metric(
                name=name,
                metric_type=MetricType.GAUGE,
                value=value,
                labels=labels or {},
            )
        )

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a histogram observation.

        Args:
            name: Histogram name.
            value: Observed value.
            labels: Optional labels.
        """
        self._metrics.append(
            Metric(
                name=name,
                metric_type=MetricType.HISTOGRAM,
                value=value,
                labels=labels or {},
            )
        )

    def record_timer(
        self,
        name: str,
        duration_ms: float,
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a timer observation.

        Args:
            name: Timer name.
            duration_ms: Duration in milliseconds.
            labels: Optional labels.
        """
        self._metrics.append(
            Metric(
                name=name,
                metric_type=MetricType.TIMER,
                value=duration_ms,
                labels=labels or {},
            )
        )

    def _make_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Create a unique key for a metric with labels."""
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get the current value of a counter."""
        key = self._make_key(name, labels)
        return self._counters.get(key, 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float:
        """Get the current value of a gauge."""
        key = self._make_key(name, labels)
        return self._gauges.get(key, 0.0)

    def get_summary(self, name: str) -> MetricSummary | None:
        """
        Get summary statistics for a metric.

        Args:
            name: Metric name.

        Returns:
            MetricSummary or None if no data.
        """
        values = [m.value for m in self._metrics if m.name == name]

        if not values:
            return None

        return MetricSummary(
            name=name,
            count=len(values),
            total=sum(values),
            min_value=min(values),
            max_value=max(values),
            avg_value=sum(values) / len(values),
        )

    def get_all_metrics(self) -> list[Metric]:
        """Get all recorded metrics."""
        return self._metrics.copy()

    def clear(self) -> None:
        """Clear all metrics."""
        self._metrics.clear()
        self._counters.clear()
        self._gauges.clear()

    def export(self) -> dict[str, Any]:
        """
        Export metrics in a format suitable for external systems.

        Returns:
            Dictionary with metrics data.
        """
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "metrics_count": len(self._metrics),
            "export_timestamp": datetime.now().isoformat(),
        }
