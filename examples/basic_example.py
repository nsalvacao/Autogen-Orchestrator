#!/usr/bin/env python
"""
Basic Orchestrator Example

This example demonstrates the basic usage of the Autogen Orchestrator,
including agent registration, task submission, and conversation management.
"""

import asyncio

from orchestrator import Orchestrator, Task, TaskPriority
from orchestrator.agents import DevAgent, DocsAgent, PMAgent, QAAgent, SecurityAgent
from orchestrator.core.conversation import ConversationMode
from orchestrator.core.task import TaskType


async def main():
    """Run the basic orchestrator example."""
    print("=" * 60)
    print("Autogen Orchestrator - Basic Example")
    print("=" * 60)

    # Create the orchestrator
    orchestrator = Orchestrator()

    # Register all agents
    agents = [
        PMAgent(),
        DevAgent(),
        QAAgent(),
        SecurityAgent(),
        DocsAgent(),
    ]

    for agent in agents:
        orchestrator.register_agent(agent)
        print(f"Registered agent: {agent.name} - {agent.description[:50]}...")

    print()

    # Start the orchestrator
    await orchestrator.start()
    print("Orchestrator started successfully!")
    print()

    # Show orchestrator status
    status = orchestrator.get_status()
    print(f"Orchestrator Status:")
    print(f"  - Name: {status['name']}")
    print(f"  - Running: {status['is_running']}")
    print(f"  - Agents: {status['agents_count']}")
    print()

    # Create and submit a development task
    print("Creating a development task...")
    dev_task = Task(
        title="Implement User Authentication",
        description="Create a secure user authentication module with JWT tokens",
        task_type=TaskType.DEVELOPMENT,
        priority=TaskPriority.HIGH,
    )

    task_id = await orchestrator.submit_task(dev_task)
    print(f"Task submitted with ID: {task_id}")
    print()

    # Process the task
    print("Processing the task...")
    result = await orchestrator.process_task(dev_task)
    print(f"Task completed:")
    print(f"  - Success: {result.success}")
    print(f"  - Assigned to: {dev_task.assigned_agent}")
    if result.output:
        print(f"  - Output: {result.output[:100]}...")
    print()

    # Create a conversation between agents
    print("Creating a multi-agent conversation...")
    conversation = await orchestrator.create_conversation(
        topic="Feature Implementation Review",
        participant_names=["PMAgent", "DevAgent", "QAAgent"],
        mode=ConversationMode.DYNAMIC,
        task_id=task_id,
    )
    print(f"Conversation created: {conversation.id}")
    print(f"  - Topic: {conversation.topic}")
    print(f"  - Participants: {conversation.participants}")
    print()

    # Send a message in the conversation
    print("Sending a message from PM to Dev...")
    response = await orchestrator.send_message(
        conversation_id=conversation.id,
        sender="PMAgent",
        recipient="DevAgent",
        content="Please provide an update on the authentication module implementation.",
    )
    if response:
        print(f"Response from {response.agent_name}:")
        print(f"  {response.content[:150]}...")
    print()

    # Create additional tasks with dependencies
    print("Creating related tasks...")
    test_task = Task(
        title="Test Authentication Module",
        description="Write comprehensive tests for the authentication module",
        task_type=TaskType.TESTING,
        priority=TaskPriority.MEDIUM,
        dependencies=[task_id],
    )

    security_task = Task(
        title="Security Review",
        description="Perform security analysis on the authentication implementation",
        task_type=TaskType.SECURITY_REVIEW,
        priority=TaskPriority.HIGH,
        dependencies=[task_id],
    )

    doc_task = Task(
        title="API Documentation",
        description="Document the authentication API endpoints",
        task_type=TaskType.DOCUMENTATION,
        priority=TaskPriority.LOW,
        dependencies=[task_id],
    )

    await orchestrator.submit_task(test_task)
    await orchestrator.submit_task(security_task)
    await orchestrator.submit_task(doc_task)

    print(f"Submitted 3 additional tasks")
    print()

    # Show final status
    final_status = orchestrator.get_status()
    print("Final Orchestrator Status:")
    print(f"  - Pending tasks: {final_status['pending_tasks']}")
    print(f"  - Active conversations: {final_status['active_conversations']}")
    print()

    # Shutdown the orchestrator
    await orchestrator.shutdown()
    print("Orchestrator shutdown complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
