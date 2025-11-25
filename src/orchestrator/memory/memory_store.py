"""
Memory Store - Provides short-term and long-term memory for agents.

This module implements memory storage for agents, enabling them to
remember context, previous interactions, and learned information.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    """Types of memory entries."""

    SHORT_TERM = "short_term"  # Session-specific, ephemeral
    LONG_TERM = "long_term"  # Persistent across sessions
    EPISODIC = "episodic"  # Specific events or interactions
    SEMANTIC = "semantic"  # General knowledge and facts
    PROCEDURAL = "procedural"  # How to do things


@dataclass
class MemoryEntry:
    """A single memory entry."""

    content: str
    memory_type: MemoryType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: list[str] = field(default_factory=list)
    source: str | None = None  # Agent or system that created this memory
    context: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0 to 1.0
    access_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        """Check if the memory has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def access(self) -> None:
        """Record an access to this memory."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "tags": self.tags,
            "source": self.source,
            "context": self.context,
            "importance": self.importance,
            "access_count": self.access_count,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class MemoryStore:
    """
    Memory storage system for agents.

    Provides functionality for storing, retrieving, and managing
    different types of memories.
    """

    def __init__(
        self,
        owner: str | None = None,
        max_short_term: int = 100,
        max_long_term: int = 1000,
        short_term_ttl_hours: int = 24,
    ):
        """
        Initialize the memory store.

        Args:
            owner: The agent or system that owns this memory store.
            max_short_term: Maximum short-term memories to keep.
            max_long_term: Maximum long-term memories to keep.
            short_term_ttl_hours: Time-to-live for short-term memories in hours.
        """
        self._owner = owner
        self._max_short_term = max_short_term
        self._max_long_term = max_long_term
        self._short_term_ttl = timedelta(hours=short_term_ttl_hours)
        self._memories: dict[str, MemoryEntry] = {}
        self._tag_index: dict[str, set[str]] = {}  # tag -> memory IDs

    def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        tags: list[str] | None = None,
        source: str | None = None,
        context: dict[str, Any] | None = None,
        importance: float = 0.5,
    ) -> str:
        """
        Store a new memory.

        Args:
            content: The memory content.
            memory_type: Type of memory.
            tags: Tags for categorization and retrieval.
            source: Source of the memory.
            context: Additional context.
            importance: Importance score (0.0 to 1.0).

        Returns:
            The memory ID.
        """
        # Set expiration for short-term memories
        expires_at = None
        if memory_type == MemoryType.SHORT_TERM:
            expires_at = datetime.now() + self._short_term_ttl

        entry = MemoryEntry(
            content=content,
            memory_type=memory_type,
            tags=tags or [],
            source=source or self._owner,
            context=context or {},
            importance=importance,
            expires_at=expires_at,
        )

        self._memories[entry.id] = entry

        # Index by tags
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry.id)

        # Cleanup if limits exceeded
        self._enforce_limits()

        return entry.id

    def retrieve(self, memory_id: str) -> MemoryEntry | None:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The memory ID.

        Returns:
            The memory entry, or None if not found.
        """
        entry = self._memories.get(memory_id)
        if entry:
            if entry.is_expired():
                self.forget(memory_id)
                return None
            entry.access()
        return entry

    def search(
        self,
        query: str | None = None,
        tags: list[str] | None = None,
        memory_type: MemoryType | None = None,
        min_importance: float = 0.0,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """
        Search for memories.

        Args:
            query: Text to search for in content.
            tags: Tags to filter by.
            memory_type: Type of memory to filter by.
            min_importance: Minimum importance score.
            limit: Maximum number of results.

        Returns:
            List of matching memory entries.
        """
        results: list[MemoryEntry] = []

        # Start with tag-filtered set if tags provided
        if tags:
            candidate_ids: set[str] = set()
            for tag in tags:
                if tag in self._tag_index:
                    candidate_ids.update(self._tag_index[tag])
            candidates = [
                self._memories[mid]
                for mid in candidate_ids
                if mid in self._memories
            ]
        else:
            candidates = list(self._memories.values())

        for entry in candidates:
            # Skip expired memories
            if entry.is_expired():
                continue

            # Filter by type
            if memory_type and entry.memory_type != memory_type:
                continue

            # Filter by importance
            if entry.importance < min_importance:
                continue

            # Filter by query
            if query and query.lower() not in entry.content.lower():
                continue

            results.append(entry)

        # Sort by importance and recency
        results.sort(
            key=lambda e: (e.importance, e.last_accessed),
            reverse=True,
        )

        # Record access for returned memories
        for entry in results[:limit]:
            entry.access()

        return results[:limit]

    def forget(self, memory_id: str) -> bool:
        """
        Remove a memory.

        Args:
            memory_id: The memory ID to remove.

        Returns:
            True if removed, False if not found.
        """
        if memory_id not in self._memories:
            return False

        entry = self._memories[memory_id]

        # Remove from tag index
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(memory_id)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]

        del self._memories[memory_id]
        return True

    def promote_to_long_term(self, memory_id: str) -> bool:
        """
        Promote a short-term memory to long-term.

        Args:
            memory_id: The memory ID to promote.

        Returns:
            True if promoted, False if not found or already long-term.
        """
        entry = self._memories.get(memory_id)
        if not entry:
            return False

        if entry.memory_type == MemoryType.LONG_TERM:
            return False

        entry.memory_type = MemoryType.LONG_TERM
        entry.expires_at = None
        return True

    def consolidate(self) -> int:
        """
        Consolidate memories by removing expired and low-importance entries.

        Returns:
            Number of memories removed.
        """
        removed = 0
        expired_ids = []

        for memory_id, entry in self._memories.items():
            if entry.is_expired():
                expired_ids.append(memory_id)

        for memory_id in expired_ids:
            self.forget(memory_id)
            removed += 1

        return removed

    def get_recent(self, count: int = 10) -> list[MemoryEntry]:
        """
        Get the most recently accessed memories.

        Args:
            count: Number of memories to retrieve.

        Returns:
            List of recent memories.
        """
        all_memories = list(self._memories.values())
        all_memories.sort(key=lambda e: e.last_accessed, reverse=True)
        return all_memories[:count]

    def get_important(self, count: int = 10) -> list[MemoryEntry]:
        """
        Get the most important memories.

        Args:
            count: Number of memories to retrieve.

        Returns:
            List of important memories.
        """
        all_memories = list(self._memories.values())
        all_memories.sort(key=lambda e: e.importance, reverse=True)
        return all_memories[:count]

    def _enforce_limits(self) -> None:
        """Enforce memory limits by removing old entries."""
        short_term = [
            e for e in self._memories.values()
            if e.memory_type == MemoryType.SHORT_TERM
        ]
        long_term = [
            e for e in self._memories.values()
            if e.memory_type == MemoryType.LONG_TERM
        ]

        # Remove excess short-term memories
        if len(short_term) > self._max_short_term:
            short_term.sort(key=lambda e: (e.importance, e.last_accessed))
            for entry in short_term[: len(short_term) - self._max_short_term]:
                self.forget(entry.id)

        # Remove excess long-term memories
        if len(long_term) > self._max_long_term:
            long_term.sort(key=lambda e: (e.importance, e.access_count))
            for entry in long_term[: len(long_term) - self._max_long_term]:
                self.forget(entry.id)

    def get_stats(self) -> dict[str, Any]:
        """Get memory store statistics."""
        type_counts = {}
        for entry in self._memories.values():
            type_counts[entry.memory_type.value] = (
                type_counts.get(entry.memory_type.value, 0) + 1
            )

        return {
            "total_memories": len(self._memories),
            "by_type": type_counts,
            "tags_count": len(self._tag_index),
            "owner": self._owner,
        }

    def clear(self) -> None:
        """Clear all memories."""
        self._memories.clear()
        self._tag_index.clear()

    def export(self) -> list[dict[str, Any]]:
        """Export all memories as dictionaries."""
        return [entry.to_dict() for entry in self._memories.values()]
