"""Tests for the Conversation and ConversationManager classes."""

import pytest

from orchestrator.contracts.agent_contract import AgentMessage
from orchestrator.core.conversation import (
    Conversation,
    ConversationManager,
    ConversationStatus,
    ConversationTurn,
)


class TestConversation:
    """Tests for the Conversation class."""

    def test_conversation_creation(self):
        """Test basic conversation creation."""
        conversation = Conversation(topic="Test Topic")

        assert conversation.topic == "Test Topic"
        assert conversation.status == ConversationStatus.ACTIVE
        assert len(conversation.participants) == 0
        assert len(conversation.turns) == 0

    def test_add_participant(self):
        """Test adding participants to a conversation."""
        conversation = Conversation(topic="Test")

        conversation.add_participant("Agent1")
        conversation.add_participant("Agent2")

        assert len(conversation.participants) == 2
        assert "Agent1" in conversation.participants
        assert "Agent2" in conversation.participants

    def test_add_participant_duplicate(self):
        """Test that duplicate participants are not added."""
        conversation = Conversation(topic="Test")

        conversation.add_participant("Agent1")
        conversation.add_participant("Agent1")

        assert len(conversation.participants) == 1

    def test_remove_participant(self):
        """Test removing participants from a conversation."""
        conversation = Conversation(
            topic="Test",
            participants=["Agent1", "Agent2"],
        )

        conversation.remove_participant("Agent1")

        assert len(conversation.participants) == 1
        assert "Agent1" not in conversation.participants

    def test_add_turn(self):
        """Test adding turns to a conversation."""
        conversation = Conversation(topic="Test")
        message = AgentMessage(
            sender="Agent1",
            recipient="Agent2",
            content="Hello",
        )
        turn = ConversationTurn(speaker="Agent1", message=message)

        conversation.add_turn(turn)

        assert len(conversation.turns) == 1
        assert conversation.turns[0].speaker == "Agent1"

    def test_get_history(self):
        """Test getting conversation history."""
        conversation = Conversation(topic="Test")

        for i in range(5):
            message = AgentMessage(
                sender=f"Agent{i}",
                recipient="All",
                content=f"Message {i}",
            )
            turn = ConversationTurn(speaker=f"Agent{i}", message=message)
            conversation.add_turn(turn)

        full_history = conversation.get_history()
        assert len(full_history) == 5

        limited_history = conversation.get_history(last_n=3)
        assert len(limited_history) == 3

    def test_get_context_for_agent(self):
        """Test getting context for a specific agent."""
        conversation = Conversation(
            topic="Test Topic",
            participants=["Agent1", "Agent2"],
            task_id="task-123",
        )

        context = conversation.get_context_for_agent("Agent1")

        assert context["topic"] == "Test Topic"
        assert context["task_id"] == "task-123"
        assert "Agent1" in context["participants"]

    def test_is_active(self):
        """Test checking if conversation is active."""
        conversation = Conversation(topic="Test")

        assert conversation.is_active() is True

        conversation.complete()

        assert conversation.is_active() is False

    def test_max_turns_completion(self):
        """Test that conversation completes when max turns reached."""
        conversation = Conversation(topic="Test", max_turns=3)

        for i in range(3):
            message = AgentMessage(
                sender="Agent",
                recipient="All",
                content=f"Message {i}",
            )
            turn = ConversationTurn(speaker="Agent", message=message)
            conversation.add_turn(turn)

        assert conversation.status == ConversationStatus.COMPLETED


class TestConversationManager:
    """Tests for the ConversationManager class."""

    @pytest.fixture
    def manager(self):
        return ConversationManager()

    def test_create_conversation(self, manager):
        """Test creating a conversation."""
        conversation = manager.create_conversation(
            topic="Test Topic",
            participants=["Agent1", "Agent2"],
        )

        assert conversation is not None
        assert conversation.topic == "Test Topic"

    def test_get_conversation(self, manager):
        """Test retrieving a conversation."""
        created = manager.create_conversation(topic="Test")
        retrieved = manager.get_conversation(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_conversation(self, manager):
        """Test retrieving a nonexistent conversation."""
        retrieved = manager.get_conversation("nonexistent-id")
        assert retrieved is None

    def test_add_agent_to_conversation(self, manager):
        """Test adding an agent to an existing conversation."""
        conversation = manager.create_conversation(topic="Test")

        success = manager.add_agent_to_conversation("Agent1", conversation.id)

        assert success is True
        assert "Agent1" in conversation.participants

    def test_add_agent_to_nonexistent_conversation(self, manager):
        """Test adding an agent to a nonexistent conversation."""
        success = manager.add_agent_to_conversation("Agent1", "nonexistent-id")
        assert success is False

    def test_get_agent_conversations(self, manager):
        """Test getting all conversations for an agent."""
        manager.create_conversation(
            topic="Conv 1",
            participants=["Agent1"],
        )
        manager.create_conversation(
            topic="Conv 2",
            participants=["Agent1", "Agent2"],
        )
        manager.create_conversation(
            topic="Conv 3",
            participants=["Agent2"],
        )

        agent1_convs = manager.get_agent_conversations("Agent1")

        assert len(agent1_convs) == 2

    def test_get_active_conversations(self, manager):
        """Test getting all active conversations."""
        conv1 = manager.create_conversation(topic="Active 1")
        manager.create_conversation(topic="Active 2")

        active = manager.get_active_conversations()
        assert len(active) == 2

        manager.end_conversation(conv1.id)

        active = manager.get_active_conversations()
        assert len(active) == 1

    def test_end_conversation(self, manager):
        """Test ending a conversation."""
        conversation = manager.create_conversation(topic="Test")

        manager.end_conversation(conversation.id)

        assert conversation.status == ConversationStatus.COMPLETED
