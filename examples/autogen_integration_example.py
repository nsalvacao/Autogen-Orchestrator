#!/usr/bin/env python
"""
AutoGen Integration Example

This example demonstrates how to use the Autogen Orchestrator with
AutoGen LLM integration enabled for intelligent, AI-powered agent responses.

To use this example:
1. Set ORCHESTRATOR_LLM_API_KEY environment variable with your OpenAI API key
2. Optionally set ORCHESTRATOR_LLM_MODEL (default: gpt-4)
3. Run: python examples/autogen_integration_example.py

Note: AutoGen integration requires a valid OpenAI API key. Without it,
agents will fall back to rule-based responses.
"""

import asyncio
import os

from orchestrator import Orchestrator, Task, TaskPriority
from orchestrator.agents import (
    ArchitectAgent,
    DataAgent,
    DevAgent,
    DevOpsAgent,
    DocsAgent,
    PMAgent,
    QAAgent,
    ResearchAgent,
    SecurityAgent,
)
from orchestrator.core.task import TaskType


async def main():
    """Run the AutoGen integration example."""
    print("=" * 70)
    print("Autogen Orchestrator - AutoGen LLM Integration Example")
    print("=" * 70)
    print()

    # Check if AutoGen is configured
    api_key = os.environ.get("ORCHESTRATOR_LLM_API_KEY")
    if api_key:
        print("✓ AutoGen LLM integration is ENABLED")
        print(f"  Model: {os.environ.get('ORCHESTRATOR_LLM_MODEL', 'gpt-4')}")
        enable_autogen = True
    else:
        print("✗ AutoGen LLM integration is DISABLED (no API key)")
        print("  Agents will use rule-based responses")
        print("  To enable: export ORCHESTRATOR_LLM_API_KEY=your_key")
        enable_autogen = False

    print()

    # Create the orchestrator
    orchestrator = Orchestrator()

    # Register agents with AutoGen enabled/disabled
    agents = [
        PMAgent(enable_autogen=enable_autogen),
        DevAgent(enable_autogen=enable_autogen),
        QAAgent(enable_autogen=enable_autogen),
        SecurityAgent(enable_autogen=enable_autogen),
        DocsAgent(enable_autogen=enable_autogen),
        ArchitectAgent(enable_autogen=enable_autogen),
        ResearchAgent(enable_autogen=enable_autogen),
        DevOpsAgent(enable_autogen=enable_autogen),
        DataAgent(enable_autogen=enable_autogen),
    ]

    for agent in agents:
        orchestrator.register_agent(agent)
        autogen_status = "AutoGen" if agent.is_autogen_enabled else "Rule-based"
        print(f"  Registered: {agent.name} ({autogen_status})")

    print()

    # Start the orchestrator
    await orchestrator.start()
    print("Orchestrator started!")
    print()

    # Example 1: Architecture Design Task
    print("-" * 70)
    print("Example 1: System Architecture Design")
    print("-" * 70)
    
    arch_task = Task(
        title="Design Microservices Architecture",
        description=(
            "Design a scalable microservices architecture for an e-commerce platform. "
            "The system should handle user management, product catalog, shopping cart, "
            "order processing, and payment integration. Consider high availability, "
            "fault tolerance, and security."
        ),
        task_type=TaskType.PLANNING,
        priority=TaskPriority.HIGH,
    )

    task_id = await orchestrator.submit_task(arch_task)
    result = await orchestrator.process_task(arch_task)
    
    print(f"Task: {arch_task.title}")
    print(f"Assigned to: {arch_task.assigned_agent}")
    print(f"Result:\n{result.output[:500]}...")
    print()

    # Example 2: Development Task with AI Guidance
    print("-" * 70)
    print("Example 2: Feature Implementation with AI Guidance")
    print("-" * 70)
    
    dev_task = Task(
        title="Implement User Authentication System",
        description=(
            "Implement a secure user authentication system with JWT tokens, "
            "password hashing (bcrypt), email verification, and password reset. "
            "Include rate limiting for login attempts and session management."
        ),
        task_type=TaskType.DEVELOPMENT,
        priority=TaskPriority.HIGH,
    )

    task_id = await orchestrator.submit_task(dev_task)
    result = await orchestrator.process_task(dev_task)
    
    print(f"Task: {dev_task.title}")
    print(f"Assigned to: {dev_task.assigned_agent}")
    print(f"Result:\n{result.output[:500]}...")
    print()

    # Example 3: Security Review with AI Analysis
    print("-" * 70)
    print("Example 3: Security Review with AI Analysis")
    print("-" * 70)
    
    security_task = Task(
        title="Security Audit: Payment Processing Module",
        description=(
            "Perform a comprehensive security audit of the payment processing module. "
            "Review for OWASP Top 10 vulnerabilities, PCI-DSS compliance, "
            "input validation, encryption, and secure API design."
        ),
        task_type=TaskType.SECURITY_REVIEW,
        priority=TaskPriority.CRITICAL,
    )

    task_id = await orchestrator.submit_task(security_task)
    result = await orchestrator.process_task(security_task)
    
    print(f"Task: {security_task.title}")
    print(f"Assigned to: {security_task.assigned_agent}")
    print(f"Result:\n{result.output[:500]}...")
    print()

    # Example 4: Research Task
    print("-" * 70)
    print("Example 4: Technology Research")
    print("-" * 70)
    
    research_task = Task(
        title="Research Modern API Gateway Solutions",
        description=(
            "Research and compare modern API gateway solutions including Kong, "
            "AWS API Gateway, Azure API Management, and Apigee. Consider features, "
            "pricing, performance, and integration capabilities."
        ),
        task_type=TaskType.PLANNING,
        priority=TaskPriority.MEDIUM,
    )

    task_id = await orchestrator.submit_task(research_task)
    result = await orchestrator.process_task(research_task)
    
    print(f"Task: {research_task.title}")
    print(f"Assigned to: {research_task.assigned_agent}")
    print(f"Result:\n{result.output[:500]}...")
    print()

    # Show orchestrator statistics
    print("-" * 70)
    print("Orchestrator Statistics")
    print("-" * 70)
    status = orchestrator.get_status()
    print(f"  Total agents: {status['agents_count']}")
    print(f"  Completed tasks: {status.get('completed_tasks', 0)}")
    print(f"  AutoGen enabled: {'Yes' if enable_autogen else 'No'}")
    print()

    # Shutdown
    await orchestrator.shutdown()
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
