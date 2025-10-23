"""
Django management command to list all registered plugins.
"""

from django.core.management.base import BaseCommand
from django.utils.text import Truncator
from apps.plugins.base import PluginRegistry


class Command(BaseCommand):
    help = 'List all registered plugins and their information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--capability',
            type=str,
            help='Filter plugins by capability they provide'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        plugins = PluginRegistry.get_all_plugins()

        if options.get('capability'):
            capability = options['capability']
            plugins = {
                name: config for name, config in plugins.items()
                if capability in getattr(config, 'provides', [])
            }
            if not plugins:
                self.stdout.write(
                    self.style.WARNING(f'No plugins found that provide capability: {capability}')
                )
                return

        if not plugins:
            self.stdout.write(self.style.WARNING('No plugins registered'))
            return

        self.stdout.write(self.style.SUCCESS('Registered Plugins:'))
        self.stdout.write('=' * 80)

        for plugin_name, plugin_config in plugins.items():
            # Basic info
            self.stdout.write(f"\n{self.style.SUCCESS(plugin_name)}")
            self.stdout.write(f"  Class: {plugin_config.__class__.__name__}")
            self.stdout.write(f"  Module: {plugin_config.name}")

            # Metadata
            version = getattr(plugin_config, 'plugin_version', 'N/A')
            description = getattr(plugin_config, 'plugin_description', 'No description')
            author = getattr(plugin_config, 'plugin_author', 'Unknown')

            self.stdout.write(f"  Version: {version}")
            self.stdout.write(f"  Author: {author}")
            self.stdout.write(f"  Description: {Truncator(description).chars(60)}")

            # Capabilities
            provides = getattr(plugin_config, 'provides', [])
            requires = getattr(plugin_config, 'requires', [])

            if provides:
                self.stdout.write(f"  Provides: {', '.join(provides)}")

            if requires:
                self.stdout.write(f"  Requires: {', '.join(requires)}")

            # Dependencies
            dependencies = getattr(plugin_config, 'plugin_dependencies', [])
            if dependencies:
                self.stdout.write(f"  Dependencies: {', '.join(dependencies)}")

        # Summary
        total_plugins = len(plugins)
        self.stdout.write(f"\n{self.style.SUCCESS(f'Total plugins: {total_plugins}')}")

        # Dependency validation
        errors = PluginRegistry.validate_dependencies()
        if errors:
            self.stdout.write(self.style.ERROR('\nDependency Issues:'))
            for error in errors:
                self.stdout.write(f"  - {error}")
        else:
            self.stdout.write(self.style.SUCCESS('\nAll dependencies satisfied'))