"""
Plugin Manager - Manages plugin lifecycle and registration.

This module provides the infrastructure for loading, unloading,
and managing plugins in the orchestrator.
"""

from typing import Any

from orchestrator.plugins.base import Plugin, PluginType


class PluginManager:
    """
    Manages plugins for the orchestrator.

    Handles plugin registration, lifecycle management, and
    provides access to plugin functionality.
    """

    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: dict[str, Plugin] = {}
        self._type_index: dict[PluginType, list[str]] = {}
        self._hooks: dict[str, list[Plugin]] = {}

    async def register(self, plugin: Plugin) -> bool:
        """
        Register a plugin.

        Args:
            plugin: The plugin to register.

        Returns:
            True if registered successfully.
        """
        name = plugin.metadata.name

        if name in self._plugins:
            return False

        # Check dependencies
        for dep in plugin.metadata.dependencies:
            if dep not in self._plugins:
                raise ValueError(
                    f"Plugin '{name}' requires '{dep}' which is not registered"
                )

        self._plugins[name] = plugin

        # Index by type
        plugin_type = plugin.metadata.plugin_type
        if plugin_type not in self._type_index:
            self._type_index[plugin_type] = []
        self._type_index[plugin_type].append(name)

        # Initialize the plugin
        await plugin.initialize()

        # Auto-enable if configured
        if plugin.metadata.enabled_by_default:
            plugin.enable()

        return True

    async def unregister(self, plugin_name: str) -> bool:
        """
        Unregister a plugin.

        Args:
            plugin_name: Name of the plugin to unregister.

        Returns:
            True if unregistered successfully.
        """
        if plugin_name not in self._plugins:
            return False

        plugin = self._plugins[plugin_name]

        # Check if other plugins depend on this one
        for other_name, other_plugin in self._plugins.items():
            if plugin_name in other_plugin.metadata.dependencies:
                raise ValueError(
                    f"Cannot unregister '{plugin_name}': "
                    f"'{other_name}' depends on it"
                )

        # Shutdown the plugin
        await plugin.shutdown()

        # Remove from indices
        plugin_type = plugin.metadata.plugin_type
        if plugin_type in self._type_index:
            self._type_index[plugin_type].remove(plugin_name)

        del self._plugins[plugin_name]

        return True

    def get(self, plugin_name: str) -> Plugin | None:
        """
        Get a plugin by name.

        Args:
            plugin_name: The plugin name.

        Returns:
            The plugin, or None if not found.
        """
        return self._plugins.get(plugin_name)

    def get_by_type(self, plugin_type: PluginType) -> list[Plugin]:
        """
        Get all plugins of a specific type.

        Args:
            plugin_type: The plugin type.

        Returns:
            List of plugins.
        """
        names = self._type_index.get(plugin_type, [])
        return [self._plugins[name] for name in names if name in self._plugins]

    def get_enabled(self) -> list[Plugin]:
        """Get all enabled plugins."""
        return [p for p in self._plugins.values() if p.is_enabled]

    def enable(self, plugin_name: str) -> bool:
        """
        Enable a plugin.

        Args:
            plugin_name: The plugin name.

        Returns:
            True if enabled.
        """
        plugin = self._plugins.get(plugin_name)
        if plugin:
            plugin.enable()
            return True
        return False

    def disable(self, plugin_name: str) -> bool:
        """
        Disable a plugin.

        Args:
            plugin_name: The plugin name.

        Returns:
            True if disabled.
        """
        plugin = self._plugins.get(plugin_name)
        if plugin:
            plugin.disable()
            return True
        return False

    async def execute_all(
        self,
        plugin_type: PluginType,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Execute all enabled plugins of a type.

        Args:
            plugin_type: The plugin type.
            context: Execution context.

        Returns:
            List of execution results.
        """
        results = []
        for plugin in self.get_by_type(plugin_type):
            if plugin.is_enabled:
                try:
                    result = await plugin.execute(context)
                    results.append({
                        "plugin": plugin.metadata.name,
                        "success": True,
                        "result": result,
                    })
                except Exception as e:
                    results.append({
                        "plugin": plugin.metadata.name,
                        "success": False,
                        "error": str(e),
                    })
        return results

    async def trigger_hook(
        self,
        hook_type: str,
        payload: Any,
    ) -> Any:
        """
        Trigger hook plugins with an event.

        Args:
            hook_type: The type of hook event.
            payload: The event payload.

        Returns:
            Modified payload after all hooks.
        """
        context = {
            "hook_type": hook_type,
            "payload": payload,
        }

        current_payload = payload

        for plugin in self.get_by_type(PluginType.HOOK):
            if plugin.is_enabled:
                try:
                    result = await plugin.execute(context)
                    if "result" in result:
                        current_payload = result["result"]
                        context["payload"] = current_payload
                except Exception:
                    # Continue with other hooks even if one fails
                    pass

        return current_payload

    def configure(self, plugin_name: str, config: dict[str, Any]) -> bool:
        """
        Configure a plugin.

        Args:
            plugin_name: The plugin name.
            config: Configuration values.

        Returns:
            True if configured.
        """
        plugin = self._plugins.get(plugin_name)
        if plugin:
            plugin.configure(config)
            return True
        return False

    def get_status(self) -> dict[str, Any]:
        """Get status of all plugins."""
        return {
            "total": len(self._plugins),
            "enabled": len(self.get_enabled()),
            "by_type": {
                ptype.value: len(names)
                for ptype, names in self._type_index.items()
            },
            "plugins": [
                plugin.get_status()
                for plugin in self._plugins.values()
            ],
        }

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all registered plugins with metadata."""
        return [
            plugin.metadata.to_dict()
            for plugin in self._plugins.values()
        ]

    async def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for plugin in self._plugins.values():
            await plugin.shutdown()
        self._plugins.clear()
        self._type_index.clear()
