"""
Plugin Base - Base classes and contracts for plugins.

This module defines the base structure for plugins that can
extend the orchestrator's functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PluginType(str, Enum):
    """Types of plugins supported by the orchestrator."""

    AGENT = "agent"  # Extends agent capabilities
    ADAPTER = "adapter"  # Adds new external integrations
    EVALUATOR = "evaluator"  # Custom evaluation logic
    PROCESSOR = "processor"  # Task/message processors
    HOOK = "hook"  # Lifecycle hooks
    STORAGE = "storage"  # Storage backends
    OBSERVER = "observer"  # Observability plugins


@dataclass
class PluginMetadata:
    """Metadata describing a plugin."""

    name: str
    version: str
    description: str
    author: str = "Unknown"
    plugin_type: PluginType = PluginType.PROCESSOR
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    enabled_by_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "dependencies": self.dependencies,
            "tags": self.tags,
            "enabled_by_default": self.enabled_by_default,
        }


class Plugin(ABC):
    """
    Base class for all plugins.

    Plugins can extend the orchestrator's functionality in various ways,
    from adding new agents to providing custom evaluation logic.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration.
        """
        self._config = config or {}
        self._enabled = False
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin metadata."""
        pass

    @property
    def is_enabled(self) -> bool:
        """Check if the plugin is enabled."""
        return self._enabled

    @property
    def is_initialized(self) -> bool:
        """Check if the plugin is initialized."""
        return self._initialized

    @property
    def config(self) -> dict[str, Any]:
        """Return the plugin configuration."""
        return self._config

    async def initialize(self) -> None:
        """
        Initialize the plugin.

        Called when the plugin is first loaded. Override to perform
        any setup required.
        """
        self._initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown the plugin.

        Called when the plugin is being unloaded. Override to perform
        any cleanup required.
        """
        self._enabled = False
        self._initialized = False

    def enable(self) -> None:
        """Enable the plugin."""
        if self._initialized:
            self._enabled = True

    def disable(self) -> None:
        """Disable the plugin."""
        self._enabled = False

    def configure(self, config: dict[str, Any]) -> None:
        """
        Update plugin configuration.

        Args:
            config: New configuration values.
        """
        self._config.update(config)

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the plugin's main functionality.

        Args:
            context: Execution context.

        Returns:
            Execution result.
        """
        pass

    def get_status(self) -> dict[str, Any]:
        """Get plugin status."""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "type": self.metadata.plugin_type.value,
            "enabled": self._enabled,
            "initialized": self._initialized,
        }


class HookPlugin(Plugin):
    """
    Base class for hook plugins.

    Hook plugins can intercept and modify behavior at various
    points in the orchestrator lifecycle.
    """

    @abstractmethod
    async def on_task_created(self, task: Any) -> Any:
        """Called when a task is created."""
        pass

    @abstractmethod
    async def on_task_started(self, task: Any) -> None:
        """Called when a task starts execution."""
        pass

    @abstractmethod
    async def on_task_completed(self, task: Any, result: Any) -> Any:
        """Called when a task completes."""
        pass

    @abstractmethod
    async def on_message_sent(self, message: Any) -> Any:
        """Called when a message is sent between agents."""
        pass

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute hook based on context."""
        hook_type = context.get("hook_type")
        payload = context.get("payload")

        if hook_type == "task_created":
            result = await self.on_task_created(payload)
        elif hook_type == "task_started":
            await self.on_task_started(payload)
            result = payload
        elif hook_type == "task_completed":
            result = await self.on_task_completed(
                payload.get("task"),
                payload.get("result"),
            )
        elif hook_type == "message_sent":
            result = await self.on_message_sent(payload)
        else:
            result = payload

        return {"result": result}


class ProcessorPlugin(Plugin):
    """
    Base class for processor plugins.

    Processor plugins transform data at various stages of processing.
    """

    @abstractmethod
    async def process(self, data: Any, context: dict[str, Any]) -> Any:
        """
        Process data.

        Args:
            data: Data to process.
            context: Processing context.

        Returns:
            Processed data.
        """
        pass

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute processor."""
        data = context.get("data")
        result = await self.process(data, context)
        return {"result": result}


class ObserverPlugin(Plugin):
    """
    Base class for observer plugins.

    Observer plugins receive notifications about events but don't
    modify behavior.
    """

    @abstractmethod
    async def observe(self, event_type: str, event_data: Any) -> None:
        """
        Observe an event.

        Args:
            event_type: Type of event.
            event_data: Event data.
        """
        pass

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute observer."""
        event_type = context.get("event_type", "unknown")
        event_data = context.get("event_data")
        await self.observe(event_type, event_data)
        return {"observed": True}
