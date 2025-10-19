"""
Django management command to view log entries.
"""

import argparse
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q, Count

from apps.auditlog.models import SystemLog


class Command(BaseCommand):
    help = 'View system log entries from the logging database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level',
            type=str,
            choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'],
            help='Filter by log level'
        )
        parser.add_argument(
            '--category',
            type=str,
            choices=['api', 'error', 'migration', 'audit', 'auth', 'system'],
            help='Filter by log category'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of log entries to display (default: 50)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            help='Show logs from the last N hours'
        )
        parser.add_argument(
            '--days',
            type=int,
            help='Show logs from the last N days'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Filter by user ID'
        )
        parser.add_argument(
            '--search',
            type=str,
            help='Search in message content'
        )
        parser.add_argument(
            '--count',
            action='store_true',
            help='Only show the count of matching log entries'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information including metadata'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show log statistics instead of entries'
        )

    def handle(self, *args, **options):
        level = options.get('level')
        category = options.get('category')
        limit = options.get('limit', 50)
        hours = options.get('hours')
        days = options.get('days')
        user_id = options.get('user_id')
        search = options.get('search')
        count_only = options.get('count', False)
        verbose = options.get('verbose', False)
        show_stats = options.get('stats', False)

        # Build queryset
        queryset = SystemLog.objects.all()

        # Apply filters
        if level:
            queryset = queryset.filter(level=level)

        if category:
            queryset = queryset.filter(category=category)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if search:
            queryset = queryset.filter(message__icontains=search)

        # Apply time filter
        if hours:
            since = timezone.now() - timedelta(hours=hours)
            queryset = queryset.filter(timestamp__gte=since)
        elif days:
            since = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=since)

        # Order by timestamp descending
        queryset = queryset.order_by('-timestamp')

        # Get count
        total_count = queryset.count()

        if show_stats:
            self.show_statistics()
            return

        if count_only:
            self.stdout.write(
                self.style.SUCCESS(f'Total matching log entries: {total_count}')
            )
            return

        if total_count == 0:
            self.stdout.write(self.style.WARNING('No log entries found matching the criteria.'))
            return

        # Display results
        self.stdout.write(
            self.style.SUCCESS(f'Found {total_count} log entries (showing latest {min(limit, total_count)}):')
        )
        self.stdout.write('')

        for log in queryset[:limit]:
            self.display_log_entry(log, verbose=verbose)

        if total_count > limit:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(f'... and {total_count - limit} more entries (use --limit to see more)')
            )

    def display_log_entry(self, log, verbose=False):
        """Display a single log entry."""
        timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Basic info
        line_parts = [
            f'[{timestamp}]',
            f'{log.level:8}',
            f'{log.category:8}',
            f'{log.message}'
        ]

        # Add user info if available
        if log.user_id:
            line_parts.append(f'(User: {log.user_id})')

        # Add IP info if available
        if log.ip_address:
            line_parts.append(f'IP: {log.ip_address}')

        self.stdout.write(' '.join(line_parts))

        # Verbose output
        if verbose:
            if log.request_id:
                self.stdout.write(f'    Request ID: {log.request_id}')
            if log.object_id:
                self.stdout.write(f'    Object ID: {log.object_id}')
            if log.user_agent:
                # Truncate long user agents
                ua = log.user_agent[:100] + '...' if len(log.user_agent) > 100 else log.user_agent
                self.stdout.write(f'    User Agent: {ua}')
            if log.metadata:
                self.stdout.write('    Metadata:')
                for key, value in log.metadata.items():
                    if isinstance(value, (dict, list)):
                        value_str = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                    else:
                        value_str = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                    self.stdout.write(f'      {key}: {value_str}')

        self.stdout.write('')

    def show_statistics(self):
        """Display log statistics."""
        self.stdout.write(self.style.SUCCESS('📊 Log Statistics'))
        self.stdout.write('')

        # Total logs
        total = SystemLog.objects.count()
        self.stdout.write(f'Total log entries: {total}')

        if total == 0:
            return

        self.stdout.write('')

        # By level
        self.stdout.write('By Level:')
        level_stats = {}
        for level, _ in SystemLog.LEVEL_CHOICES:
            count = SystemLog.objects.filter(level=level).count()
            if count > 0:
                level_stats[level] = count
                percentage = (count / total) * 100
                self.stdout.write(f'  {level:8}: {count:6} ({percentage:5.1f}%)')

        self.stdout.write('')

        # By category
        self.stdout.write('By Category:')
        category_stats = {}
        for category, _ in SystemLog.CATEGORY_CHOICES:
            count = SystemLog.objects.filter(category=category).count()
            if count > 0:
                category_stats[category] = count
                percentage = (count / total) * 100
                self.stdout.write(f'  {category:8}: {count:6} ({percentage:5.1f}%)')

        self.stdout.write('')

        # Recent activity
        now = timezone.now()
        last_24h = SystemLog.objects.filter(timestamp__gte=now - timedelta(hours=24)).count()
        last_7d = SystemLog.objects.filter(timestamp__gte=now - timedelta(days=7)).count()
        last_30d = SystemLog.objects.filter(timestamp__gte=now - timedelta(days=30)).count()

        self.stdout.write('Recent Activity:')
        self.stdout.write(f'  Last 24 hours: {last_24h}')
        self.stdout.write(f'  Last 7 days:   {last_7d}')
        self.stdout.write(f'  Last 30 days:  {last_30d}')

        # Top users
        self.stdout.write('')
        self.stdout.write('Top Users (by log count):')
        top_users = SystemLog.objects.filter(user_id__isnull=False) \
                                   .values('user_id') \
                                   .annotate(count=Count('id')) \
                                   .order_by('-count')[:5]

        for user_stat in top_users:
            user_id = user_stat['user_id']
            count = user_stat['count']
            self.stdout.write(f'  User {user_id}: {count} entries')

        # Error patterns
        self.stdout.write('')
        self.stdout.write('Recent Errors (last 24 hours):')
        recent_errors = SystemLog.objects.filter(
            level='ERROR',
            timestamp__gte=now - timedelta(hours=24)
        ).order_by('-timestamp')[:10]

        if recent_errors:
            for error in recent_errors:
                timestamp = error.timestamp.strftime('%H:%M:%S')
                message = error.message[:80] + '...' if len(error.message) > 80 else error.message
                self.stdout.write(f'  [{timestamp}] {message}')
        else:
            self.stdout.write('  No errors in the last 24 hours 🎉')