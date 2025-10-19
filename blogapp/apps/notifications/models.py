"""
Models for notification system.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Notification(models.Model):
    """Model for user notifications."""

    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional data field for additional information
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])

    @classmethod
    def create_notification(cls, user, title, message, level='info', data=None):
        """Create a new notification and send real-time update."""
        notification = cls.objects.create(
            user=user,
            title=title,
            message=message,
            level=level,
            data=data or {}
        )

        # Send real-time notification via channels
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        user_group_name = f'notifications_user_{user.id}'

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'new_notification',
                'data': {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'level': notification.level,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'data': notification.data
                }
            }
        )

        return notification


class UserPresence(models.Model):
    """Model for tracking user presence/online status."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

    @classmethod
    def set_user_online(cls, user):
        """Set user as online."""
        presence, created = cls.objects.get_or_create(
            user=user,
            defaults={'is_online': True}
        )
        if not created:
            presence.is_online = True
            presence.last_activity = timezone.now()
            presence.save()
        return presence

    @classmethod
    def set_user_offline(cls, user):
        """Set user as offline."""
        try:
            presence = cls.objects.get(user=user)
            presence.is_online = False
            presence.last_seen = timezone.now()
            presence.save()
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_online_users(cls):
        """Get list of online users."""
        return cls.objects.filter(is_online=True).select_related('user')