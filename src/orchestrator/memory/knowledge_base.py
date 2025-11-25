"""
Knowledge Base - Shared knowledge repository for agents.

This module implements a knowledge base that agents can use to
store and retrieve structured information, best practices,
and learned patterns.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class KnowledgeCategory(str, Enum):
    """Categories of knowledge."""

    TECHNICAL = "technical"  # Technical information
    DOMAIN = "domain"  # Domain-specific knowledge
    PROCESS = "process"  # Processes and procedures
    BEST_PRACTICE = "best_practice"  # Best practices
    PATTERN = "pattern"  # Design patterns
    CONVENTION = "convention"  # Coding conventions
    LESSON_LEARNED = "lesson_learned"  # Lessons from past experiences
    REFERENCE = "reference"  # Reference materials


@dataclass
class KnowledgeEntry:
    """A single knowledge entry."""

    title: str
    content: str
    category: KnowledgeCategory
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tags: list[str] = field(default_factory=list)
    source: str | None = None
    author: str | None = None
    references: list[str] = field(default_factory=list)  # Related entry IDs
    confidence: float = 1.0  # How confident we are in this knowledge
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, content: str, author: str | None = None) -> None:
        """Update the knowledge content."""
        self.content = content
        self.version += 1
        self.updated_at = datetime.now()
        if author:
            self.author = author

    def access(self) -> None:
        """Record an access to this knowledge."""
        self.access_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category": self.category.value,
            "tags": self.tags,
            "source": self.source,
            "author": self.author,
            "references": self.references,
            "confidence": self.confidence,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
        }


class KnowledgeBase:
    """
    Shared knowledge repository for agents.

    Provides functionality for storing, retrieving, and managing
    structured knowledge that can be shared across agents.
    """

    def __init__(self, name: str = "default"):
        """
        Initialize the knowledge base.

        Args:
            name: Name of this knowledge base.
        """
        self._name = name
        self._entries: dict[str, KnowledgeEntry] = {}
        self._category_index: dict[KnowledgeCategory, set[str]] = {}
        self._tag_index: dict[str, set[str]] = {}

    @property
    def name(self) -> str:
        """Return the knowledge base name."""
        return self._name

    def add(
        self,
        title: str,
        content: str,
        category: KnowledgeCategory,
        tags: list[str] | None = None,
        source: str | None = None,
        author: str | None = None,
        references: list[str] | None = None,
        confidence: float = 1.0,
    ) -> str:
        """
        Add a new knowledge entry.

        Args:
            title: Entry title.
            content: Entry content.
            category: Knowledge category.
            tags: Tags for categorization.
            source: Source of the knowledge.
            author: Author of the entry.
            references: Related entry IDs.
            confidence: Confidence score (0.0 to 1.0).

        Returns:
            The entry ID.
        """
        entry = KnowledgeEntry(
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            source=source,
            author=author,
            references=references or [],
            confidence=confidence,
        )

        self._entries[entry.id] = entry
        self._index_entry(entry)

        return entry.id

    def get(self, entry_id: str) -> KnowledgeEntry | None:
        """
        Get a specific knowledge entry.

        Args:
            entry_id: The entry ID.

        Returns:
            The knowledge entry, or None if not found.
        """
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
        return entry

    def search(
        self,
        query: str | None = None,
        category: KnowledgeCategory | None = None,
        tags: list[str] | None = None,
        min_confidence: float = 0.0,
        limit: int = 10,
    ) -> list[KnowledgeEntry]:
        """
        Search for knowledge entries.

        Args:
            query: Text to search for.
            category: Category to filter by.
            tags: Tags to filter by.
            min_confidence: Minimum confidence score.
            limit: Maximum number of results.

        Returns:
            List of matching entries.
        """
        results: list[KnowledgeEntry] = []

        # Start with category or tag filtered set
        if category:
            cat_ids = self._category_index.get(category, set())
            candidates = [
                self._entries[eid]
                for eid in cat_ids
                if eid in self._entries
            ]
        elif tags:
            tag_ids: set[str] = set()
            for tag in tags:
                if tag in self._tag_index:
                    tag_ids.update(self._tag_index[tag])
            candidates = [
                self._entries[eid]
                for eid in tag_ids
                if eid in self._entries
            ]
        else:
            candidates = list(self._entries.values())

        for entry in candidates:
            # Filter by confidence
            if entry.confidence < min_confidence:
                continue

            # Filter by query
            if query:
                query_lower = query.lower()
                if (
                    query_lower not in entry.title.lower()
                    and query_lower not in entry.content.lower()
                ):
                    continue

            # Filter by tags (if not already filtered)
            if tags and not category:
                if not any(tag in entry.tags for tag in tags):
                    continue

            results.append(entry)

        # Sort by relevance (access count and confidence)
        results.sort(
            key=lambda e: (e.confidence, e.access_count),
            reverse=True,
        )

        # Record access
        for entry in results[:limit]:
            entry.access()

        return results[:limit]

    def update(
        self,
        entry_id: str,
        content: str | None = None,
        tags: list[str] | None = None,
        confidence: float | None = None,
        author: str | None = None,
    ) -> bool:
        """
        Update a knowledge entry.

        Args:
            entry_id: The entry ID.
            content: New content (optional).
            tags: New tags (optional).
            confidence: New confidence score (optional).
            author: Author of the update.

        Returns:
            True if updated, False if not found.
        """
        entry = self._entries.get(entry_id)
        if not entry:
            return False

        if content:
            entry.update(content, author)

        if tags is not None:
            # Remove from old tag indices
            for tag in entry.tags:
                if tag in self._tag_index:
                    self._tag_index[tag].discard(entry_id)

            entry.tags = tags

            # Add to new tag indices
            for tag in tags:
                if tag not in self._tag_index:
                    self._tag_index[tag] = set()
                self._tag_index[tag].add(entry_id)

        if confidence is not None:
            entry.confidence = confidence

        entry.updated_at = datetime.now()
        return True

    def delete(self, entry_id: str) -> bool:
        """
        Delete a knowledge entry.

        Args:
            entry_id: The entry ID.

        Returns:
            True if deleted, False if not found.
        """
        if entry_id not in self._entries:
            return False

        entry = self._entries[entry_id]
        self._remove_from_indices(entry)
        del self._entries[entry_id]

        return True

    def add_reference(self, entry_id: str, reference_id: str) -> bool:
        """
        Add a reference between entries.

        Args:
            entry_id: The entry to add reference to.
            reference_id: The referenced entry ID.

        Returns:
            True if added, False if entry not found.
        """
        entry = self._entries.get(entry_id)
        if not entry:
            return False

        if reference_id not in entry.references:
            entry.references.append(reference_id)
            entry.updated_at = datetime.now()

        return True

    def get_by_category(self, category: KnowledgeCategory) -> list[KnowledgeEntry]:
        """Get all entries in a category."""
        entry_ids = self._category_index.get(category, set())
        return [
            self._entries[eid]
            for eid in entry_ids
            if eid in self._entries
        ]

    def get_by_tag(self, tag: str) -> list[KnowledgeEntry]:
        """Get all entries with a specific tag."""
        entry_ids = self._tag_index.get(tag, set())
        return [
            self._entries[eid]
            for eid in entry_ids
            if eid in self._entries
        ]

    def get_popular(self, limit: int = 10) -> list[KnowledgeEntry]:
        """Get the most accessed entries."""
        entries = list(self._entries.values())
        entries.sort(key=lambda e: e.access_count, reverse=True)
        return entries[:limit]

    def get_recent(self, limit: int = 10) -> list[KnowledgeEntry]:
        """Get recently updated entries."""
        entries = list(self._entries.values())
        entries.sort(key=lambda e: e.updated_at, reverse=True)
        return entries[:limit]

    def _index_entry(self, entry: KnowledgeEntry) -> None:
        """Add entry to indices."""
        # Category index
        if entry.category not in self._category_index:
            self._category_index[entry.category] = set()
        self._category_index[entry.category].add(entry.id)

        # Tag index
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry.id)

    def _remove_from_indices(self, entry: KnowledgeEntry) -> None:
        """Remove entry from indices."""
        # Category index
        if entry.category in self._category_index:
            self._category_index[entry.category].discard(entry.id)

        # Tag index
        for tag in entry.tags:
            if tag in self._tag_index:
                self._tag_index[tag].discard(entry.id)

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        category_counts = {
            cat.value: len(ids)
            for cat, ids in self._category_index.items()
        }

        return {
            "name": self._name,
            "total_entries": len(self._entries),
            "by_category": category_counts,
            "tags_count": len(self._tag_index),
        }

    def export(self) -> list[dict[str, Any]]:
        """Export all entries as dictionaries."""
        return [entry.to_dict() for entry in self._entries.values()]

    def clear(self) -> None:
        """Clear all knowledge entries."""
        self._entries.clear()
        self._category_index.clear()
        self._tag_index.clear()

    # Pre-built knowledge templates
    @classmethod
    def create_with_defaults(cls, name: str = "default") -> "KnowledgeBase":
        """Create a knowledge base with default best practices."""
        kb = cls(name)

        # Add some default best practices
        kb.add(
            title="Code Review Best Practices",
            content=(
                "1. Review for functionality, not just style\n"
                "2. Keep reviews small and focused\n"
                "3. Provide constructive feedback\n"
                "4. Check for security vulnerabilities\n"
                "5. Verify test coverage"
            ),
            category=KnowledgeCategory.BEST_PRACTICE,
            tags=["code_review", "development"],
            confidence=1.0,
        )

        kb.add(
            title="Error Handling Pattern",
            content=(
                "Use consistent error handling:\n"
                "- Define custom exception classes\n"
                "- Catch specific exceptions\n"
                "- Log errors with context\n"
                "- Provide meaningful error messages"
            ),
            category=KnowledgeCategory.PATTERN,
            tags=["error_handling", "patterns"],
            confidence=1.0,
        )

        kb.add(
            title="Testing Pyramid",
            content=(
                "Follow the testing pyramid:\n"
                "- Many unit tests (base)\n"
                "- Fewer integration tests (middle)\n"
                "- Few end-to-end tests (top)\n"
                "- Fast feedback from unit tests\n"
                "- Confidence from integration tests"
            ),
            category=KnowledgeCategory.BEST_PRACTICE,
            tags=["testing", "qa"],
            confidence=1.0,
        )

        return kb
