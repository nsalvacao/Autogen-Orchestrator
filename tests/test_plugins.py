"""Tests for plugin system."""

import pytest

from orchestrator.plugins.base import (
    Plugin,
    PluginMetadata,
    PluginType,
    ProcessorPlugin,
)
from orchestrator.plugins.manager import PluginManager


class SamplePlugin(Plugin):
    """Sample plugin for testing."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sample_plugin",
            version="1.0.0",
            description="A sample test plugin",
            author="Test",
            plugin_type=PluginType.PROCESSOR,
        )

    async def execute(self, context: dict) -> dict:
        return {"executed": True, "data": context.get("data")}


class DependentPlugin(Plugin):
    """Plugin that depends on SamplePlugin."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dependent_plugin",
            version="1.0.0",
            description="A plugin with dependencies",
            plugin_type=PluginType.PROCESSOR,
            dependencies=["sample_plugin"],
        )

    async def execute(self, context: dict) -> dict:
        return {"executed": True}


class SampleProcessorPlugin(ProcessorPlugin):
    """Sample processor plugin for testing."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sample_processor",
            version="1.0.0",
            description="A sample processor plugin",
            plugin_type=PluginType.PROCESSOR,
            enabled_by_default=True,
        )

    async def process(self, data, context: dict) -> str:
        return f"processed: {data}"


class TestPluginMetadata:
    """Tests for PluginMetadata."""

    def test_metadata_creation(self):
        """Test creating plugin metadata."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test description",
            author="Test Author",
            plugin_type=PluginType.ADAPTER,
        )

        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.plugin_type == PluginType.ADAPTER

    def test_metadata_to_dict(self):
        """Test metadata serialization."""
        metadata = PluginMetadata(
            name="test",
            version="1.0.0",
            description="Test",
            plugin_type=PluginType.HOOK,
        )

        data = metadata.to_dict()

        assert data["name"] == "test"
        assert data["plugin_type"] == "hook"


class TestPlugin:
    """Tests for Plugin base class."""

    @pytest.fixture
    def plugin(self):
        return SamplePlugin()

    def test_plugin_creation(self, plugin):
        """Test plugin creation."""
        assert plugin.metadata.name == "sample_plugin"
        assert plugin.is_enabled is False
        assert plugin.is_initialized is False

    @pytest.mark.asyncio
    async def test_plugin_initialize(self, plugin):
        """Test plugin initialization."""
        await plugin.initialize()

        assert plugin.is_initialized is True

    @pytest.mark.asyncio
    async def test_plugin_enable_disable(self, plugin):
        """Test enabling and disabling plugin."""
        await plugin.initialize()

        plugin.enable()
        assert plugin.is_enabled is True

        plugin.disable()
        assert plugin.is_enabled is False

    @pytest.mark.asyncio
    async def test_plugin_execute(self, plugin):
        """Test plugin execution."""
        await plugin.initialize()
        plugin.enable()

        result = await plugin.execute({"data": "test"})

        assert result["executed"] is True
        assert result["data"] == "test"

    def test_plugin_configure(self, plugin):
        """Test plugin configuration."""
        plugin.configure({"key": "value"})

        assert plugin.config["key"] == "value"

    @pytest.mark.asyncio
    async def test_plugin_shutdown(self, plugin):
        """Test plugin shutdown."""
        await plugin.initialize()
        plugin.enable()

        await plugin.shutdown()

        assert plugin.is_enabled is False
        assert plugin.is_initialized is False

    def test_plugin_get_status(self, plugin):
        """Test getting plugin status."""
        status = plugin.get_status()

        assert status["name"] == "sample_plugin"
        assert status["enabled"] is False


class TestPluginManager:
    """Tests for PluginManager."""

    @pytest.fixture
    def manager(self):
        return PluginManager()

    @pytest.mark.asyncio
    async def test_register_plugin(self, manager):
        """Test registering a plugin."""
        plugin = SamplePlugin()

        result = await manager.register(plugin)

        assert result is True
        assert manager.get("sample_plugin") is not None

    @pytest.mark.asyncio
    async def test_register_duplicate(self, manager):
        """Test registering duplicate plugin."""
        await manager.register(SamplePlugin())

        result = await manager.register(SamplePlugin())

        assert result is False

    @pytest.mark.asyncio
    async def test_register_with_dependencies(self, manager):
        """Test registering plugin with dependencies."""
        # Register dependency first
        await manager.register(SamplePlugin())

        # Now register dependent plugin
        result = await manager.register(DependentPlugin())

        assert result is True

    @pytest.mark.asyncio
    async def test_register_missing_dependency(self, manager):
        """Test registering plugin with missing dependency."""
        with pytest.raises(ValueError, match="requires"):
            await manager.register(DependentPlugin())

    @pytest.mark.asyncio
    async def test_unregister_plugin(self, manager):
        """Test unregistering a plugin."""
        await manager.register(SamplePlugin())

        result = await manager.unregister("sample_plugin")

        assert result is True
        assert manager.get("sample_plugin") is None

    @pytest.mark.asyncio
    async def test_unregister_with_dependents(self, manager):
        """Test unregistering plugin that others depend on."""
        await manager.register(SamplePlugin())
        await manager.register(DependentPlugin())

        with pytest.raises(ValueError, match="depends on it"):
            await manager.unregister("sample_plugin")

    @pytest.mark.asyncio
    async def test_get_by_type(self, manager):
        """Test getting plugins by type."""
        await manager.register(SamplePlugin())
        await manager.register(SampleProcessorPlugin())

        processors = manager.get_by_type(PluginType.PROCESSOR)

        assert len(processors) == 2

    @pytest.mark.asyncio
    async def test_enable_disable(self, manager):
        """Test enabling and disabling plugins."""
        plugin = SamplePlugin()
        await manager.register(plugin)

        manager.enable("sample_plugin")
        assert plugin.is_enabled is True

        manager.disable("sample_plugin")
        assert plugin.is_enabled is False

    @pytest.mark.asyncio
    async def test_execute_all(self, manager):
        """Test executing all plugins of a type."""
        await manager.register(SamplePlugin())
        await manager.register(SampleProcessorPlugin())

        manager.enable("sample_plugin")
        manager.enable("sample_processor")

        results = await manager.execute_all(
            PluginType.PROCESSOR,
            {"data": "test"},
        )

        assert len(results) == 2
        assert all(r["success"] for r in results)

    @pytest.mark.asyncio
    async def test_get_status(self, manager):
        """Test getting manager status."""
        await manager.register(SamplePlugin())
        manager.enable("sample_plugin")

        status = manager.get_status()

        assert status["total"] == 1
        assert status["enabled"] == 1

    @pytest.mark.asyncio
    async def test_list_plugins(self, manager):
        """Test listing plugins."""
        await manager.register(SamplePlugin())

        plugins = manager.list_plugins()

        assert len(plugins) == 1
        assert plugins[0]["name"] == "sample_plugin"

    @pytest.mark.asyncio
    async def test_shutdown_all(self, manager):
        """Test shutting down all plugins."""
        await manager.register(SamplePlugin())
        await manager.register(SampleProcessorPlugin())

        await manager.shutdown_all()

        assert len(manager.list_plugins()) == 0
