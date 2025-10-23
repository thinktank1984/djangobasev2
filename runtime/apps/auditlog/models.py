import json
from django.db import models
from django.utils import timezone


class SystemLog(models.Model):
    """
    A unified model for storing all types of operational logs.
    """

    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARN', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]

    CATEGORY_CHOICES = [
        ('api', 'API Request'),
        ('error', 'Error'),
        ('migration', 'Migration'),
        ('audit', 'Audit'),
        ('auth', 'Authentication'),
        ('system', 'System'),
    ]

    level = models.CharField(
        max_length=10,
        choices=LEVEL_CHOICES,
        default='INFO',
        db_index=True
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True
    )
    message = models.TextField()
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )

    # Optional foreign key references (stored as integers to avoid cross-db constraints)
    user_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="ID of the user associated with this log entry"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="ID of the object associated with this log entry"
    )

    # Additional metadata stored as JSON
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional structured data related to the log entry"
    )

    # Request tracking information
    request_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        db_index=True,
        help_text="Unique identifier for the request that generated this log"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the client"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent string of the client"
    )

    class Meta:
        app_label = 'auditlog'
        db_table = 'system_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['level', 'timestamp']),
            models.Index(fields=['category', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
            models.Index(fields=['request_id']),
        ]
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'

    def __str__(self):
        return f"{self.level}: {self.category} - {self.message[:50]}"

    @property
    def metadata_json(self):
        """Return metadata as formatted JSON string"""
        if self.metadata:
            return json.dumps(self.metadata, indent=2, sort_keys=True)
        return "{}"

    def get_display_level(self):
        """Return level with appropriate CSS class for admin interface"""
        css_classes = {
            'DEBUG': 'debug',
            'INFO': 'info',
            'WARN': 'warning',
            'ERROR': 'error',
            'CRITICAL': 'critical',
        }
        return f'<span class="log-level {css_classes.get(self.level, "")}">{self.level}</span>'

    def get_display_category(self):
        """Return category with appropriate icon"""
        icons = {
            'api': '🌐',
            'error': '❌',
            'migration': '🔄',
            'audit': '📋',
            'auth': '🔐',
            'system': '⚙️',
        }
        return f'{icons.get(self.category, "📝")} {self.get_category_display()}'
