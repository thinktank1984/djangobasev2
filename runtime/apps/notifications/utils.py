"""
Utilities for sending real-time messages via Django Channels.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User


def send_dashboard_update(user_id, data):
    """
    Send dashboard update to a specific user.

    Args:
        user_id (int): The user ID to send the update to
        data (dict): Dashboard data to send
    """
    channel_layer = get_channel_layer()
    user_group_name = f'dashboard_user_{user_id}'

    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'dashboard_update',
            'data': data
        }
    )


def send_notification(user_id, title, message, level='info', data=None):
    """
    Send a notification to a specific user via WebSocket and create database record.

    Args:
        user_id (int): The user ID to send the notification to
        title (str): Notification title
        message (str): Notification message
        level (str): Notification level (info, success, warning, error)
        data (dict): Additional notification data
    """
    try:
        user = User.objects.get(id=user_id)
        from .models import Notification

        # Create notification in database
        notification = Notification.create_notification(
            user=user,
            title=title,
            message=message,
            level=level,
            data=data or {}
        )

        return notification

    except User.DoesNotExist:
        # If user doesn't exist, still try to send WebSocket message
        channel_layer = get_channel_layer()
        user_group_name = f'notifications_user_{user_id}'

        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'notification_message',
                'message': message,
                'level': level
            }
        )


def send_subscription_update(user_id, subscription_data):
    """
    Send subscription status update to a specific user.

    Args:
        user_id (int): The user ID to send the update to
        subscription_data (dict): Subscription data to send
    """
    channel_layer = get_channel_layer()
    user_group_name = f'subscriptions_user_{user_id}'

    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'subscription_status_update',
            'data': subscription_data
        }
    )


def send_payment_confirmation(user_id, payment_data):
    """
    Send payment confirmation to a specific user.

    Args:
        user_id (int): The user ID to send the confirmation to
        payment_data (dict): Payment data to send
    """
    channel_layer = get_channel_layer()
    user_group_name = f'subscriptions_user_{user_id}'

    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'payment_confirmation',
            'data': payment_data
        }
    )


def send_subscription_expiry_warning(user_id, subscription_data):
    """
    Send subscription expiry warning to a specific user.

    Args:
        user_id (int): The user ID to send the warning to
        subscription_data (dict): Subscription data about to expire
    """
    channel_layer = get_channel_layer()
    user_group_name = f'subscriptions_user_{user_id}'

    async_to_sync(channel_layer.group_send)(
        user_group_name,
        {
            'type': 'subscription_expiry_warning',
            'data': subscription_data
        }
    )


def send_admin_dashboard_update(data):
    """
    Send dashboard update to all admin users.

    Args:
        data (dict): Dashboard data to send
    """
    channel_layer = get_channel_layer()
    admin_group_name = 'admin_dashboard'

    async_to_sync(channel_layer.group_send)(
        admin_group_name,
        {
            'type': 'system_update',
            'data': data
        }
    )


def send_admin_subscription_alert(alert_type, data):
    """
    Send subscription alert to all admin users.

    Args:
        alert_type (str): Type of alert (new_subscription, subscription_cancellation)
        data (dict): Alert data
    """
    channel_layer = get_channel_layer()
    admin_group_name = 'subscription_admin'

    message_type = f'{alert_type}_alert'

    async_to_sync(channel_layer.group_send)(
        admin_group_name,
        {
            'type': message_type,
            'data': data
        }
    )


def broadcast_system_message(message, level='info', target_groups=None):
    """
    Broadcast a system message to multiple user groups.

    Args:
        message (str): System message to broadcast
        level (str): Message level (info, success, warning, error)
        target_groups (list): List of user groups to send to (default: all authenticated users)
    """
    channel_layer = get_channel_layer()

    if target_groups is None:
        # Send to common groups
        groups = ['admin_dashboard', 'subscription_admin']
    else:
        groups = target_groups

    for group_name in groups:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'message': message,
                'level': level
            }
        )


def send_to_multiple_users(user_ids, message_data, message_type='notification_message'):
    """
    Send a message to multiple users.

    Args:
        user_ids (list): List of user IDs to send to
        message_data (dict): Message data to send
        message_type (str): Type of message
    """
    channel_layer = get_channel_layer()

    for user_id in user_ids:
        # Determine the appropriate group based on message type
        if 'dashboard' in message_type:
            group_name = f'dashboard_user_{user_id}'
        elif 'subscription' in message_type:
            group_name = f'subscriptions_user_{user_id}'
        else:
            group_name = f'notifications_user_{user_id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': message_type,
                **message_data
            }
        )