"""
Base plugin system for the Django application.
"""

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured
from django.urls import include, path
from django.utils.module_loading import autodiscover_modules
import importlib
from typing import Dict, List, Optional, Type


class PluginConfig(AppConfig):
    """
    Base configuration class for plugins.
    """
    # Plugin metadata
    plugin_name: str = ""
    plugin_version: str = "1.0.0"
    plugin_description: str = ""
    plugin_author: str = ""
    plugin_dependencies: List[str] = []

    # Plugin capabilities
    provides: List[str] = []
    requires: List[str] = []

    # Plugin configuration
    plugin_settings: Dict = {}

    def ready(self):
        """Called when the plugin is ready."""
        super().ready()
        # Register the plugin
        PluginRegistry.register(self)


class PluginRegistry:
    """
    Registry for managing plugins.
    """
    _plugins: Dict[str, PluginConfig] = {}
    _loaded_plugins: Dict[str, Type] = {}

    @classmethod
    def register(cls, plugin_config: PluginConfig):
        """Register a plugin."""
        plugin_name = getattr(plugin_config, 'plugin_name', plugin_config.name)
        cls._plugins[plugin_name] = plugin_config

    @classmethod
    def get_plugin(cls, name: str) -> Optional[PluginConfig]:
        """Get a plugin by name."""
        return cls._plugins.get(name)

    @classmethod
    def get_all_plugins(cls) -> Dict[str, PluginConfig]:
        """Get all registered plugins."""
        return cls._plugins.copy()

    @classmethod
    def get_plugins_by_capability(cls, capability: str) -> List[PluginConfig]:
        """Get all plugins that provide a specific capability."""
        return [
            plugin for plugin in cls._plugins.values()
            if capability in getattr(plugin, 'provides', [])
        ]

    @classmethod
    def validate_dependencies(cls) -> List[str]:
        """Validate plugin dependencies and return list of errors."""
        errors = []

        for plugin_name, plugin_config in cls._plugins.items():
            dependencies = getattr(plugin_config, 'plugin_dependencies', [])

            for dep in dependencies:
                if dep not in cls._plugins:
                    errors.append(f"Plugin '{plugin_name}' requires '{dep}' but it's not available")

        return errors


class PluginManager:
    """
    Manager for plugin operations.
    """

    @staticmethod
    def load_plugin_urls() -> List:
        """
        Load URLs from all registered plugins.
        """
        url_patterns = []

        for plugin_config in PluginRegistry.get_all_plugins().values():
            try:
                # Try to import urls module from the plugin
                plugin_name = plugin_config.name.split('.')[-1]
                urls_module = importlib.import_module(f'{plugin_name}.urls')

                if hasattr(urls_module, 'urlpatterns'):
                    # Create namespaced URLs for the plugin
                    namespace = getattr(urls_module, 'app_name', plugin_name)
                    url_patterns.append(
                        path(f'{plugin_name}/', include((urls_module.urlpatterns, namespace)))
                    )

            except ImportError:
                # Plugin doesn't have URLs, that's fine
                pass
            except Exception as e:
                # Log the error but don't crash
                print(f"Error loading URLs for plugin {plugin_config.name}: {e}")

        return url_patterns

    @staticmethod
    def get_plugin_settings(plugin_name: str) -> Dict:
        """Get settings for a specific plugin."""
        plugin_config = PluginRegistry.get_plugin(plugin_name)
        if plugin_config:
            return getattr(plugin_config, 'plugin_settings', {})
        return {}

    @staticmethod
    def is_plugin_enabled(plugin_name: str) -> bool:
        """Check if a plugin is enabled."""
        return PluginRegistry.get_plugin(plugin_name) is not None


def autodiscover_plugins():
    """
    Auto-discover and load plugins.
    """
    autodiscover_modules('plugins', register_to=True)