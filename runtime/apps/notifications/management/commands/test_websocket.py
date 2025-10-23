"""
Django management command to test WebSocket functionality.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notifications.utils import (
    send_notification,
    send_dashboard_update,
    send_subscription_update,
    broadcast_system_message
)
import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Test WebSocket real-time functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to send test messages to (default: sends to all users)'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['notification', 'dashboard', 'subscription', 'broadcast'],
            default='notification',
            help='Type of message to send'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of messages to send'
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=1.0,
            help='Interval between messages in seconds'
        )

    def handle(self, *args, **options):
        username = options.get('user')
        message_type = options.get('type')
        count = options.get('count')
        interval = options.get('interval')

        self.stdout.write(
            self.style.SUCCESS(f'Testing WebSocket {message_type} messages...')
        )

        if username:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.SUCCESS(f'Sending to user: {user.username} (ID: {user.id})')
                )
                self.send_test_messages(user, message_type, count, interval)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User {username} does not exist')
                )
                return
        else:
            users = User.objects.all()
            if users.exists():
                self.stdout.write(
                    self.style.SUCCESS(f'Sending to {users.count()} users')
                )
                for user in users:
                    self.send_test_messages(user, message_type, count, interval)
                    time.sleep(interval)
            else:
                self.stdout.write(
                    self.style.WARNING('No users found. Creating test user...')
                )
                user = User.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='testpass123'
                )
                self.send_test_messages(user, message_type, count, interval)

        self.stdout.write(
            self.style.SUCCESS('WebSocket test completed')
        )

    def send_test_messages(self, user, message_type, count, interval):
        """Send test messages to a user."""
        for i in range(count):
            try:
                if message_type == 'notification':
                    levels = ['info', 'success', 'warning', 'error']
                    level = levels[i % len(levels)]

                    send_notification(
                        user_id=user.id,
                        title=f'Test Notification #{i + 1}',
                        message=f'This is test notification #{i + 1} sent at {time.strftime("%H:%M:%S")}',
                        level=level
                    )

                elif message_type == 'dashboard':
                    import random
                    send_dashboard_update(
                        user_id=user.id,
                        data={
                            'total_subscriptions': random.randint(1, 10),
                            'active_subscriptions': random.randint(1, 5),
                            'total_revenue': f'{random.uniform(10, 100):.2f}',
                            'last_updated': time.strftime("%Y-%m-%dT%H:%M:%S")
                        }
                    )

                elif message_type == 'subscription':
                    statuses = ['active', 'expired', 'cancelled', 'pending']
                    status = statuses[i % len(statuses)]

                    send_subscription_update(
                        user_id=user.id,
                        subscription_data={
                            'status': status,
                            'plan_name': 'Premium Plan',
                            'amount': '29.99',
                            'currency': 'USD',
                            'next_billing': time.strftime("%Y-%m-%d")
                        }
                    )

                elif message_type == 'broadcast':
                    broadcast_system_message(
                        message=f'Broadcast message #{i + 1} sent at {time.strftime("%H:%M:%S")}',
                        level='info'
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Sent {message_type} message #{i + 1} to {user.username}'
                    )
                )

                if i < count - 1:  # Don't sleep after the last message
                    time.sleep(interval)

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Error sending {message_type} message #{i + 1}: {str(e)}'
                    )
                )