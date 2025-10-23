"""
Tests for real-time notification functionality.
"""

import json
from unittest.mock import patch, MagicMock
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from .consumers import NotificationConsumer, PresenceConsumer
from .models import Notification, UserPresence
from core.asgi import application

User = get_user_model()


class NotificationConsumerTests(TestCase):
    """Test cases for NotificationConsumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @database_sync_to_async
    def create_notification(self, user, title, message, level='info'):
        """Create a notification for testing."""
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            level=level
        )

    async def test_notification_consumer_connects_with_authenticated_user(self):
        """Test that authenticated users can connect to the notification consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
        )

        # Simulate authenticated user
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
        self.assertEqual(response['user_id'], self.user.id)

        # Test unread count message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'unread_count')
        self.assertEqual(response['count'], 0)

        await communicator.disconnect()

    async def test_notification_consumer_rejects_anonymous_users(self):
        """Test that anonymous users cannot connect to the notification consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
        )

        # Simulate anonymous user
        communicator.scope['user'] = MagicMock()
        communicator.scope['user'].is_anonymous = True

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_mark_notification_as_read(self):
        """Test marking a notification as read via WebSocket."""
        # Create a notification
        notification = await self.create_notification(
            self.user,
            'Test Notification',
            'This is a test notification'
        )

        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Send mark as read message
        await communicator.send_json_to({
            'type': 'mark_as_read',
            'notification_id': notification.id
        })

        # Receive confirmation
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'notification_marked_read')
        self.assertEqual(response['notification_id'], notification.id)

        await communicator.disconnect()

        # Verify notification is marked as read in database
        await database_sync_to_async(notification.refresh_from_db)()
        self.assertTrue(notification.is_read)

    async def test_request_notifications(self):
        """Test requesting notifications list."""
        # Create some notifications
        await self.create_notification(
            self.user,
            'Test 1',
            'First test notification'
        )
        await self.create_notification(
            self.user,
            'Test 2',
            'Second test notification'
        )

        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip initial messages
        await communicator.receive_json_from()  # connection_established
        await communicator.receive_json_from()  # unread_count

        # Request notifications
        await communicator.send_json_to({
            'type': 'request_notifications'
        })

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'notifications_list')
        self.assertIsInstance(response['data'], list)
        self.assertEqual(len(response['data']), 2)

        await communicator.disconnect()


class PresenceConsumerTests(TestCase):
    """Test cases for PresenceConsumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    async def test_presence_consumer_connects_with_authenticated_user(self):
        """Test that authenticated users can connect to the presence consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/presence/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')

        await communicator.disconnect()

    async def test_presence_consumer_rejects_anonymous_users(self):
        """Test that anonymous users cannot connect to the presence consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/presence/',
        )
        communicator.scope['user'] = MagicMock()
        communicator.scope['user'].is_anonymous = True

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)


class NotificationModelTests(TestCase):
    """Test cases for Notification model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_notification(self):
        """Test creating a notification."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            level='info'
        )

        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.level, 'info')
        self.assertFalse(notification.is_read)

    def test_mark_as_read(self):
        """Test marking notification as read."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification'
        )

        self.assertFalse(notification.is_read)

        notification.mark_as_read()
        self.assertTrue(notification.is_read)

    @patch('channels.layers.get_channel_layer')
    def test_create_notification_with_real_time(self, mock_get_channel_layer):
        """Test creating notification with real-time sending."""
        # Mock channel layer
        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer

        notification = Notification.create_notification(
            user=self.user,
            title='Real-time Notification',
            message='This should be sent via WebSocket',
            level='success'
        )

        # Verify notification was created
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Real-time Notification')

        # Verify channel layer was called
        mock_channel_layer.group_send.assert_called_once()


class NotificationUtilsTests(TestCase):
    """Test cases for notification utility functions."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    @patch('channels.layers.get_channel_layer')
    def test_send_notification(self, mock_get_channel_layer):
        """Test sending notification via utility function."""
        from .utils import send_notification

        mock_channel_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_channel_layer

        send_notification(
            user_id=self.user.id,
            title='Test Notification',
            message='Test message',
            level='info'
        )

        # Verify channel layer was called
        mock_channel_layer.group_send.assert_called_once()

        # Verify notification was created in database
        notification = Notification.objects.get(user=self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'Test message')


class UserPresenceModelTests(TestCase):
    """Test cases for UserPresence model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_set_user_online(self):
        """Test setting user as online."""
        presence = UserPresence.set_user_online(self.user)

        self.assertEqual(presence.user, self.user)
        self.assertTrue(presence.is_online)

        # Test updating existing presence
        presence2 = UserPresence.set_user_online(self.user)
        self.assertEqual(presence.id, presence2.id)
        self.assertTrue(presence2.is_online)

    def test_set_user_offline(self):
        """Test setting user as offline."""
        # First set user online
        UserPresence.set_user_online(self.user)

        # Then set offline
        UserPresence.set_user_offline(self.user)

        presence = UserPresence.objects.get(user=self.user)
        self.assertFalse(presence.is_online)

    def test_get_online_users(self):
        """Test getting list of online users."""
        # Create another user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )

        # Set first user online
        UserPresence.set_user_online(self.user)

        # Get online users
        online_users = UserPresence.get_online_users()
        self.assertEqual(len(online_users), 1)
        self.assertEqual(online_users[0].user, self.user)

        # Set second user online
        UserPresence.set_user_online(user2)

        # Get online users again
        online_users = UserPresence.get_online_users()
        self.assertEqual(len(online_users), 2)