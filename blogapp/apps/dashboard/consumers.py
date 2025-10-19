"""
WebSocket consumers for real-time dashboard updates.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.user_group_name = f'dashboard_user_{self.user.id}'

        # Join user-specific group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Dashboard connection established',
            'user_id': self.user.id
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

        if message_type == 'heartbeat':
            await self.send(text_data=json.dumps({
                'type': 'heartbeat_response',
                'timestamp': text_data_json.get('timestamp')
            }))

        elif message_type == 'request_dashboard_update':
            # Send current dashboard data
            dashboard_data = await self.get_dashboard_data()
            await self.send(text_data=json.dumps({
                'type': 'dashboard_update',
                'data': dashboard_data
            }))

    async def dashboard_update(self, event):
        """Handle dashboard update events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': event['data']
        }))

    async def notification_message(self, event):
        """Handle notification events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'level': event.get('level', 'info')
        }))

    @database_sync_to_async
    def get_dashboard_data(self):
        """Get current dashboard data for the user."""
        try:
            from .models import DashboardStats

            stats = DashboardStats.objects.filter(user=self.user).first()
            if stats:
                return {
                    'total_subscriptions': stats.total_subscriptions,
                    'active_subscriptions': stats.active_subscriptions,
                    'total_revenue': stats.total_revenue,
                    'last_updated': stats.last_updated.isoformat()
                }
            else:
                return {
                    'total_subscriptions': 0,
                    'active_subscriptions': 0,
                    'total_revenue': '0.00',
                    'last_updated': None
                }
        except ImportError:
            # Return dummy data if model doesn't exist yet
            return {
                'total_subscriptions': 0,
                'active_subscriptions': 0,
                'total_revenue': '0.00',
                'last_updated': None
            }


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """Consumer for admin dashboard real-time updates."""

    async def connect(self):
        """Handle WebSocket connection for admin users."""
        if not self.scope["user"].is_authenticated or not self.scope["user"].is_staff:
            await self.close()
            return

        self.admin_group_name = 'admin_dashboard'

        # Join admin group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'admin_connection_established',
            'message': 'Admin dashboard connection established'
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        await self.channel_layer.group_discard(
            self.admin_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', '')

        if message_type == 'request_system_stats':
            system_stats = await self.get_system_stats()
            await self.send(text_data=json.dumps({
                'type': 'system_stats',
                'data': system_stats
            }))

    async def system_update(self, event):
        """Handle system update events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'system_update',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_system_stats(self):
        """Get system-wide statistics for admin dashboard."""
        from django.contrib.auth.models import User

        return {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
            'last_updated': None  # You can add timestamp here
        }