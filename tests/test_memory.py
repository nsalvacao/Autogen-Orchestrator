"""Tests for memory module."""

import pytest

from orchestrator.memory.knowledge_base import KnowledgeBase, KnowledgeCategory
from orchestrator.memory.memory_store import MemoryEntry, MemoryStore, MemoryType


class TestMemoryEntry:
    """Tests for MemoryEntry."""

    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        entry = MemoryEntry(
            content="Test memory content",
            memory_type=MemoryType.SHORT_TERM,
            tags=["test", "example"],
        )

        assert entry.content == "Test memory content"
        assert entry.memory_type == MemoryType.SHORT_TERM
        assert "test" in entry.tags
        assert entry.id is not None

    def test_memory_access(self):
        """Test accessing a memory."""
        entry = MemoryEntry(
            content="Test",
            memory_type=MemoryType.SHORT_TERM,
        )

        initial_count = entry.access_count
        entry.access()

        assert entry.access_count == initial_count + 1

    def test_memory_to_dict(self):
        """Test memory serialization."""
        entry = MemoryEntry(
            content="Test",
            memory_type=MemoryType.LONG_TERM,
        )

        data = entry.to_dict()

        assert data["content"] == "Test"
        assert data["memory_type"] == "long_term"


class TestMemoryStore:
    """Tests for MemoryStore."""

    @pytest.fixture
    def store(self):
        return MemoryStore(owner="TestAgent")

    def test_store_creation(self, store):
        """Test store creation."""
        assert store is not None
        stats = store.get_stats()
        assert stats["total_memories"] == 0

    def test_store_memory(self, store):
        """Test storing a memory."""
        memory_id = store.store(
            content="Test memory",
            memory_type=MemoryType.SHORT_TERM,
            tags=["test"],
        )

        assert memory_id is not None
        stats = store.get_stats()
        assert stats["total_memories"] == 1

    def test_retrieve_memory(self, store):
        """Test retrieving a memory."""
        memory_id = store.store("Test content", MemoryType.SHORT_TERM)

        entry = store.retrieve(memory_id)

        assert entry is not None
        assert entry.content == "Test content"

    def test_search_by_query(self, store):
        """Test searching memories by query."""
        store.store("Python programming", MemoryType.SHORT_TERM, tags=["code"])
        store.store("JavaScript development", MemoryType.SHORT_TERM, tags=["code"])
        store.store("Database design", MemoryType.SHORT_TERM, tags=["data"])

        results = store.search(query="python")

        assert len(results) == 1
        assert "Python" in results[0].content

    def test_search_by_tags(self, store):
        """Test searching memories by tags."""
        store.store("Memory 1", MemoryType.SHORT_TERM, tags=["important"])
        store.store("Memory 2", MemoryType.SHORT_TERM, tags=["important"])
        store.store("Memory 3", MemoryType.SHORT_TERM, tags=["minor"])

        results = store.search(tags=["important"])

        assert len(results) == 2

    def test_search_by_type(self, store):
        """Test searching by memory type."""
        store.store("Short term", MemoryType.SHORT_TERM)
        store.store("Long term", MemoryType.LONG_TERM)

        results = store.search(memory_type=MemoryType.LONG_TERM)

        assert len(results) == 1
        assert results[0].content == "Long term"

    def test_forget_memory(self, store):
        """Test forgetting a memory."""
        memory_id = store.store("To forget", MemoryType.SHORT_TERM)

        result = store.forget(memory_id)

        assert result is True
        assert store.retrieve(memory_id) is None

    def test_promote_to_long_term(self, store):
        """Test promoting memory to long-term."""
        memory_id = store.store("Important", MemoryType.SHORT_TERM)

        result = store.promote_to_long_term(memory_id)

        assert result is True
        entry = store.retrieve(memory_id)
        assert entry.memory_type == MemoryType.LONG_TERM

    def test_get_recent(self, store):
        """Test getting recent memories."""
        store.store("First", MemoryType.SHORT_TERM)
        store.store("Second", MemoryType.SHORT_TERM)
        store.store("Third", MemoryType.SHORT_TERM)

        recent = store.get_recent(count=2)

        assert len(recent) == 2

    def test_get_important(self, store):
        """Test getting important memories."""
        store.store("Low importance", MemoryType.SHORT_TERM, importance=0.1)
        store.store("High importance", MemoryType.SHORT_TERM, importance=0.9)
        store.store("Medium importance", MemoryType.SHORT_TERM, importance=0.5)

        important = store.get_important(count=1)

        assert len(important) == 1
        assert important[0].content == "High importance"

    def test_clear(self, store):
        """Test clearing all memories."""
        store.store("Memory 1", MemoryType.SHORT_TERM)
        store.store("Memory 2", MemoryType.SHORT_TERM)

        store.clear()

        stats = store.get_stats()
        assert stats["total_memories"] == 0


class TestKnowledgeBase:
    """Tests for KnowledgeBase."""

    @pytest.fixture
    def kb(self):
        return KnowledgeBase(name="test")

    def test_kb_creation(self, kb):
        """Test knowledge base creation."""
        assert kb.name == "test"
        stats = kb.get_stats()
        assert stats["total_entries"] == 0

    def test_add_entry(self, kb):
        """Test adding knowledge entry."""
        entry_id = kb.add(
            title="Test Entry",
            content="Test content",
            category=KnowledgeCategory.TECHNICAL,
            tags=["test"],
        )

        assert entry_id is not None
        stats = kb.get_stats()
        assert stats["total_entries"] == 1

    def test_get_entry(self, kb):
        """Test getting a knowledge entry."""
        entry_id = kb.add(
            title="Test",
            content="Content",
            category=KnowledgeCategory.BEST_PRACTICE,
        )

        entry = kb.get(entry_id)

        assert entry is not None
        assert entry.title == "Test"

    def test_search_by_query(self, kb):
        """Test searching by query."""
        kb.add("Python Tips", "Python programming tips", KnowledgeCategory.TECHNICAL)
        kb.add("Java Guide", "Java development guide", KnowledgeCategory.TECHNICAL)

        results = kb.search(query="python")

        assert len(results) == 1
        assert "Python" in results[0].title

    def test_search_by_category(self, kb):
        """Test searching by category."""
        kb.add("Best Practice 1", "Content", KnowledgeCategory.BEST_PRACTICE)
        kb.add("Pattern 1", "Content", KnowledgeCategory.PATTERN)

        results = kb.search(category=KnowledgeCategory.BEST_PRACTICE)

        assert len(results) == 1

    def test_update_entry(self, kb):
        """Test updating an entry."""
        entry_id = kb.add("Title", "Old content", KnowledgeCategory.TECHNICAL)

        result = kb.update(entry_id, content="New content")

        assert result is True
        entry = kb.get(entry_id)
        assert entry.content == "New content"
        assert entry.version == 2

    def test_delete_entry(self, kb):
        """Test deleting an entry."""
        entry_id = kb.add("To delete", "Content", KnowledgeCategory.TECHNICAL)

        result = kb.delete(entry_id)

        assert result is True
        assert kb.get(entry_id) is None

    def test_get_by_category(self, kb):
        """Test getting entries by category."""
        kb.add("Entry 1", "Content", KnowledgeCategory.PATTERN)
        kb.add("Entry 2", "Content", KnowledgeCategory.PATTERN)
        kb.add("Entry 3", "Content", KnowledgeCategory.BEST_PRACTICE)

        patterns = kb.get_by_category(KnowledgeCategory.PATTERN)

        assert len(patterns) == 2

    def test_add_reference(self, kb):
        """Test adding references between entries."""
        entry1_id = kb.add("Entry 1", "Content", KnowledgeCategory.TECHNICAL)
        entry2_id = kb.add("Entry 2", "Content", KnowledgeCategory.TECHNICAL)

        result = kb.add_reference(entry1_id, entry2_id)

        assert result is True
        entry1 = kb.get(entry1_id)
        assert entry2_id in entry1.references

    def test_create_with_defaults(self):
        """Test creating KB with default entries."""
        kb = KnowledgeBase.create_with_defaults("default")

        stats = kb.get_stats()
        assert stats["total_entries"] > 0
