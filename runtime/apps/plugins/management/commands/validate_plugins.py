"""
Django management command to validate all registered plugins.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from apps.plugins.base import PluginRegistry, PluginManager
import importlib


class Command(BaseCommand):
    help = 'Validate all registered plugins and report issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plugin',
            type=str,
            help='Validate only a specific plugin'
        )
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Check if plugin URLs can be loaded'
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        plugins = PluginRegistry.get_all_plugins()

        if options.get('plugin'):
            plugin_name = options['plugin']
            if plugin_name not in plugins:
                raise CommandError(f"Plugin '{plugin_name}' not found")
            plugins = {plugin_name: plugins[plugin_name]}

        if not plugins:
            self.stdout.write(self.style.WARNING('No plugins to validate'))
            return

        self.stdout.write(self.style.SUCCESS('Validating Plugins:'))
        self.stdout.write('=' * 80)

        all_valid = True

        for plugin_name, plugin_config in plugins.items():
            self.stdout.write(f"\nValidating: {self.style.SUCCESS(plugin_name)}")
            plugin_valid = True

            # Check required attributes
            required_attrs = ['plugin_name', 'plugin_version']
            for attr in required_attrs:
                if not hasattr(plugin_config, attr):
                    self.stdout.write(f"  ❌ Missing required attribute: {attr}")
                    plugin_valid = False
                    all_valid = False
                else:
                    value = getattr(plugin_config, attr)
                    if not value:
                        self.stdout.write(f"  ❌ Empty required attribute: {attr}")
                        plugin_valid = False
                        all_valid = False

            # Check plugin module structure
            try:
                plugin_module = importlib.import_module(plugin_config.name)
                self.stdout.write(f"  ✅ Plugin module loads correctly")
            except ImportError as e:
                self.stdout.write(f"  ❌ Plugin module import failed: {e}")
                plugin_valid = False
                all_valid = False

            # Check models module
            try:
                models_module = importlib.import_module(f'{plugin_config.name}.models')
                self.stdout.write(f"  ✅ Models module available")
            except ImportError:
                self.stdout.write(f"  ⚠️  No models module (this may be intentional)")

            # Check views module
            try:
                views_module = importlib.import_module(f'{plugin_config.name}.views')
                self.stdout.write(f"  ✅ Views module available")
            except ImportError:
                self.stdout.write(f"  ⚠️  No views module (this may be intentional)")

            # Check URLs module if requested
            if options.get('check_urls'):
                try:
                    urls_module = importlib.import_module(f'{plugin_config.name}.urls')
                    if hasattr(urls_module, 'urlpatterns'):
                        self.stdout.write(f"  ✅ URLs module with patterns found")
                    else:
                        self.stdout.write(f"  ⚠️  URLs module exists but no patterns found")
                except ImportError:
                    self.stdout.write(f"  ⚠️  No URLs module (this may be intentional)")

            # Check admin module
            try:
                admin_module = importlib.import_module(f'{plugin_config.name}.admin')
                self.stdout.write(f"  ✅ Admin module available")
            except ImportError:
                self.stdout.write(f"  ⚠️  No admin module (this may be intentional)")

            if plugin_valid:
                self.stdout.write(f"  ✅ Plugin validation passed")
            else:
                self.stdout.write(f"  ❌ Plugin validation failed")

        # Dependency validation
        self.stdout.write(f"\n{self.style.SUCCESS('Checking Dependencies:')}")
        dependency_errors = PluginRegistry.validate_dependencies()
        if dependency_errors:
            for error in dependency_errors:
                self.stdout.write(f"  ❌ {error}")
                all_valid = False
        else:
            self.stdout.write("  ✅ All dependencies satisfied")

        # Summary
        if all_valid:
            self.stdout.write(f"\n{self.style.SUCCESS('All plugins validated successfully!')}")
        else:
            self.stdout.write(f"\n{self.style.ERROR('Some plugins failed validation')}")
            raise CommandError('Plugin validation failed')