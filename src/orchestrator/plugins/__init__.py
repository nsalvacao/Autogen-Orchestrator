"""
Plugin System - Extensibility framework for the orchestrator.
"""

from orchestrator.plugins.base import Plugin, PluginMetadata, PluginType
from orchestrator.plugins.manager import PluginManager

__all__ = [
    "Plugin",
    "PluginType",
    "PluginMetadata",
    "PluginManager",
]
