"""
Tests for real-time dashboard functionality.
"""

import json
from unittest.mock import patch, MagicMock
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

from .consumers import DashboardConsumer, AdminDashboardConsumer
from core.asgi import application

User = get_user_model()


class DashboardConsumerTests(TestCase):
    """Test cases for DashboardConsumer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    async def test_dashboard_consumer_connects_with_authenticated_user(self):
        """Test that authenticated users can connect to the dashboard consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
        self.assertEqual(response['user_id'], self.user.id)

        await communicator.disconnect()

    async def test_dashboard_consumer_rejects_anonymous_users(self):
        """Test that anonymous users cannot connect to the dashboard consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/',
        )
        communicator.scope['user'] = MagicMock()
        communicator.scope['user'].is_anonymous = True

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_heartbeat(self):
        """Test heartbeat functionality."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Send heartbeat
        await communicator.send_json_to({
            'type': 'heartbeat',
            'timestamp': '2023-01-01T00:00:00Z'
        })

        # Receive heartbeat response
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'heartbeat_response')
        self.assertEqual(response['timestamp'], '2023-01-01T00:00:00Z')

        await communicator.disconnect()

    async def test_request_dashboard_update(self):
        """Test requesting dashboard update."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Request dashboard update
        await communicator.send_json_to({
            'type': 'request_dashboard_update'
        })

        # Receive dashboard update (dummy data since model doesn't exist)
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'dashboard_update')
        self.assertIn('data', response)
        self.assertEqual(response['data']['total_subscriptions'], 0)

        await communicator.disconnect()


class AdminDashboardConsumerTests(TestCase):
    """Test cases for AdminDashboardConsumer."""

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

    async def test_admin_dashboard_consumer_connects_with_staff_user(self):
        """Test that staff users can connect to the admin dashboard consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/admin/',
        )
        communicator.scope['user'] = self.admin_user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test connection confirmation message
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'admin_connection_established')

        await communicator.disconnect()

    async def test_admin_dashboard_consumer_rejects_non_staff_users(self):
        """Test that non-staff users cannot connect to the admin dashboard consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/admin/',
        )
        communicator.scope['user'] = self.regular_user

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_admin_dashboard_consumer_rejects_anonymous_users(self):
        """Test that anonymous users cannot connect to the admin dashboard consumer."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/admin/',
        )
        communicator.scope['user'] = MagicMock()
        communicator.scope['user'].is_anonymous = True

        connected, subprotocol = await communicator.connect()
        self.assertFalse(connected)

    async def test_request_system_stats(self):
        """Test requesting system stats as admin."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/dashboard/admin/',
        )
        communicator.scope['user'] = self.admin_user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Skip connection message
        await communicator.receive_json_from()

        # Request system stats
        await communicator.send_json_to({
            'type': 'request_system_stats'
        })

        # Receive system stats
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'system_stats')
        self.assertIn('data', response)
        self.assertIn('total_users', response['data'])
        self.assertIn('active_users', response['data'])
        self.assertIn('staff_users', response['data'])

        await communicator.disconnect()