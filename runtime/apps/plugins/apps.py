"""
Django app configuration for the plugin system.
"""

from django.apps import AppConfig


class PluginsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.plugins"
    verbose_name = "Plugin System"

    def ready(self):
        """
        Called when the plugin system app is ready.
        """
        # Import the base plugin system to trigger registration
        from .base import PluginRegistry
        from .management.commands import list_plugins, validate_plugins

        # The plugin system is now ready to accept plugin registrations