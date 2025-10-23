"""
Tests for real-time subscription functionality.
"""

import json
from unittest.mock import patch, MagicMock
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from .consumers import SubscriptionConsumer, SubscriptionAdminConsumer
from core.asgi import application

User = get_user_model()


class SubscriptionConsumerTests(TestCase):
    """Test cases for SubscriptionConsumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    async def test_subscription_consumer_connects_with_authenticated_user(self):
        """Test that authenticated users can connect to the subscription consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
        self.assertEqual(response['user_id'], self.user.id)

        await communicator.disconnect()

    async def test_subscription_consumer_rejects_anonymous_users(self):
        """Test that anonymous users cannot connect to the subscription consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/',
        )
        communicator.scope['user'] = MagicMock()
        communicator.scope['user'].is_anonymous = True

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_request_subscription_status(self):
        """Test requesting subscription status."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Request subscription status
        await communicator.send_json_to({
            'type': 'request_subscription_status'
        })

        # Receive subscription status (dummy data since model doesn't exist)
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'subscription_status')
        self.assertIn('data', response)
        self.assertEqual(response['data']['total_active_count'], 0)

        await communicator.disconnect()

    async def test_request_subscription_history(self):
        """Test requesting subscription history."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Request subscription history
        await communicator.send_json_to({
            'type': 'request_subscription_history'
        })

        # Receive subscription history (dummy data since model doesn't exist)
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'subscription_history')
        self.assertIn('data', response)
        self.assertIsInstance(response['data'], list)

        await communicator.disconnect()


class SubscriptionAdminConsumerTests(TestCase):
    """Test cases for SubscriptionAdminConsumer."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='regularpass123'
        )

    async def test_subscription_admin_consumer_connects_with_staff_user(self):
        """Test that staff users can connect to the subscription admin consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/admin/',
        )
        communicator.scope['user'] = self.admin_user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'admin_connection_established')

        await communicator.disconnect()

    async def test_subscription_admin_consumer_rejects_non_staff_users(self):
        """Test that non-staff users cannot connect to the subscription admin consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/admin/',
        )
        communicator.scope['user'] = self.regular_user

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_request_subscription_stats(self):
        """Test requesting subscription stats as admin."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/subscriptions/admin/',
        )
        communicator.scope['user'] = self.admin_user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Request subscription stats
        await communicator.send_json_to({
            'type': 'request_subscription_stats'
        })

        # Receive subscription stats (dummy data since model doesn't exist)
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'subscription_stats')
        self.assertIn('data', response)
        self.assertIn('total_subscriptions', response['data'])
        self.assertIn('active_subscriptions', response['data'])
        self.assertIn('inactive_subscriptions', response['data'])

        await communicator.disconnect()