"""
WebSocket consumers for real-time notifications.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.user_group_name = f'notifications_user_{self.user.id}'

        # Join user-specific notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Notifications connection established',
            'user_id': self.user.id
        }))

        # Send unread notifications count
        unread_count = await self.get_unread_notifications_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'mark_as_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_as_read(notification_id)
            await self.send(text_data=json.dumps({
                'type': 'notification_marked_read',
                'notification_id': notification_id
            }))

        elif message_type == 'mark_all_as_read':
            await self.mark_all_notifications_as_read()
            await self.send(text_data=json.dumps({
                'type': 'all_notifications_marked_read'
            }))

        elif message_type == 'request_notifications':
            notifications = await self.get_user_notifications()
            await self.send(text_data=json.dumps({
                'type': 'notifications_list',
                'data': notifications
            }))

        elif message_type == 'request_unread_count':
            unread_count = await self.get_unread_notifications_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))

    async def new_notification(self, event):
        """Handle new notification events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': event['data']
        }))

        # Update unread count
        unread_count = await self.get_unread_notifications_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    async def notification_read(self, event):
        """Handle notification read events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'notification_read',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_user_notifications(self):
        """Get user's notifications."""
        try:
            from .models import Notification

            notifications = Notification.objects.filter(
                user=self.user
            ).order_by('-created_at')[:20]  # Get last 20 notifications

            return [
                {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'level': notification.level,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'data': notification.data if hasattr(notification, 'data') else {}
                }
                for notification in notifications
            ]

        except ImportError:
            return []

    @database_sync_to_async
    def get_unread_notifications_count(self):
        """Get count of unread notifications."""
        try:
            from .models import Notification
            return Notification.objects.filter(
                user=self.user,
                is_read=False
            ).count()
        except ImportError:
            return 0

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark a specific notification as read."""
        try:
            from .models import Notification
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        """Mark all user notifications as read."""
        try:
            from .models import Notification
            Notification.objects.filter(
                user=self.user,
                is_read=False
            ).update(is_read=True)
            return True
        except:
            return False


class PresenceConsumer(AsyncWebsocketConsumer):
    """Consumer for user presence/online status."""

    async def connect(self):
        """Handle WebSocket connection for presence tracking."""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.presence_group_name = 'presence'

        # Join presence group
        await self.channel_layer.group_add(
            self.presence_group_name,
            self.channel_name
        )

        await self.accept()

        # Announce user is online
        await self.channel_layer.group_send(
            self.presence_group_name,
            {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name
            }
        )

        # Send list of online users
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'data': online_users
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Announce user is offline
        await self.channel_layer.group_send(
            self.presence_group_name,
            {
                'type': 'user_offline',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )

        await self.channel_layer.group_discard(
            self.presence_group_name,
            self.channel_name
        )

    async def user_online(self, event):
        """Handle user online events."""
        await self.send(text_data=json.dumps({
            'type': 'user_online',
            'data': {
                'user_id': event['user_id'],
                'username': event['username'],
                'first_name': event.get('first_name', ''),
                'last_name': event.get('last_name', '')
            }
        }))

    async def user_offline(self, event):
        """Handle user offline events."""
        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'data': {
                'user_id': event['user_id'],
                'username': event['username']
            }
        }))

    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users (simplified implementation)."""
        # In a production environment, you'd want to use Redis sets
        # or a similar mechanism to track online users
        return []