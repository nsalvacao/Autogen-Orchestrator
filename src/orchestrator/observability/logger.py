"""
Logger - Structured logging for the orchestrator.

Provides a centralized logging facility with support for
structured logging and future integration with log aggregation systems.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(str, Enum):
    """Log levels for the orchestrator."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry."""

    level: LogLevel
    message: str
    timestamp: datetime
    component: str
    context: dict[str, Any] | None = None
    correlation_id: str | None = None


class OrchestratorLogger:
    """
    Centralized logger for the orchestrator.

    Provides structured logging with support for:
    - Multiple output targets (placeholder for future implementations)
    - Correlation IDs for request tracking
    - Component-level logging
    - Log level filtering
    """

    def __init__(
        self,
        name: str = "orchestrator",
        level: LogLevel = LogLevel.INFO,
    ):
        """
        Initialize the logger.

        Args:
            name: Logger name.
            level: Minimum log level.
        """
        self._name = name
        self._level = level
        self._entries: list[LogEntry] = []
        self._handlers: list[logging.Handler] = []

        # Configure Python logging
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._get_logging_level(level))

        # Add console handler if no handlers exist
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            self._logger.addHandler(handler)

    def _get_logging_level(self, level: LogLevel) -> int:
        """Convert LogLevel to logging module level."""
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(level, logging.INFO)

    def debug(
        self,
        message: str,
        component: str = "general",
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message, component, context, correlation_id)

    def info(
        self,
        message: str,
        component: str = "general",
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message, component, context, correlation_id)

    def warning(
        self,
        message: str,
        component: str = "general",
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message, component, context, correlation_id)

    def error(
        self,
        message: str,
        component: str = "general",
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Log an error message."""
        self._log(LogLevel.ERROR, message, component, context, correlation_id)

    def critical(
        self,
        message: str,
        component: str = "general",
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Log a critical message."""
        self._log(LogLevel.CRITICAL, message, component, context, correlation_id)

    def _log(
        self,
        level: LogLevel,
        message: str,
        component: str,
        context: dict[str, Any] | None,
        correlation_id: str | None,
    ) -> None:
        """Internal logging method."""
        entry = LogEntry(
            level=level,
            message=message,
            timestamp=datetime.now(),
            component=component,
            context=context,
            correlation_id=correlation_id,
        )
        self._entries.append(entry)

        # Format message with context
        formatted_message = f"[{component}] {message}"
        if correlation_id:
            formatted_message = f"[{correlation_id}] {formatted_message}"
        if context:
            formatted_message = f"{formatted_message} | {context}"

        # Log using Python logging
        log_method = getattr(self._logger, level.value)
        log_method(formatted_message)

    def get_entries(
        self,
        level: LogLevel | None = None,
        component: str | None = None,
        limit: int | None = None,
    ) -> list[LogEntry]:
        """
        Get log entries with optional filtering.

        Args:
            level: Filter by log level.
            component: Filter by component.
            limit: Maximum number of entries to return.

        Returns:
            List of matching log entries.
        """
        entries = self._entries

        if level is not None:
            entries = [e for e in entries if e.level == level]

        if component is not None:
            entries = [e for e in entries if e.component == component]

        if limit is not None:
            entries = entries[-limit:]

        return entries
