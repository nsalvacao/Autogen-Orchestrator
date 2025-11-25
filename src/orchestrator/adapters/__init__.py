"""
Adapters module - Contains adapter implementations for external systems.

Adapters provide integration points for external tools, APIs, and services.
These are placeholder implementations for future integrations.
"""

from orchestrator.adapters.api_adapter import APIAdapter
from orchestrator.adapters.cli_adapter import CLIAdapter
from orchestrator.adapters.vcs_adapter import VCSAdapter

__all__ = [
    "CLIAdapter",
    "APIAdapter",
    "VCSAdapter",
]
