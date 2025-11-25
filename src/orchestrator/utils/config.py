"""
Config - Configuration management for the orchestrator.

Provides configuration loading and management with support for
environment variables and configuration files.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Environment(str, Enum):
    """Deployment environments."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class LLMConfig:
    """Configuration for LLM integration (placeholder)."""

    provider: str = "NOT_CONFIGURED"
    model: str = "NOT_CONFIGURED"
    # Placeholder for API key - should use proper secret management
    api_key_env_var: str = "ORCHESTRATOR_LLM_API_KEY"
    max_tokens: int = 4096
    temperature: float = 0.7


@dataclass
class AgentConfig:
    """Configuration for agents."""

    enabled_agents: list[str] = field(
        default_factory=lambda: ["PMAgent", "DevAgent", "QAAgent", "SecurityAgent", "DocsAgent"]
    )
    max_concurrent_agents: int = 5
    agent_timeout_seconds: int = 300


@dataclass
class TaskConfig:
    """Configuration for task processing."""

    max_queue_size: int = 1000
    max_concurrent_tasks: int = 10
    task_timeout_seconds: int = 600
    max_correction_iterations: int = 3


@dataclass
class ObservabilityConfig:
    """Configuration for observability features."""

    logging_level: str = "INFO"
    enable_metrics: bool = True
    enable_tracing: bool = True
    # Placeholder for external endpoints
    metrics_endpoint: str = "NOT_CONFIGURED"
    tracing_endpoint: str = "NOT_CONFIGURED"


@dataclass
class Config:
    """
    Main configuration for the orchestrator.

    Supports loading from environment variables and configuration files.
    """

    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    llm: LLMConfig = field(default_factory=LLMConfig)
    agents: AgentConfig = field(default_factory=AgentConfig)
    tasks: TaskConfig = field(default_factory=TaskConfig)
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)
    # Adapter enable flags (all disabled by default)
    enable_cli_adapter: bool = False
    enable_api_adapter: bool = False
    enable_vcs_adapter: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT


def load_config(config_path: str | Path | None = None) -> Config:
    """
    Load configuration from environment variables and optional config file.

    Args:
        config_path: Optional path to a configuration file.

    Returns:
        Config object with loaded settings.
    """
    config = Config()

    # Load from environment variables
    env = os.environ.get("ORCHESTRATOR_ENV", "development").lower()
    if env in [e.value for e in Environment]:
        config.environment = Environment(env)

    config.debug = os.environ.get("ORCHESTRATOR_DEBUG", "false").lower() == "true"

    # LLM config from environment
    config.llm.provider = os.environ.get("ORCHESTRATOR_LLM_PROVIDER", config.llm.provider)
    config.llm.model = os.environ.get("ORCHESTRATOR_LLM_MODEL", config.llm.model)

    max_tokens = os.environ.get("ORCHESTRATOR_LLM_MAX_TOKENS")
    if max_tokens:
        try:
            config.llm.max_tokens = int(max_tokens)
        except ValueError:
            pass

    temperature = os.environ.get("ORCHESTRATOR_LLM_TEMPERATURE")
    if temperature:
        try:
            config.llm.temperature = float(temperature)
        except ValueError:
            pass

    # Observability config from environment
    config.observability.logging_level = os.environ.get(
        "ORCHESTRATOR_LOG_LEVEL", config.observability.logging_level
    )
    config.observability.enable_metrics = (
        os.environ.get("ORCHESTRATOR_ENABLE_METRICS", "true").lower() == "true"
    )
    config.observability.enable_tracing = (
        os.environ.get("ORCHESTRATOR_ENABLE_TRACING", "true").lower() == "true"
    )

    # Adapter flags from environment
    config.enable_cli_adapter = (
        os.environ.get("ORCHESTRATOR_ENABLE_CLI_ADAPTER", "false").lower() == "true"
    )
    config.enable_api_adapter = (
        os.environ.get("ORCHESTRATOR_ENABLE_API_ADAPTER", "false").lower() == "true"
    )
    config.enable_vcs_adapter = (
        os.environ.get("ORCHESTRATOR_ENABLE_VCS_ADAPTER", "false").lower() == "true"
    )

    # TODO: Load from config file if provided
    # This is a placeholder for future implementation
    if config_path is not None:
        path = Path(config_path)
        if path.exists():
            # Future: Parse YAML/JSON/TOML config file
            config.metadata["config_file"] = str(path)

    return config


def get_default_config_paths() -> list[Path]:
    """
    Get the default configuration file search paths.

    Returns:
        List of paths to search for configuration files.
    """
    paths = [
        Path.cwd() / "orchestrator.yaml",
        Path.cwd() / "orchestrator.yml",
        Path.cwd() / "config" / "orchestrator.yaml",
        Path.home() / ".orchestrator" / "config.yaml",
    ]

    # Add XDG config path on Linux
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        paths.append(Path(xdg_config) / "orchestrator" / "config.yaml")
    else:
        paths.append(Path.home() / ".config" / "orchestrator" / "config.yaml")

    return paths
