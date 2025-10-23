"""
Todo plugin configuration.
"""

from apps.plugins.base import PluginConfig


class TodoConfig(PluginConfig):
    """
    Configuration for the Todo plugin.
    """
    # Basic Django app configuration
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.todo"
    verbose_name = "Todo Plugin"

    # Plugin metadata
    plugin_name = "todo"
    plugin_version = "1.0.0"
    plugin_description = "Task management plugin with collaboration features"
    plugin_author = "Django Blog Application"

    # Plugin capabilities
    provides = ["tasks", "todo", "task_management"]
    requires = []

    # Plugin dependencies (if any)
    plugin_dependencies = []

    # Plugin-specific settings
    plugin_settings = {
        "default_priority": "medium",
        "allow_task_sharing": True,
        "max_title_length": 200,
        "enable_comments": True,
    }

    def ready(self):
        """Called when the plugin is ready."""
        super().ready()

        # Import and register signal handlers if needed
        try:
            from . import signals
        except ImportError:
            # No signals module, that's fine
            pass
