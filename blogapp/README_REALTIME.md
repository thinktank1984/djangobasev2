# Real-time Pub/Sub Support with Django Channels

This document describes the implementation of real-time publish/subscribe functionality using Django Channels and Redis for WebSocket communication.

## Overview

The real-time system provides:
- **Real-time dashboard updates** - Live statistics and notifications for user dashboards
- **Subscription status updates** - Instant payment confirmations and subscription changes
- **Push notifications** - Real-time user notifications with different priority levels
- **User presence tracking** - Online/offline status for users
- **Admin monitoring** - Real-time alerts for administrators

## Architecture

### Components

1. **Django Channels** - WebSocket support and ASGI application
2. **Redis** - Channel layer for pub/sub messaging
3. **WebSocket Consumers** - Handle real-time connections and events
4. **Frontend JavaScript Client** - WebSocket client for browser integration
5. **Notification Models** - Database models for persistent notifications

### WebSocket Endpoints

- `/ws/dashboard/` - User dashboard updates
- `/ws/dashboard/admin/` - Admin dashboard updates (staff only)
- `/ws/subscriptions/` - Subscription status updates
- `/ws/subscriptions/admin/` - Admin subscription monitoring (staff only)
- `/ws/notifications/` - Real-time notifications
- `/ws/presence/` - User presence tracking

## Installation & Setup

### 1. Dependencies

The following packages are added to `requirements.txt`:
```
channels
channels-redis
redis
```

### 2. Configuration

In `core/settings.py`:
```python
# Add 'channels' to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'channels',
    'apps.notifications',  # New app for notifications
    # ... other apps
]

# ASGI configuration
ASGI_APPLICATION = 'core.asgi.application'

# Channels configuration
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### 3. ASGI Application

The `core/asgi.py` file is configured to handle both HTTP and WebSocket protocols:

```python
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(core.routing.websocket_urlpatterns)
        )
    ),
})
```

### 4. Redis Server

Make sure Redis is running on localhost:6379 or update the configuration accordingly:

```bash
# Start Redis server
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:alpine
```

## WebSocket Consumers

### Dashboard Consumer

Located in `apps/dashboard/consumers.py`:

```python
class DashboardConsumer(AsyncWebsocketConsumer):
    # Handles user-specific dashboard updates
    # Supports: dashboard updates, notifications, heartbeat
```

**Features:**
- Real-time dashboard statistics
- Live notifications
- Connection heartbeat for monitoring
- User-specific groups

### Subscription Consumer

Located in `apps/subscriptions/consumers.py`:

```python
class SubscriptionConsumer(AsyncWebsocketConsumer):
    # Handles subscription status updates
    # Supports: status updates, payment confirmations, expiry warnings
```

**Features:**
- Subscription status changes
- Payment confirmations
- Subscription expiry warnings
- Subscription history

### Notification Consumer

Located in `apps/notifications/consumers.py`:

```python
class NotificationConsumer(AsyncWebsocketConsumer):
    # Handles real-time notifications
    # Supports: new notifications, read/unread status
```

**Features:**
- Real-time push notifications
- Mark as read functionality
- Unread count tracking
- Different notification levels (info, success, warning, error)

### Presence Consumer

Located in `apps/notifications/consumers.py`:

```python
class PresenceConsumer(AsyncWebsocketConsumer):
    # Handles user presence tracking
    # Supports: online/offline status, user lists
```

**Features:**
- Online/offline user tracking
- Real-time user lists
- Join/leave announcements

## Frontend Integration

### JavaScript Client Library

The `static/js/websocket-client.js` file provides a comprehensive WebSocket client:

```javascript
// Dashboard updates
const dashboardClient = new DashboardClient(
    (data) => updateDashboardUI(data),
    (notification) => showNotification(notification)
);

// Notifications
const notificationClient = new NotificationClient(
    (notification) => handleNewNotification(notification),
    (count) => updateUnreadCount(count)
);

// User presence
const presenceClient = new PresenceClient(
    (user) => showUserOnline(user),
    (user) => showUserOffline(user)
);
```

### Example Templates

Three example templates demonstrate the functionality:

1. `templates/realtime/dashboard_example.html` - Real-time dashboard
2. `templates/realtime/notifications_example.html` - Notification system
3. `templates/realtime/presence_example.html` - User presence tracking

## Usage Examples

### Sending Notifications from Django

```python
from apps.notifications.utils import send_notification

# Send to a specific user
send_notification(
    user_id=user.id,
    title="New Subscription",
    message="Your subscription has been activated",
    level="success"
)

# Send dashboard updates
from apps.notifications.utils import send_dashboard_update

send_dashboard_update(
    user_id=user.id,
    data={
        'total_subscriptions': 5,
        'active_subscriptions': 3,
        'total_revenue': '99.99'
    }
)
```

### Sending Subscription Updates

```python
from apps.notifications.utils import (
    send_subscription_update,
    send_payment_confirmation
)

# Update subscription status
send_subscription_update(
    user_id=user.id,
    subscription_data={
        'status': 'active',
        'plan_name': 'Premium',
        'end_date': '2024-12-31'
    }
)

# Send payment confirmation
send_payment_confirmation(
    user_id=user.id,
    payment_data={
        'amount': '29.99',
        'currency': 'USD',
        'transaction_id': 'txn_123456'
    }
)
```

### Admin Alerts

```python
from apps.notifications.utils import send_admin_subscription_alert

# Alert admins about new subscription
send_admin_subscription_alert(
    'new_subscription',
    {
        'user_id': user.id,
        'username': user.username,
        'plan_name': 'Premium',
        'amount': '29.99'
    }
)
```

## Models

### Notification Model

```python
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)
```

### UserPresence Model

```python
class UserPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
```

## Testing

The implementation includes comprehensive tests:

### Test Coverage

- WebSocket connection handling
- Authentication and authorization
- Message sending and receiving
- Model functionality
- Utility functions
- Admin access controls

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.notifications
python manage.py test apps.dashboard
python manage.py test apps.subscriptions
```

### Example Test Structure

```python
class NotificationConsumerTests(TestCase):
    async def test_notification_consumer_connects_with_authenticated_user(self):
        communicator = WebsocketCommunicator(
            application,
            '/ws/notifications/',
        )
        communicator.scope['user'] = self.user

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'connection_established')
```

## Deployment Considerations

### Production Configuration

For production, consider:

1. **Redis Configuration**: Use a dedicated Redis server with persistence
2. **ASGI Server**: Use Daphne or Uvicorn instead of the development server
3. **Scaling**: Configure multiple Django instances with shared Redis
4. **Security**: Use WSS (WebSocket Secure) for HTTPS connections
5. **Monitoring**: Monitor WebSocket connections and Redis performance

### ASGI Server Example

```bash
# Using Daphne
daphne -b 0.0.0.0 -p 8000 core.asgi:application

# Using Uvicorn
uvicorn core.asgi:application --host 0.0.0.0 --port 8000
```

### Nginx Configuration

```nginx
upstream websocket {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location /ws/ {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Performance Optimization

### Best Practices

1. **Connection Limits**: Implement connection limits per user
2. **Message Batching**: Batch updates to reduce WebSocket traffic
3. **Connection Cleanup**: Properly handle disconnections
4. **Redis Optimization**: Use Redis pub/sub efficiently
5. **Frontend Optimization**: Debounce frequent updates

### Monitoring

Monitor:
- WebSocket connection counts
- Redis memory usage
- Message throughput
- Connection latency

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check Redis server is running
2. **403 Forbidden**: Verify user authentication
3. **Connection Drops**: Check network stability and server load
4. **Messages Not Received**: Verify channel layer configuration

### Debug Mode

Enable Django Channels debug mode:

```python
# settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
            'capacity': 1500,
            'expiry': 60,
        },
    },
}
```

## Security Considerations

1. **Authentication**: All WebSocket connections require authenticated users
2. **Authorization**: Admin endpoints require staff privileges
3. **Input Validation**: Validate all incoming WebSocket messages
4. **Rate Limiting**: Implement rate limiting for WebSocket connections
5. **CSRF Protection**: Use OriginValidator for WebSocket security

## Future Enhancements

Potential improvements:

1. **Chat System**: Real-time messaging between users
2. **File Sharing**: Real-time file upload/download progress
3. **Collaboration**: Real-time collaborative editing
4. **Analytics**: Real-time analytics and metrics
5. **Multi-tenancy**: Isolated real-time features per organization

## License

This implementation follows the same license as the main Django project.