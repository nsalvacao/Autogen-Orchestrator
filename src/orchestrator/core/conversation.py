"""
Conversation - Manages dynamic multi-agent conversations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from orchestrator.contracts.agent_contract import AgentMessage, AgentResponse


class ConversationStatus(str, Enum):
    """Status of a conversation."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ConversationMode(str, Enum):
    """Mode of conversation."""

    SEQUENTIAL = "sequential"  # Agents speak in order
    ROUND_ROBIN = "round_robin"  # Cycle through agents
    DYNAMIC = "dynamic"  # Agents join based on need
    BROADCAST = "broadcast"  # Message to all agents


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    speaker: str
    message: AgentMessage
    response: AgentResponse | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Conversation:
    """
    Represents a multi-agent conversation.

    Conversations track the exchange of messages between agents
    and provide context for task-related discussions.
    """

    topic: str
    participants: list[str] = field(default_factory=list)
    mode: ConversationMode = ConversationMode.DYNAMIC
    status: ConversationStatus = ConversationStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    turns: list[ConversationTurn] = field(default_factory=list)
    task_id: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    max_turns: int = 50

    def add_participant(self, agent_name: str) -> None:
        """Add a participant to the conversation."""
        if agent_name not in self.participants:
            self.participants.append(agent_name)
            self.updated_at = datetime.now()

    def remove_participant(self, agent_name: str) -> None:
        """Remove a participant from the conversation."""
        if agent_name in self.participants:
            self.participants.remove(agent_name)
            self.updated_at = datetime.now()

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a turn to the conversation."""
        self.turns.append(turn)
        self.updated_at = datetime.now()

        if len(self.turns) >= self.max_turns:
            self.status = ConversationStatus.COMPLETED

    def get_history(self, last_n: int | None = None) -> list[ConversationTurn]:
        """
        Get conversation history.

        Args:
            last_n: Optional limit on number of turns to return.

        Returns:
            List of conversation turns.
        """
        if last_n is None:
            return self.turns.copy()
        return self.turns[-last_n:]

    def get_context_for_agent(self, agent_name: str) -> dict[str, Any]:
        """
        Get conversation context relevant to a specific agent.

        Args:
            agent_name: The name of the agent.

        Returns:
            Context dictionary for the agent.
        """
        return {
            "conversation_id": self.id,
            "topic": self.topic,
            "participants": self.participants,
            "turn_count": len(self.turns),
            "last_speaker": self.turns[-1].speaker if self.turns else None,
            "task_id": self.task_id,
            "history_summary": self._summarize_history(),
        }

    def _summarize_history(self) -> str:
        """Create a brief summary of conversation history."""
        if not self.turns:
            return "No conversation history."

        summary_parts = []
        for turn in self.turns[-5:]:  # Last 5 turns
            summary_parts.append(f"{turn.speaker}: {turn.message.content[:100]}...")

        return "\n".join(summary_parts)

    def is_active(self) -> bool:
        """Check if the conversation is active."""
        return self.status == ConversationStatus.ACTIVE

    def complete(self) -> None:
        """Mark the conversation as completed."""
        self.status = ConversationStatus.COMPLETED
        self.updated_at = datetime.now()


class ConversationManager:
    """
    Manages multiple conversations and handles message routing.
    """

    def __init__(self):
        self._conversations: dict[str, Conversation] = {}
        self._agent_conversations: dict[str, list[str]] = {}  # agent -> conversation IDs

    def create_conversation(
        self,
        topic: str,
        participants: list[str] | None = None,
        mode: ConversationMode = ConversationMode.DYNAMIC,
        task_id: str | None = None,
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            topic: The topic of the conversation.
            participants: Initial list of participants.
            mode: The conversation mode.
            task_id: Optional associated task ID.

        Returns:
            The created conversation.
        """
        conversation = Conversation(
            topic=topic,
            participants=participants or [],
            mode=mode,
            task_id=task_id,
        )

        self._conversations[conversation.id] = conversation

        for participant in conversation.participants:
            self._add_agent_to_conversation(participant, conversation.id)

        return conversation

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)

    def add_agent_to_conversation(
        self, agent_name: str, conversation_id: str
    ) -> bool:
        """
        Add an agent to an existing conversation.

        Args:
            agent_name: The name of the agent to add.
            conversation_id: The conversation ID.

        Returns:
            True if successful, False otherwise.
        """
        conversation = self._conversations.get(conversation_id)
        if conversation is None:
            return False

        conversation.add_participant(agent_name)
        self._add_agent_to_conversation(agent_name, conversation_id)
        return True

    def _add_agent_to_conversation(self, agent_name: str, conversation_id: str) -> None:
        """Internal method to track agent-conversation mapping."""
        if agent_name not in self._agent_conversations:
            self._agent_conversations[agent_name] = []

        if conversation_id not in self._agent_conversations[agent_name]:
            self._agent_conversations[agent_name].append(conversation_id)

    def get_agent_conversations(self, agent_name: str) -> list[Conversation]:
        """Get all conversations an agent is participating in."""
        conversation_ids = self._agent_conversations.get(agent_name, [])
        return [
            self._conversations[cid]
            for cid in conversation_ids
            if cid in self._conversations
        ]

    def get_active_conversations(self) -> list[Conversation]:
        """Get all active conversations."""
        return [
            conv
            for conv in self._conversations.values()
            if conv.status == ConversationStatus.ACTIVE
        ]

    def end_conversation(self, conversation_id: str) -> None:
        """End a conversation."""
        conversation = self._conversations.get(conversation_id)
        if conversation:
            conversation.complete()
