"""
Django management command for database operations.
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from utils.database import DatabaseManager, DatabaseBackup, DatabaseHealthChecker
import json
import os


class Command(BaseCommand):
    help = 'Perform various database operations for PostgreSQL'

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest='operation', help='Database operation to perform')

        # Info command
        info_parser = subparsers.add_parser('info', help='Show database information')
        info_parser.add_argument('--format', choices=['json', 'table'], default='table', help='Output format')

        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show database statistics')

        # Backup command
        backup_parser = subparsers.add_parser('backup', help='Create database backup')
        backup_parser.add_argument('--path', help='Backup file path')
        backup_parser.add_argument('--compress', action='store_true', help='Compress backup')

        # Restore command
        restore_parser = subparsers.add_parser('restore', help='Restore database from backup')
        restore_parser.add_argument('path', help='Backup file path')

        # Health check command
        health_parser = subparsers.add_parser('health', help='Check database health')

        # Query command
        query_parser = subparsers.add_parser('query', help='Execute custom query')
        query_parser.add_argument('query', help='SQL query to execute')
        query_parser.add_argument('--analyze', action='store_true', help='Analyze query performance')

        # Optimize command
        optimize_parser = subparsers.add_parser('optimize', help='Optimize database tables')
        optimize_parser.add_argument('--table', help='Specific table to optimize (optional)')

        # Tables command
        tables_parser = subparsers.add_parser('tables', help='Show table information')

        # Indexes command
        indexes_parser = subparsers.add_parser('indexes', help='Show index usage statistics')

        # Setup command for Docker
        setup_parser = subparsers.add_parser('setup', help='Setup database for Docker environment')
        setup_parser.add_argument('--create-user', action='store_true', help='Create database user')
        setup_parser.add_argument('--create-db', action='store_true', help='Create database')

    def handle(self, *args, **options):
        operation = options.get('operation')

        if operation == 'info':
            self.show_database_info(options)
        elif operation == 'stats':
            self.show_database_stats()
        elif operation == 'backup':
            self.create_backup(options)
        elif operation == 'restore':
            self.restore_backup(options)
        elif operation == 'health':
            self.check_health()
        elif operation == 'query':
            self.execute_query(options)
        elif operation == 'optimize':
            self.optimize_database(options)
        elif operation == 'tables':
            self.show_tables()
        elif operation == 'indexes':
            self.show_indexes()
        elif operation == 'setup':
            self.setup_docker_environment(options)
        else:
            self.print_help('manage.py', 'db_ops')

    def show_database_info(self, options):
        """Show database information."""
        info = DatabaseManager.get_database_info()

        if options.get('format') == 'json':
            self.stdout.write(json.dumps(info, indent=2))
        else:
            self.stdout.write(self.style.SUCCESS('Database Information:'))
            self.stdout.write(f"  Engine: {info['engine']}")
            self.stdout.write(f"  Name: {info['name']}")
            self.stdout.write(f"  Host: {info['host']}")
            self.stdout.write(f"  Port: {info['port']}")
            self.stdout.write(f"  Vendor: {info['vendor']}")

            if 'version' in info:
                self.stdout.write(f"  Version: {info['version']}")
            if 'size' in info:
                self.stdout.write(f"  Size: {info['size']}")
            if 'active_connections' in info:
                self.stdout.write(f"  Active Connections: {info['active_connections']}")
                self.stdout.write(f"  Max Connections: {info['max_connections']}")

    def show_database_stats(self):
        """Show comprehensive database statistics."""
        stats = DatabaseHealthChecker.get_database_stats()

        self.stdout.write(self.style.SUCCESS('Database Statistics:'))

        # Connection status
        connection = stats['connection']
        status_color = self.style.SUCCESS if connection['status'] == 'healthy' else self.style.ERROR
        self.stdout.write(f"  Connection: {status_color(connection['status'])}")

        # Table information
        tables = stats['tables']
        self.stdout.write(f"  Tables: {len(tables)}")
        if tables:
            self.stdout.write("  Table Details:")
            for table in tables[:10]:  # Show first 10 tables
                if 'total_bytes' in table:
                    size_mb = table['total_bytes'] / 1024 / 1024
                    self.stdout.write(f"    - {table['tablename']}: {size_mb:.2f} MB")
                else:
                    self.stdout.write(f"    - {table['tablename']}: {table.get('row_count', 'N/A')} rows")

        # Index usage (PostgreSQL only)
        if 'index_usage' in stats:
            indexes = stats['index_usage']
            self.stdout.write(f"  Indexes: {len(indexes)}")
            if indexes:
                self.stdout.write("  Top Used Indexes:")
                for idx in indexes[:5]:
                    self.stdout.write(f"    - {idx['indexname']}: {idx['idx_scan']} scans")

        # Slow queries (PostgreSQL only)
        if 'slow_queries' in stats:
            slow_queries = stats['slow_queries']
            if slow_queries and 'error' not in slow_queries[0]:
                self.stdout.write(f"  Slow Queries: {len(slow_queries)}")
                for query in slow_queries[:3]:
                    self.stdout.write(f"    - Avg time: {query['mean_time']:.2f}ms")

    def create_backup(self, options):
        """Create database backup."""
        backup_path = options.get('path')

        self.stdout.write(self.style.WARNING('Creating database backup...'))
        result = DatabaseBackup.create_backup(backup_path)

        if result['success']:
            self.stdout.write(self.style.SUCCESS(
                f"Backup created: {result['backup_path']} ({result['file_size']} bytes)"
            ))
        else:
            self.stdout.write(self.style.ERROR(f"Backup failed: {result.get('error', 'Unknown error')}"))

    def restore_backup(self, options):
        """Restore database from backup."""
        backup_path = options['path']

        if not os.path.exists(backup_path):
            raise CommandError(f"Backup file not found: {backup_path}")

        # Confirm restoration
        confirm = input(f"Are you sure you want to restore from {backup_path}? [y/N]: ")
        if confirm.lower() != 'y':
            self.stdout.write(self.style.WARNING('Restore cancelled'))
            return

        self.stdout.write(self.style.WARNING('Restoring database backup...'))
        result = DatabaseBackup.restore_backup(backup_path)

        if result['success']:
            self.stdout.write(self.style.SUCCESS(result['message']))
        else:
            self.stdout.write(self.style.ERROR(f"Restore failed: {result.get('error', 'Unknown error')}"))

    def check_health(self):
        """Check database health."""
        self.stdout.write(self.style.SUCCESS('Checking database health...'))

        # Connection check
        connection = DatabaseHealthChecker.check_connection()
        status_color = self.style.SUCCESS if connection['status'] == 'healthy' else self.style.ERROR
        self.stdout.write(f"  Connection: {status_color(connection['status'])}")

        # Integrity check (SQLite only)
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            integrity = DatabaseHealthChecker.check_table_integrity()
            if integrity['status'] == 'ok':
                self.stdout.write(f"  Integrity: {self.style.SUCCESS('OK')}")
            else:
                self.stdout.write(f"  Integrity: {self.style.ERROR(integrity.get('message', 'Unknown'))}")

    def execute_query(self, options):
        """Execute custom query."""
        query = options['query']
        analyze = options.get('analyze', False)

        if analyze and 'postgresql' in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.SUCCESS('Analyzing query...'))
            analysis = DatabaseManager.analyze_query_performance(query)

            if 'error' in analysis:
                self.stdout.write(self.style.ERROR(f"Analysis failed: {analysis['error']}"))
            else:
                self.stdout.write(f"  Execution Time: {analysis['execution_time']:.2f}ms")
                self.stdout.write(f"  Planning Time: {analysis['planning_time']:.2f}ms")
                self.stdout.write(f"  Actual Rows: {analysis['actual_rows']}")

        self.stdout.write(self.style.SUCCESS('Executing query...'))
        try:
            results = DatabaseManager.execute_raw_query(query)

            if isinstance(results, list):
                self.stdout.write(f"  Rows returned: {len(results)}")
                if results:
                    # Print headers
                    headers = list(results[0].keys())
                    self.stdout.write("  " + " | ".join(headers))
                    self.stdout.write("  " + "-+-".join(["-" * len(h) for h in headers]))

                    # Print first few rows
                    for row in results[:10]:
                        values = [str(row.get(h, '')) for h in headers]
                        self.stdout.write("  " + " | ".join(values))

                    if len(results) > 10:
                        self.stdout.write(f"  ... and {len(results) - 10} more rows")
            else:
                self.stdout.write(f"  Rows affected: {results}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Query failed: {str(e)}"))

    def optimize_database(self, options):
        """Optimize database tables."""
        table_name = options.get('table')

        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.WARNING('Database optimization only available for PostgreSQL'))
            return

        if table_name:
            self.stdout.write(self.style.WARNING(f"Optimizing table: {table_name}"))
            result = DatabaseManager.optimize_table(table_name)

            if result['success']:
                self.stdout.write(self.style.SUCCESS(result['message']))
            else:
                self.stdout.write(self.style.ERROR(f"Optimization failed: {result.get('error', 'Unknown error')}"))
        else:
            self.stdout.write(self.style.WARNING('Optimizing all tables...'))
            tables = DatabaseManager.get_table_sizes()

            for table in tables:
                if 'tablename' in table:
                    result = DatabaseManager.optimize_table(table['tablename'])
                    if result['success']:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ {table['tablename']}"))
                    else:
                        self.stdout.write(self.style.ERROR(f"  ✗ {table['tablename']}: {result.get('error', 'Unknown error')}"))

    def show_tables(self):
        """Show table information."""
        tables = DatabaseManager.get_table_sizes()

        self.stdout.write(self.style.SUCCESS(f'Table Information ({len(tables)} tables):'))

        for table in tables:
            if 'total_bytes' in table:
                size_mb = table['total_bytes'] / 1024 / 1024
                self.stdout.write(f"  {table['tablename']}: {size_mb:.2f} MB")
            else:
                self.stdout.write(f"  {table['tablename']}: {table.get('row_count', 'N/A')} rows")

    def show_indexes(self):
        """Show index usage statistics."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.WARNING('Index statistics only available for PostgreSQL'))
            return

        indexes = DatabaseManager.get_index_usage()

        self.stdout.write(self.style.SUCCESS(f'Index Usage Statistics ({len(indexes)} indexes):'))

        for idx in indexes:
            usage = idx['idx_scan']
            status = "✓" if usage > 0 else "✗"
            self.stdout.write(f"  {status} {idx['indexname']} ({idx['tablename']}): {usage} scans")

    def setup_docker_environment(self, options):
        """Setup database for Docker environment."""
        self.stdout.write(self.style.SUCCESS('Setting up Docker database environment...'))

        # Check if using PostgreSQL
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(self.style.ERROR('PostgreSQL configuration required for Docker setup'))
            return

        # Test database connection
        connection = DatabaseHealthChecker.check_connection()
        if connection['status'] != 'healthy':
            self.stdout.write(self.style.ERROR('Cannot connect to database. Make sure PostgreSQL is running.'))
            self.stdout.write('  Try: docker-compose up -d db')
            return

        # Create migrations
        self.stdout.write(self.style.WARNING('Creating migrations...'))
        os.system('python manage.py makemigrations')

        # Apply migrations
        self.stdout.write(self.style.WARNING('Applying migrations...'))
        os.system('python manage.py migrate')

        # Collect static files
        self.stdout.write(self.style.WARNING('Collecting static files...'))
        os.system('python manage.py collectstatic --noinput')

        self.stdout.write(self.style.SUCCESS('Docker database environment setup complete!'))
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('  1. Start the development server: python manage.py runserver')
        self.stdout.write('  2. Create a superuser: python manage.py createsuperuser')
        self.stdout.write('  3. Access the application at http://localhost:8000')