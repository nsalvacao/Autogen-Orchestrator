"""
Adapter Contract - Defines the interface for external system adapters.

Adapters provide a bridge between the orchestrator and external systems
such as CLIs, APIs, databases, and other services. This contract ensures
consistent integration patterns.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class AdapterType(str, Enum):
    """Types of adapters supported by the orchestrator."""

    CLI = "cli"
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    VERSION_CONTROL = "version_control"
    CI_CD = "ci_cd"
    MESSAGING = "messaging"
    CLOUD = "cloud"


class AdapterStatus(str, Enum):
    """Status of an adapter."""

    NOT_CONFIGURED = "not_configured"
    CONFIGURED = "configured"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class AdapterConfig:
    """Configuration for an adapter."""

    adapter_type: AdapterType
    name: str
    enabled: bool = False
    # Placeholder for credentials - to be implemented with proper secret management
    credentials_placeholder: str = "NOT_CONFIGURED"
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Result of an adapter operation."""

    success: bool
    data: Any = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class AdapterContract(ABC):
    """
    Abstract base class defining the contract for external system adapters.

    Adapters bridge the orchestrator with external systems. This contract
    ensures consistent patterns for future integrations.
    """

    def __init__(self, config: AdapterConfig):
        """
        Initialize the adapter with configuration.

        Args:
            config: The adapter configuration.
        """
        self._config = config
        self._status = AdapterStatus.NOT_CONFIGURED

    @property
    def config(self) -> AdapterConfig:
        """Return the adapter configuration."""
        return self._config

    @property
    def status(self) -> AdapterStatus:
        """Return the current adapter status."""
        return self._status

    @property
    @abstractmethod
    def adapter_type(self) -> AdapterType:
        """Return the type of this adapter."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this adapter."""
        pass

    @abstractmethod
    async def connect(self) -> AdapterResult:
        """
        Establish connection to the external system.

        Returns:
            AdapterResult indicating success or failure.
        """
        pass

    @abstractmethod
    async def disconnect(self) -> AdapterResult:
        """
        Disconnect from the external system.

        Returns:
            AdapterResult indicating success or failure.
        """
        pass

    @abstractmethod
    async def execute(self, operation: str, **kwargs: Any) -> AdapterResult:
        """
        Execute an operation on the external system.

        Args:
            operation: The operation to execute.
            **kwargs: Operation-specific parameters.

        Returns:
            AdapterResult containing the operation result.
        """
        pass

    @abstractmethod
    async def health_check(self) -> AdapterResult:
        """
        Check the health of the connection to the external system.

        Returns:
            AdapterResult indicating the health status.
        """
        pass

    def is_connected(self) -> bool:
        """Check if the adapter is connected."""
        return self._status == AdapterStatus.CONNECTED

    def is_configured(self) -> bool:
        """Check if the adapter is configured."""
        return self._status != AdapterStatus.NOT_CONFIGURED
