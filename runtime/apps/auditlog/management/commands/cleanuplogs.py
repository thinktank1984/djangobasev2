"""
Django management command to clean up old log entries.
"""

import argparse
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.db.models import Count

from apps.auditlog.models import SystemLog
from apps.auditlog.utils import cleanup_old_logs, get_log_stats


class Command(BaseCommand):
    help = 'Clean up old system log entries from the logging database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete logs older than this many days (default: 30)'
        )
        parser.add_argument(
            '--level',
            type=str,
            choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
            help='Only delete logs of this level'
        )
        parser.add_argument(
            '--category',
            type=str,
            choices=['api', 'error', 'migration', 'audit', 'auth', 'system'],
            help='Only delete logs of this category'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of logs to delete in each batch (default: 1000)'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Answer yes to all prompts (same as --force)'
        )

    def handle(self, *args, **options):
        days = options.get('days', 30)
        level = options.get('level')
        category = options.get('category')
        dry_run = options.get('dry_run', False)
        force = options.get('force', False) or options.get('yes', False)
        batch_size = options.get('batch_size', 1000)

        if days < 1:
            raise CommandError('Days must be a positive integer')

        if batch_size < 1:
            raise CommandError('Batch size must be a positive integer')

        # Show current statistics
        self.show_current_stats()

        # Calculate what would be deleted
        cutoff_date = timezone.now() - timedelta(days=days)
        queryset = SystemLog.objects.filter(timestamp__lt=cutoff_date)

        if level:
            queryset = queryset.filter(level=level)

        if category:
            queryset = queryset.filter(category=category)

        count_to_delete = queryset.count()

        if count_to_delete == 0:
            self.stdout.write(self.style.SUCCESS('No log entries match the criteria for deletion.'))
            return

        # Show what would be deleted
        self.stdout.write('')
        self.stdout.write(self.style.WARNING(f'Logs to delete: {count_to_delete}'))
        self.stdout.write(f'Deletion criteria: older than {days} days')
        if level:
            self.stdout.write(f'Level filter: {level}')
        if category:
            self.stdout.write(f'Category filter: {category}')
        self.stdout.write(f'Cutoff date: {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")}')

        # Show breakdown
        self.show_deletion_breakdown(queryset)

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('DRY RUN - No logs were actually deleted.'))
            return

        # Confirmation
        if not force:
            self.stdout.write('')
            response = input('Are you sure you want to delete these logs? [y/N]: ')
            if response.lower() not in ['y', 'yes']:
                self.stdout.write('Operation cancelled.')
                return

        # Perform deletion
        self.stdout.write('')
        self.stdout.write('Deleting logs...')

        try:
            with transaction.atomic():
                deleted_count = 0
                remaining = count_to_delete

                while remaining > 0:
                    current_batch_size = min(batch_size, remaining)
                    batch_queryset = queryset[:current_batch_size]
                    batch_deleted = batch_queryset.delete()[0]
                    deleted_count += batch_deleted
                    remaining -= batch_deleted

                    # Progress indicator
                    progress = (deleted_count / count_to_delete) * 100
                    self.stdout.write(
                        f'  Progress: {deleted_count}/{count_to_delete} ({progress:.1f}%)',
                        ending='\r'
                    )

                self.stdout.write('')  # New line after progress

        except Exception as e:
            raise CommandError(f'Error during deletion: {e}')

        # Show results
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} log entries.'))

        # Show new statistics
        self.show_current_stats()

    def show_current_stats(self):
        """Display current database statistics."""
        self.stdout.write(self.style.SUCCESS('📊 Current Database Statistics'))
        stats = get_log_stats()
        self.stdout.write(f'Total logs: {stats["total"]}')
        self.stdout.write(f'Recent 24h: {stats["recent_24h"]}')
        self.stdout.write(f'Recent 7d: {stats["recent_7d"]}')

        # Database file size if SQLite
        from django.conf import settings
        db_config = settings.DATABASES.get('logs', {})
        if db_config.get('ENGINE') == 'django.db.backends.sqlite3':
            import os
            db_path = db_config.get('NAME')
            if os.path.exists(db_path):
                size_bytes = os.path.getsize(db_path)
                size_mb = size_bytes / (1024 * 1024)
                self.stdout.write(f'Database size: {size_mb:.2f} MB')

    def show_deletion_breakdown(self, queryset):
        """Show a breakdown of what will be deleted."""
        self.stdout.write('')
        self.stdout.write('Deletion breakdown:')

        # By level
        level_breakdown = {}
        for level, _ in SystemLog.LEVEL_CHOICES:
            count = queryset.filter(level=level).count()
            if count > 0:
                level_breakdown[level] = count

        if level_breakdown:
            self.stdout.write('  By level:')
            total = sum(level_breakdown.values())
            for level, count in level_breakdown.items():
                percentage = (count / total) * 100
                self.stdout.write(f'    {level:8}: {count:6} ({percentage:5.1f}%)')

        # By category
        category_breakdown = {}
        for category, _ in SystemLog.CATEGORY_CHOICES:
            count = queryset.filter(category=category).count()
            if count > 0:
                category_breakdown[category] = count

        if category_breakdown:
            self.stdout.write('  By category:')
            total = sum(category_breakdown.values())
            for category, count in category_breakdown.items():
                percentage = (count / total) * 100
                self.stdout.write(f'    {category:8}: {count:6} ({percentage:5.1f}%)')

        # Date range of logs to be deleted
        oldest_log = queryset.order_by('timestamp').first()
        newest_log = queryset.order_by('-timestamp').first()
        if oldest_log and newest_log:
            self.stdout.write('')
            self.stdout.write('  Date range:')
            self.stdout.write(f'    Oldest: {oldest_log.timestamp.strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'    Newest: {newest_log.timestamp.strftime("%Y-%m-%d %H:%M:%S")}')