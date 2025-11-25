"""
Autogen Orchestrator - A modular AI meta-orchestrator MVP built on AutoGen.

This package provides a framework for orchestrating multiple AI agents
(PM, Dev, QA, Security, Docs) with dynamic conversations, task distribution,
evaluation, and correction loops.
"""

__version__ = "0.1.0"

from orchestrator.core.orchestrator import Orchestrator
from orchestrator.core.task import Task, TaskPriority, TaskStatus

__all__ = ["Orchestrator", "Task", "TaskStatus", "TaskPriority"]
