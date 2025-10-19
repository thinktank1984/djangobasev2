"""
Database utilities for PostgreSQL integration and query management.
"""

import os
from contextlib import contextmanager
from django.db import connection, models
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import Dict, List, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class DatabaseManager:
    """Utility class for advanced database operations."""

    @staticmethod
    def get_database_info() -> Dict[str, Any]:
        """Get comprehensive database information."""
        info = {
            'engine': settings.DATABASES['default']['ENGINE'],
            'name': settings.DATABASES['default']['NAME'],
            'host': settings.DATABASES['default']['HOST'],
            'port': settings.DATABASES['default']['PORT'],
            'vendor': 'sqlite' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'postgresql'
        }

        if info['vendor'] == 'postgresql':
            info.update(DatabaseManager.get_postgresql_info())
        else:
            info.update(DatabaseManager.get_sqlite_info())

        return info

    @staticmethod
    def get_postgresql_info() -> Dict[str, Any]:
        """Get PostgreSQL-specific information."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]

                cursor.execute("SELECT pg_size_pretty(pg_database_size(%s));", [settings.DATABASES['default']['NAME']])
                size = cursor.fetchone()[0]

                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
                active_connections = cursor.fetchone()[0]

                cursor.execute("SHOW max_connections;")
                max_connections = cursor.fetchone()[0]

                return {
                    'version': version,
                    'size': size,
                    'active_connections': active_connections,
                    'max_connections': max_connections,
                    'is_postgresql': True
                }
        except Exception as e:
            logger.error(f"Error getting PostgreSQL info: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_sqlite_info() -> Dict[str, Any]:
        """Get SQLite-specific information."""
        try:
            db_path = settings.DATABASES['default']['NAME']
            file_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

            with connection.cursor() as cursor:
                cursor.execute("SELECT sqlite_version();")
                version = cursor.fetchone()[0]

                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]

                return {
                    'version': f"SQLite {version}",
                    'size': f"{file_size / 1024 / 1024:.2f} MB",
                    'table_count': table_count,
                    'is_sqlite': True,
                    'path': str(db_path)
                }
        except Exception as e:
            logger.error(f"Error getting SQLite info: {e}")
            return {'error': str(e)}

    @staticmethod
    def execute_raw_query(query: str, params: Optional[List] = None, fetch: bool = True) -> Union[List[Dict], int]:
        """Execute a raw SQL query safely."""
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params or [])

                if fetch:
                    columns = [col[0] for col in cursor.description]
                    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    return results
                else:
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"Error executing query: {query[:100]}... Error: {e}")
            raise

    @staticmethod
    def analyze_query_performance(query: str, params: Optional[List] = None) -> Dict[str, Any]:
        """Analyze query performance using EXPLAIN."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return {'error': 'Query analysis only available for PostgreSQL'}

        try:
            with connection.cursor() as cursor:
                # Explain the query
                explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"
                cursor.execute(explain_query, params)
                explain_result = cursor.fetchone()[0]

                return {
                    'explain_plan': explain_result,
                    'execution_time': explain_result[0].get('Execution Time', 0),
                    'planning_time': explain_result[0].get('Planning Time', 0),
                    'actual_rows': explain_result[0].get('Plan', {}).get('Actual Rows', 0),
                }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {'error': str(e)}

    @staticmethod
    def get_table_sizes() -> List[Dict[str, Any]]:
        """Get size information for all tables."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return DatabaseManager._get_sqlite_table_sizes()

        try:
            query = """
                SELECT
                    schemaname,
                    tablename,
                    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
                    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) as index_size,
                    pg_total_relation_size(schemaname||'.'||tablename) as total_bytes
                FROM pg_tables
                WHERE schemaname = 'public'
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            """
            return DatabaseManager.execute_raw_query(query)
        except Exception as e:
            logger.error(f"Error getting table sizes: {e}")
            return []

    @staticmethod
    def _get_sqlite_table_sizes() -> List[Dict[str, Any]]:
        """Get table sizes for SQLite database."""
        try:
            tables = DatabaseManager.execute_raw_query(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            results = []

            for table in tables:
                table_name = table['name']
                try:
                    count_query = f"SELECT COUNT(*) FROM {table_name};"
                    row_count = DatabaseManager.execute_raw_query(count_query)[0]['COUNT(*)']

                    results.append({
                        'tablename': table_name,
                        'row_count': row_count,
                        'estimated_size': 'N/A (SQLite)'
                    })
                except:
                    results.append({
                        'tablename': table_name,
                        'row_count': 'N/A',
                        'estimated_size': 'N/A'
                    })

            return results
        except Exception as e:
            logger.error(f"Error getting SQLite table sizes: {e}")
            return []

    @staticmethod
    def get_index_usage() -> List[Dict[str, Any]]:
        """Get index usage statistics (PostgreSQL only)."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return []

        try:
            query = """
                SELECT
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
            """
            return DatabaseManager.execute_raw_query(query)
        except Exception as e:
            logger.error(f"Error getting index usage: {e}")
            return []

    @staticmethod
    def get_slow_queries(limit: int = 10) -> List[Dict[str, Any]]:
        """Get slow queries from pg_stat_statements (PostgreSQL only)."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return []

        try:
            # Check if pg_stat_statements is available
            check_query = """
                SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_stat_statements'
            """
            result = DatabaseManager.execute_raw_query(check_query)
            if result[0]['count'] == 0:
                return [{'error': 'pg_stat_statements extension not installed'}]

            query = """
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows,
                    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT %s
            """
            return DatabaseManager.execute_raw_query(query, [limit])
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []

    @staticmethod
    def optimize_table(table_name: str) -> Dict[str, Any]:
        """Optimize a table (VACUUM ANALYZE for PostgreSQL)."""
        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return {'error': 'Table optimization only available for PostgreSQL'}

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"VACUUM ANALYZE {table_name};")
                return {'success': True, 'table': table_name, 'message': 'Table optimized successfully'}
        except Exception as e:
            logger.error(f"Error optimizing table {table_name}: {e}")
            return {'error': str(e)}

    @staticmethod
    @contextmanager
    def transaction_scope():
        """Context manager for database transactions."""
        try:
            with connection.atomic():
                yield
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            raise


class QueryOptimizer:
    """Utility class for query optimization and analysis."""

    @staticmethod
    def suggest_indexes() -> List[Dict[str, Any]]:
        """Suggest indexes based on query patterns."""
        suggestions = []

        # Check foreign key indexes
        with connection.cursor() as cursor:
            if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("""
                    SELECT
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                """)
                foreign_keys = cursor.fetchall()

                for fk in foreign_keys:
                    table_name, column_name, foreign_table, foreign_column = fk
                    suggestions.append({
                        'type': 'foreign_key',
                        'table': table_name,
                        'column': column_name,
                        'suggestion': f"Create index on {table_name}.{column_name} for foreign key performance",
                        'sql': f"CREATE INDEX CONCURRENTLY idx_{table_name}_{column_name} ON {table_name} ({column_name});"
                    })

        return suggestions

    @staticmethod
    def analyze_model_queries(model_class: models.Model) -> Dict[str, Any]:
        """Analyze common query patterns for a model."""
        model_name = model_class._meta.model_name
        table_name = model_class._meta.db_table

        analysis = {
            'model': model_name,
            'table': table_name,
            'fields': [],
            'suggestions': []
        }

        # Analyze fields
        for field in model_class._meta.fields:
            field_info = {
                'name': field.name,
                'type': field.get_internal_type(),
                'indexed': field.db_index or field.unique or field.primary_key,
                'foreign_key': field.many_to_one
            }
            analysis['fields'].append(field_info)

            # Suggest indexes for commonly queried fields
            if not field_info['indexed'] and field_info['type'] in ['CharField', 'TextField', 'DateField', 'DateTimeField']:
                analysis['suggestions'].append({
                    'type': 'field_index',
                    'field': field.name,
                    'suggestion': f"Consider indexing {field.name} if frequently queried",
                    'sql': f"CREATE INDEX CONCURRENTLY idx_{table_name}_{field.name} ON {table_name} ({field.name});"
                })

        return analysis


class DatabaseBackup:
    """Utility class for database backup operations."""

    @staticmethod
    def create_backup(backup_path: Optional[str] = None) -> Dict[str, Any]:
        """Create a database backup."""
        import subprocess
        from datetime import datetime

        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return DatabaseBackup._create_sqlite_backup(backup_path)

        db_config = settings.DATABASES['default']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not backup_path:
            backup_path = f"backup_{timestamp}.dump"

        try:
            # Create backup using pg_dump
            cmd = [
                'pg_dump',
                '-h', db_config['HOST'],
                '-U', db_config['USER'],
                '-d', db_config['NAME'],
                '-Fc',  # Custom format
                '-f', backup_path
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                file_size = os.path.getsize(backup_path)
                return {
                    'success': True,
                    'backup_path': backup_path,
                    'file_size': file_size,
                    'message': f'Backup created successfully: {backup_path}'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Backup failed'
                }
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _create_sqlite_backup(backup_path: Optional[str] = None) -> Dict[str, Any]:
        """Create SQLite backup."""
        import shutil
        from datetime import datetime

        db_path = settings.DATABASES['default']['NAME']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not backup_path:
            backup_path = f"sqlite_backup_{timestamp}.db"

        try:
            shutil.copy2(db_path, backup_path)
            file_size = os.path.getsize(backup_path)

            return {
                'success': True,
                'backup_path': backup_path,
                'file_size': file_size,
                'message': f'SQLite backup created successfully: {backup_path}'
            }
        except Exception as e:
            logger.error(f"Error creating SQLite backup: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def restore_backup(backup_path: str) -> Dict[str, Any]:
        """Restore database from backup."""
        import subprocess

        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            return DatabaseBackup._restore_sqlite_backup(backup_path)

        db_config = settings.DATABASES['default']

        try:
            # Restore backup using pg_restore
            cmd = [
                'pg_restore',
                '-h', db_config['HOST'],
                '-U', db_config['USER'],
                '-d', db_config['NAME'],
                '--clean',
                '--if-exists',
                backup_path
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['PASSWORD']

            result = subprocess.run(cmd, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': f'Database restored successfully from: {backup_path}'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': 'Restore failed'
                }
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _restore_sqlite_backup(backup_path: str) -> Dict[str, Any]:
        """Restore SQLite backup."""
        import shutil

        db_path = settings.DATABASES['default']['NAME']

        try:
            shutil.copy2(backup_path, db_path)
            return {
                'success': True,
                'message': f'SQLite database restored from: {backup_path}'
            }
        except Exception as e:
            logger.error(f"Error restoring SQLite backup: {e}")
            return {'success': False, 'error': str(e)}


class DatabaseHealthChecker:
    """Utility class for database health monitoring."""

    @staticmethod
    def check_connection() -> Dict[str, Any]:
        """Check database connection health."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {
                    'status': 'healthy',
                    'message': 'Database connection is working'
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }

    @staticmethod
    def check_table_integrity() -> Dict[str, Any]:
        """Check table integrity (SQLite specific)."""
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            return {'message': 'Table integrity check not applicable for PostgreSQL'}

        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA integrity_check;")
                result = cursor.fetchone()
                return {
                    'status': 'ok' if result[0] == 'ok' else 'error',
                    'message': result[0]
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """Get comprehensive database statistics."""
        stats = {
            'connection': DatabaseHealthChecker.check_connection(),
            'info': DatabaseManager.get_database_info(),
            'tables': DatabaseManager.get_table_sizes(),
        }

        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            stats.update({
                'index_usage': DatabaseManager.get_index_usage(),
                'slow_queries': DatabaseManager.get_slow_queries(),
            })
        else:
            stats['integrity'] = DatabaseHealthChecker.check_table_integrity()

        return stats