"""
WebSocket routing configuration for the core application.
"""

from django.urls import re_path
from apps.dashboard.consumers import DashboardConsumer, AdminDashboardConsumer
from apps.subscriptions.consumers import SubscriptionConsumer, SubscriptionAdminConsumer
from apps.notifications.consumers import NotificationConsumer, PresenceConsumer

websocket_urlpatterns = [
    re_path(r'ws/dashboard/$', DashboardConsumer.as_asgi()),
    re_path(r'ws/dashboard/admin/$', AdminDashboardConsumer.as_asgi()),
    re_path(r'ws/subscriptions/$', SubscriptionConsumer.as_asgi()),
    re_path(r'ws/subscriptions/admin/$', SubscriptionAdminConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/presence/$', PresenceConsumer.as_asgi()),
]