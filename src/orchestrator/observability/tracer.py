"""
Tracer - Distributed tracing for the orchestrator.

Provides tracing capabilities for tracking requests across
agents and components.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SpanStatus(str, Enum):
    """Status of a trace span."""

    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SpanEvent:
    """An event within a span."""

    name: str
    timestamp: datetime = field(default_factory=datetime.now)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """
    A span represents a single operation within a trace.

    Spans form a tree structure representing the call hierarchy.
    """

    name: str
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:16])
    parent_span_id: str | None = None
    status: SpanStatus = SpanStatus.OK
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span."""
        self.events.append(
            SpanEvent(
                name=name,
                attributes=attributes or {},
            )
        )

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        self.attributes[key] = value

    def end(self, status: SpanStatus = SpanStatus.OK) -> None:
        """End the span."""
        self.end_time = datetime.now()
        self.status = status

    @property
    def duration_ms(self) -> float | None:
        """Get span duration in milliseconds."""
        if self.end_time is None:
            return None
        delta = self.end_time - self.start_time
        return delta.total_seconds() * 1000


@dataclass
class Trace:
    """
    A trace represents a complete request through the system.

    Contains one or more spans representing the operations performed.
    """

    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spans: list[Span] = field(default_factory=list)
    root_span_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_span(self, span: Span) -> None:
        """Add a span to the trace."""
        self.spans.append(span)
        if span.parent_span_id is None:
            self.root_span_id = span.span_id


class Tracer:
    """
    Distributed tracer for the orchestrator.

    This is a placeholder implementation that provides basic
    in-memory tracing. Future implementations will integrate
    with distributed tracing systems like Jaeger or Zipkin.

    Features:
    - Trace creation and management
    - Span creation with parent-child relationships
    - Event recording within spans
    - Context propagation helpers
    """

    def __init__(self, service_name: str = "orchestrator"):
        """
        Initialize the tracer.

        Args:
            service_name: Name of the service for tracing.
        """
        self._service_name = service_name
        self._traces: dict[str, Trace] = {}
        self._active_spans: dict[str, Span] = {}

    def create_trace(self, metadata: dict[str, Any] | None = None) -> Trace:
        """
        Create a new trace.

        Args:
            metadata: Optional trace metadata.

        Returns:
            The created trace.
        """
        trace = Trace(metadata=metadata or {})
        self._traces[trace.trace_id] = trace
        return trace

    def start_span(
        self,
        name: str,
        trace_id: str,
        parent_span_id: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Span:
        """
        Start a new span.

        Args:
            name: Span name.
            trace_id: Parent trace ID.
            parent_span_id: Optional parent span ID.
            attributes: Optional span attributes.

        Returns:
            The created span.
        """
        span = Span(
            name=name,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            attributes=attributes or {},
        )

        # Add to trace
        trace = self._traces.get(trace_id)
        if trace:
            trace.add_span(span)

        self._active_spans[span.span_id] = span
        return span

    def end_span(self, span_id: str, status: SpanStatus = SpanStatus.OK) -> None:
        """
        End a span.

        Args:
            span_id: The span ID to end.
            status: Final status of the span.
        """
        span = self._active_spans.pop(span_id, None)
        if span:
            span.end(status)

    def get_trace(self, trace_id: str) -> Trace | None:
        """Get a trace by ID."""
        return self._traces.get(trace_id)

    def get_active_span(self, span_id: str) -> Span | None:
        """Get an active span by ID."""
        return self._active_spans.get(span_id)

    def get_all_traces(self) -> list[Trace]:
        """Get all traces."""
        return list(self._traces.values())

    def export_trace(self, trace_id: str) -> dict[str, Any] | None:
        """
        Export a trace in a format suitable for external systems.

        Args:
            trace_id: The trace ID to export.

        Returns:
            Dictionary with trace data, or None if not found.
        """
        trace = self._traces.get(trace_id)
        if trace is None:
            return None

        return {
            "trace_id": trace.trace_id,
            "service": self._service_name,
            "created_at": trace.created_at.isoformat(),
            "span_count": len(trace.spans),
            "spans": [
                {
                    "span_id": s.span_id,
                    "name": s.name,
                    "parent_span_id": s.parent_span_id,
                    "status": s.status.value,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "duration_ms": s.duration_ms,
                    "attributes": s.attributes,
                    "events": [
                        {
                            "name": e.name,
                            "timestamp": e.timestamp.isoformat(),
                            "attributes": e.attributes,
                        }
                        for e in s.events
                    ],
                }
                for s in trace.spans
            ],
            "metadata": trace.metadata,
        }

    def clear(self) -> None:
        """Clear all traces."""
        self._traces.clear()
        self._active_spans.clear()
