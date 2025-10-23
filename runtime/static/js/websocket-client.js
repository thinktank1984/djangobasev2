/**
 * WebSocket client for real-time communication with Django Channels.
 */

class WebSocketClient {
    constructor(url, onMessage = null, onOpen = null, onClose = null, onError = null) {
        this.url = url;
        this.onMessage = onMessage;
        this.onOpen = onOpen;
        this.onClose = onClose;
        this.onError = onError;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 5000; // 5 seconds
        this.isConnecting = false;
    }

    connect() {
        if (this.isConnecting || (this.socket && this.socket.readyState === WebSocket.OPEN)) {
            return;
        }

        this.isConnecting = true;

        try {
            this.socket = new WebSocket(this.url);

            this.socket.onopen = (event) => {
                console.log('WebSocket connected:', event);
                this.isConnecting = false;
                this.reconnectAttempts = 0;

                if (this.onOpen) {
                    this.onOpen(event);
                }

                // Start heartbeat
                this.startHeartbeat();
            };

            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    console.log('WebSocket message received:', data);

                    if (this.onMessage) {
                        this.onMessage(data);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.socket.onclose = (event) => {
                console.log('WebSocket disconnected:', event);
                this.isConnecting = false;
                this.stopHeartbeat();

                if (this.onClose) {
                    this.onClose(event);
                }

                // Attempt to reconnect
                if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.attemptReconnect();
                }
            };

            this.socket.onerror = (event) => {
                console.error('WebSocket error:', event);
                this.isConnecting = false;

                if (this.onError) {
                    this.onError(event);
                }
            };

        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.isConnecting = false;
        }
    }

    disconnect() {
        this.stopHeartbeat();
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            try {
                const message = typeof data === 'string' ? data : JSON.stringify(data);
                this.socket.send(message);
                console.log('WebSocket message sent:', data);
            } catch (error) {
                console.error('Error sending WebSocket message:', error);
            }
        } else {
            console.warn('WebSocket is not connected. Message not sent:', data);
        }
    }

    attemptReconnect() {
        this.reconnectAttempts++;
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect();
        }, this.reconnectInterval);
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            this.send({
                type: 'heartbeat',
                timestamp: new Date().toISOString()
            });
        }, 30000); // Send heartbeat every 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    isConnected() {
        return this.socket && this.socket.readyState === WebSocket.OPEN;
    }
}

/**
 * Dashboard WebSocket Client
 */
class DashboardClient extends WebSocketClient {
    constructor(onDashboardUpdate = null, onNotification = null) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const url = `${protocol}//${host}/ws/dashboard/`;

        super(url, null, null, null, null);

        this.onDashboardUpdate = onDashboardUpdate;
        this.onNotification = onNotification;

        // Set up message handling
        this.onMessage = (data) => {
            switch (data.type) {
                case 'connection_established':
                    console.log('Dashboard connection established');
                    break;
                case 'dashboard_update':
                    if (this.onDashboardUpdate) {
                        this.onDashboardUpdate(data.data);
                    }
                    break;
                case 'notification':
                    if (this.onNotification) {
                        this.onNotification(data);
                    }
                    break;
                case 'heartbeat_response':
                    // Handle heartbeat response
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        };
    }

    requestDashboardUpdate() {
        this.send({
            type: 'request_dashboard_update'
        });
    }
}

/**
 * Subscription WebSocket Client
 */
class SubscriptionClient extends WebSocketClient {
    constructor(onStatusUpdate = null, onPaymentConfirmation = null, onExpiryWarning = null) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const url = `${protocol}//${host}/ws/subscriptions/`;

        super(url, null, null, null, null);

        this.onStatusUpdate = onStatusUpdate;
        this.onPaymentConfirmation = onPaymentConfirmation;
        this.onExpiryWarning = onExpiryWarning;

        // Set up message handling
        this.onMessage = (data) => {
            switch (data.type) {
                case 'connection_established':
                    console.log('Subscription connection established');
                    break;
                case 'subscription_status_update':
                    if (this.onStatusUpdate) {
                        this.onStatusUpdate(data.data);
                    }
                    break;
                case 'payment_confirmation':
                    if (this.onPaymentConfirmation) {
                        this.onPaymentConfirmation(data.data);
                    }
                    break;
                case 'subscription_expiry_warning':
                    if (this.onExpiryWarning) {
                        this.onExpiryWarning(data.data);
                    }
                    break;
                case 'subscription_status':
                    // Handle subscription status response
                    break;
                case 'subscription_history':
                    // Handle subscription history response
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        };
    }

    requestSubscriptionStatus() {
        this.send({
            type: 'request_subscription_status'
        });
    }

    requestSubscriptionHistory() {
        this.send({
            type: 'request_subscription_history'
        });
    }
}

/**
 * Notification WebSocket Client
 */
class NotificationClient extends WebSocketClient {
    constructor(onNewNotification = null, onUnreadCount = null, onNotificationRead = null) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const url = `${protocol}//${host}/ws/notifications/`;

        super(url, null, null, null, null);

        this.onNewNotification = onNewNotification;
        this.onUnreadCount = onUnreadCount;
        this.onNotificationRead = onNotificationRead;

        // Set up message handling
        this.onMessage = (data) => {
            switch (data.type) {
                case 'connection_established':
                    console.log('Notifications connection established');
                    break;
                case 'new_notification':
                    if (this.onNewNotification) {
                        this.onNewNotification(data.data);
                    }
                    break;
                case 'unread_count':
                    if (this.onUnreadCount) {
                        this.onUnreadCount(data.count);
                    }
                    break;
                case 'notification_read':
                    if (this.onNotificationRead) {
                        this.onNotificationRead(data.data);
                    }
                    break;
                case 'notifications_list':
                    // Handle notifications list response
                    break;
                case 'all_notifications_marked_read':
                    // Handle all notifications marked as read
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        };
    }

    requestNotifications() {
        this.send({
            type: 'request_notifications'
        });
    }

    markAsRead(notificationId) {
        this.send({
            type: 'mark_as_read',
            notification_id: notificationId
        });
    }

    markAllAsRead() {
        this.send({
            type: 'mark_all_as_read'
        });
    }

    requestUnreadCount() {
        this.send({
            type: 'request_unread_count'
        });
    }
}

/**
 * Presence WebSocket Client
 */
class PresenceClient extends WebSocketClient {
    constructor(onUserOnline = null, onUserOffline = null, onOnlineUsers = null) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const url = `${protocol}//${host}/ws/presence/`;

        super(url, null, null, null, null);

        this.onUserOnline = onUserOnline;
        this.onUserOffline = onUserOffline;
        this.onOnlineUsers = onOnlineUsers;

        // Set up message handling
        this.onMessage = (data) => {
            switch (data.type) {
                case 'connection_established':
                    console.log('Presence connection established');
                    break;
                case 'user_online':
                    if (this.onUserOnline) {
                        this.onUserOnline(data.data);
                    }
                    break;
                case 'user_offline':
                    if (this.onUserOffline) {
                        this.onUserOffline(data.data);
                    }
                    break;
                case 'online_users':
                    if (this.onOnlineUsers) {
                        this.onOnlineUsers(data.data);
                    }
                    break;
                default:
                    console.log('Unknown message type:', data.type);
            }
        };
    }
}

// Export classes for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        WebSocketClient,
        DashboardClient,
        SubscriptionClient,
        NotificationClient,
        PresenceClient
    };
}