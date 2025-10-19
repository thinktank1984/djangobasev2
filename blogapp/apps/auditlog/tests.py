"""
Tests for the auditlog app.
"""

import json
import time
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

from apps.auditlog.models import SystemLog
from apps.auditlog.utils import (
    create_log_entry, log_api_request, log_error, log_audit_action,
    cleanup_old_logs, get_log_stats
)
from apps.auditlog.handlers import DatabaseLogHandler, set_request_context, clear_request_context
from apps.auditlog.middleware import RequestLoggingMiddleware, ErrorLoggingMiddleware
from apps.auditlog.exceptions import log_function_call, log_operation, OperationLogger

User = get_user_model()


class SystemLogModelTest(TestCase):
    """Test the SystemLog model."""
    databases = ['default', 'logs']

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for all tests."""
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_log_entry(self):
        """Test creating a basic log entry."""
        log = SystemLog.objects.create(
            level='INFO',
            category='system',
            message='Test log entry',
            user_id=self.user.id
        )

        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.category, 'system')
        self.assertEqual(log.message, 'Test log entry')
        self.assertEqual(log.user_id, self.user.id)
        self.assertIsNotNone(log.timestamp)

    def test_log_metadata(self):
        """Test log entry with metadata."""
        metadata = {'key1': 'value1', 'key2': 42}
        log = SystemLog.objects.create(
            level='ERROR',
            category='api',
            message='Error with metadata',
            metadata=metadata
        )

        self.assertEqual(log.metadata, metadata)
        self.assertIsInstance(log.metadata_json, str)

    def test_get_display_methods(self):
        """Test display methods for admin interface."""
        log = SystemLog.objects.create(
            level='ERROR',
            category='error',
            message='An error occurred'
        )

        level_display = log.get_display_level()
        self.assertIn('ERROR', level_display)
        self.assertIn('span', level_display)

        category_display = log.get_display_category()
        self.assertIn('❌', category_display)
        self.assertIn('Error', category_display)


class LoggingUtilsTest(TestCase):
    """Test logging utility functions."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_log_entry(self):
        """Test creating log entry via utility function."""
        metadata = {'test': 'data'}
        log = create_log_entry(
            level='INFO',
            category='system',
            message='Test via utility',
            user_id=self.user.id,
            metadata=metadata
        )

        self.assertEqual(log.level, 'INFO')
        self.assertEqual(log.category, 'system')
        self.assertEqual(log.message, 'Test via utility')
        self.assertEqual(log.user_id, self.user.id)
        self.assertEqual(log.metadata, metadata)

    def test_cleanup_old_logs(self):
        """Test cleanup of old logs."""
        # Create some test logs
        old_date = timezone.now() - timedelta(days=35)
        recent_date = timezone.now() - timedelta(days=5)

        old_log = SystemLog.objects.create(
            level='INFO',
            category='system',
            message='Old log',
            timestamp=old_date
        )

        recent_log = SystemLog.objects.create(
            level='INFO',
            category='system',
            message='Recent log',
            timestamp=recent_date
        )

        # Clean up logs older than 30 days
        deleted_count, remaining_count = cleanup_old_logs(days_to_keep=30)

        self.assertEqual(deleted_count, 1)
        self.assertEqual(remaining_count, 1)

        # Verify old log is deleted and recent log remains
        self.assertFalse(SystemLog.objects.filter(id=old_log.id).exists())
        self.assertTrue(SystemLog.objects.filter(id=recent_log.id).exists())

    def test_get_log_stats(self):
        """Test log statistics."""
        # Create test logs
        SystemLog.objects.create(level='INFO', category='api', message='Info log')
        SystemLog.objects.create(level='ERROR', category='error', message='Error log')
        SystemLog.objects.create(level='WARN', category='api', message='Warning log')

        stats = get_log_stats()

        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['by_level']['INFO'], 1)
        self.assertEqual(stats['by_level']['ERROR'], 1)
        self.assertEqual(stats['by_level']['WARN'], 1)
        self.assertEqual(stats['by_category']['api'], 2)
        self.assertEqual(stats['by_category']['error'], 1)


class ManagementCommandsTest(TestCase):
    """Test management commands."""

    def setUp(self):
        # Create test logs
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create logs at different times
        old_date = timezone.now() - timedelta(days=35)
        recent_date = timezone.now() - timedelta(hours=5)

        SystemLog.objects.create(
            level='INFO',
            category='api',
            message='Recent log',
            timestamp=recent_date,
            user_id=self.user.id
        )

        SystemLog.objects.create(
            level='ERROR',
            category='error',
            message='Old log',
            timestamp=old_date
        )

    def test_viewlogs_command(self):
        """Test the viewlogs management command."""
        out = StringIO()
        call_command('viewlogs', '--limit=10', stdout=out)

        output = out.getvalue()
        self.assertIn('Found', output)
        self.assertIn('Recent log', output)

    def test_cleanuplogs_dry_run(self):
        """Test cleanuplogs command with dry run."""
        out = StringIO()
        call_command('cleanuplogs', '--days=30', '--dry-run', stdout=out)

        output = out.getvalue()
        self.assertIn('DRY RUN', output)
        self.assertIn('Logs to delete: 1', output)
