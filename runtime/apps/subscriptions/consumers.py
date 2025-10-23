"""
WebSocket consumers for real-time subscription updates.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class SubscriptionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        if self.scope["user"].is_anonymous:
            await self.close()
            return

        self.user = self.scope["user"]
        self.user_group_name = f'subscriptions_user_{self.user.id}'

        # Join user-specific subscription group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Subscription updates connection established',
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

        if message_type == 'request_subscription_status':
            # Send current subscription status
            subscription_data = await self.get_subscription_data()
            await self.send(text_data=json.dumps({
                'type': 'subscription_status',
                'data': subscription_data
            }))

        elif message_type == 'request_subscription_history':
            # Send subscription history
            history_data = await self.get_subscription_history()
            await self.send(text_data=json.dumps({
                'type': 'subscription_history',
                'data': history_data
            }))

    async def subscription_status_update(self, event):
        """Handle subscription status update events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'subscription_status_update',
            'data': event['data']
        }))

    async def payment_confirmation(self, event):
        """Handle payment confirmation events from the channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'payment_confirmation',
            'data': event['data']
        }))

    async def subscription_expiry_warning(self, event):
        """Handle subscription expiry warning events."""
        await self.send(text_data=json.dumps({
            'type': 'subscription_expiry_warning',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_subscription_data(self):
        """Get current subscription data for the user."""
        try:
            from .models import Subscription

            active_subscriptions = Subscription.objects.filter(
                user=self.user,
                is_active=True
            ).order_by('-created_at')

            subscriptions_data = []
            for sub in active_subscriptions:
                subscriptions_data.append({
                    'id': sub.id,
                    'plan_name': sub.plan_name if hasattr(sub, 'plan_name') else 'Premium',
                    'status': 'active' if sub.is_active else 'inactive',
                    'start_date': sub.created_at.isoformat(),
                    'end_date': sub.end_date.isoformat() if hasattr(sub, 'end_date') and sub.end_date else None,
                    'amount': str(sub.amount) if hasattr(sub, 'amount') else '0.00',
                    'currency': getattr(sub, 'currency', 'USD')
                })

            return {
                'active_subscriptions': subscriptions_data,
                'total_active_count': len(subscriptions_data)
            }

        except ImportError:
            # Return dummy data if model doesn't exist yet
            return {
                'active_subscriptions': [],
                'total_active_count': 0
            }

    @database_sync_to_async
    def get_subscription_history(self):
        """Get subscription history for the user."""
        try:
            from .models import Subscription

            all_subscriptions = Subscription.objects.filter(
                user=self.user
            ).order_by('-created_at')

            history_data = []
            for sub in all_subscriptions:
                history_data.append({
                    'id': sub.id,
                    'plan_name': getattr(sub, 'plan_name', 'Premium'),
                    'status': 'active' if sub.is_active else 'inactive',
                    'created_at': sub.created_at.isoformat(),
                    'amount': str(getattr(sub, 'amount', 0)),
                    'currency': getattr(sub, 'currency', 'USD')
                })

            return history_data

        except ImportError:
            return []


class SubscriptionAdminConsumer(AsyncWebsocketConsumer):
    """Consumer for admin subscription monitoring."""

    async def connect(self):
        """Handle WebSocket connection for admin users."""
        if not self.scope["user"].is_authenticated or not self.scope["user"].is_staff:
            await self.close()
            return

        self.admin_group_name = 'subscription_admin'

        # Join admin subscription group
        await self.channel_layer.group_add(
            self.admin_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'admin_connection_established',
            'message': 'Subscription admin connection established'
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

        if message_type == 'request_subscription_stats':
            stats = await self.get_subscription_stats()
            await self.send(text_data=json.dumps({
                'type': 'subscription_stats',
                'data': stats
            }))

    async def new_subscription_alert(self, event):
        """Handle new subscription alerts."""
        await self.send(text_data=json.dumps({
            'type': 'new_subscription_alert',
            'data': event['data']
        }))

    async def subscription_cancellation_alert(self, event):
        """Handle subscription cancellation alerts."""
        await self.send(text_data=json.dumps({
            'type': 'subscription_cancellation_alert',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_subscription_stats(self):
        """Get subscription statistics for admin."""
        try:
            from .models import Subscription

            total_subscriptions = Subscription.objects.count()
            active_subscriptions = Subscription.objects.filter(is_active=True).count()

            return {
                'total_subscriptions': total_subscriptions,
                'active_subscriptions': active_subscriptions,
                'inactive_subscriptions': total_subscriptions - active_subscriptions,
                'last_updated': None  # Add timestamp if needed
            }

        except ImportError:
            return {
                'total_subscriptions': 0,
                'active_subscriptions': 0,
                'inactive_subscriptions': 0,
                'last_updated': None
            }