# Specification: Realtime Pub/Sub

## ADDED Requirements

### Requirement: WebSocket Connection Endpoint

The system SHALL provide a WebSocket endpoint at `/realtime/subscribe` that accepts client connections for realtime event subscriptions.

#### Scenario: Successful connection
- **WHEN** a client opens a WebSocket connection to `/realtime/subscribe`
- **THEN** the system accepts the connection and assigns a unique connection ID
- **AND** the system tracks the connection in the subscription broker

#### Scenario: Authenticated connection
- **WHEN** an authenticated user opens a WebSocket connection
- **THEN** the system associates the user's authentication context with the connection
- **AND** the user can subscribe to collections they have permission to access

#### Scenario: Connection cleanup
- **WHEN** a WebSocket connection is closed
- **THEN** the system removes all subscriptions for that connection
- **AND** the system removes the connection from the subscription broker

### Requirement: Collection Subscription

The system SHALL allow clients to subscribe to collections using subscription patterns and receive events when records in those collections change.

#### Scenario: Subscribe to all records in a collection
- **WHEN** a client sends a subscribe message with pattern `posts.*`
- **THEN** the client receives events for all create/update/delete operations on post records

#### Scenario: Subscribe to specific record
- **WHEN** a client sends a subscribe message with pattern `posts.123`
- **THEN** the client receives events only for changes to post record with ID 123

#### Scenario: Subscribe to all collections
- **WHEN** an admin user sends a subscribe message with pattern `*`
- **THEN** the client receives events for all record changes in all collections

#### Scenario: Multiple subscriptions per connection
- **WHEN** a client sends multiple subscribe messages
- **THEN** the system tracks all subscriptions for that connection
- **AND** the client receives events matching any of their subscriptions

### Requirement: Unsubscribe from Collections

The system SHALL allow clients to unsubscribe from previously subscribed collections.

#### Scenario: Unsubscribe from specific collection
- **WHEN** a client sends an unsubscribe message with pattern `posts.*`
- **THEN** the system removes that subscription
- **AND** the client stops receiving events for that pattern

#### Scenario: Unsubscribe from all
- **WHEN** a client sends an unsubscribe message with pattern `*`
- **THEN** the system removes all subscriptions for that connection
- **AND** the client stops receiving all realtime events

### Requirement: Automatic CRUD Event Broadcasting

The system SHALL automatically broadcast realtime events when records are created, updated, or deleted through the ORM.

#### Scenario: Record creation event
- **WHEN** a new post record is created
- **THEN** the system broadcasts a create event to all clients subscribed to `posts.*`
- **AND** the event includes the complete record data

#### Scenario: Record update event
- **WHEN** an existing post record is updated
- **THEN** the system broadcasts an update event to all clients subscribed to `posts.*`
- **AND** the event includes the updated record data

#### Scenario: Record deletion event
- **WHEN** a post record is deleted
- **THEN** the system broadcasts a delete event to all clients subscribed to `posts.*`
- **AND** the event includes the record ID

#### Scenario: Specific record subscription
- **WHEN** a post with ID 123 is updated
- **THEN** clients subscribed to `posts.123` receive the update event
- **AND** clients subscribed to `posts.*` also receive the update event

### Requirement: Event Message Format

The system SHALL send realtime events in a standardized JSON format with consistent fields.

#### Scenario: Create event format
- **WHEN** a record create event is broadcast
- **THEN** the event message includes:
  - `type`: "record_event"
  - `collection`: collection name (e.g., "posts")
  - `action`: "create"
  - `record`: complete record data as JSON object
  - `timestamp`: ISO 8601 timestamp

#### Scenario: Update event format
- **WHEN** a record update event is broadcast
- **THEN** the event message includes:
  - `type`: "record_event"
  - `collection`: collection name
  - `action`: "update"
  - `record`: updated record data as JSON object
  - `timestamp`: ISO 8601 timestamp

#### Scenario: Delete event format
- **WHEN** a record delete event is broadcast
- **THEN** the event message includes:
  - `type`: "record_event"
  - `collection`: collection name
  - `action`: "delete"
  - `record`: object with at least `id` field
  - `timestamp`: ISO 8601 timestamp

### Requirement: Custom Event Broadcasting

The system SHALL provide an API for application code to broadcast custom realtime events to connected clients.

#### Scenario: Broadcast custom event to collection subscribers
- **WHEN** application code calls `app.realtime.broadcast('notifications', {'message': 'Hello'})`
- **THEN** all clients subscribed to `notifications.*` receive the custom event
- **AND** the event type is "custom_event"

#### Scenario: Broadcast to all clients
- **WHEN** application code calls `app.realtime.broadcast_all({'announcement': 'System maintenance'})`
- **THEN** all connected clients receive the event regardless of subscriptions

### Requirement: Client Connection Tracking

The system SHALL track active client connections with their authentication context and subscriptions.

#### Scenario: Connection metadata storage
- **WHEN** a client connects
- **THEN** the system stores:
  - Unique connection ID
  - WebSocket connection object
  - List of active subscriptions
  - Authenticated user (if any)
  - Connection timestamp

#### Scenario: Authentication context retrieval
- **WHEN** the system needs to check permissions for a subscription
- **THEN** the system can retrieve the authenticated user from the connection metadata

#### Scenario: Connection listing
- **WHEN** application code calls `app.realtime.get_connections()`
- **THEN** the system returns all active connection metadata

### Requirement: Subscription Pattern Matching

The system SHALL match subscription patterns against events to determine which clients receive which events.

#### Scenario: Exact collection match
- **WHEN** an event occurs for collection "posts"
- **THEN** clients subscribed to `posts.*` receive the event

#### Scenario: Specific record match
- **WHEN** an event occurs for posts record ID 123
- **THEN** clients subscribed to `posts.123` receive the event
- **AND** clients subscribed to `posts.*` also receive the event

#### Scenario: Wildcard match
- **WHEN** an event occurs for any collection
- **THEN** clients subscribed to `*` receive the event

#### Scenario: No match
- **WHEN** an event occurs for collection "posts"
- **THEN** clients subscribed only to `comments.*` do NOT receive the event

### Requirement: Connection Health Monitoring

The system SHALL monitor WebSocket connection health to detect and clean up stale connections.

#### Scenario: Heartbeat ping
- **WHEN** a WebSocket connection is active
- **THEN** the system sends periodic ping messages
- **AND** expects pong responses within a timeout period

#### Scenario: Stale connection cleanup
- **WHEN** a connection fails to respond to pings
- **THEN** the system closes the WebSocket connection
- **AND** removes all subscriptions for that connection

### Requirement: Permission Validation

The system SHALL validate that clients have permission to subscribe to collections based on authentication context.

#### Scenario: Unauthorized subscription attempt
- **WHEN** an unauthenticated client attempts to subscribe to a protected collection
- **THEN** the system rejects the subscription
- **AND** sends an error message to the client

#### Scenario: Authorized subscription
- **WHEN** an authenticated user subscribes to a collection they can access
- **THEN** the system accepts the subscription
- **AND** begins sending events to the client

#### Scenario: Admin wildcard subscription
- **WHEN** an admin user subscribes to `*`
- **THEN** the system accepts the subscription
- **AND** sends all events to the client

### Requirement: Error Handling

The system SHALL handle errors gracefully and inform clients of issues without crashing connections.

#### Scenario: Invalid subscription pattern
- **WHEN** a client sends a malformed subscription pattern
- **THEN** the system sends an error message to the client
- **AND** keeps the connection open

#### Scenario: Serialization error
- **WHEN** a record cannot be serialized to JSON
- **THEN** the system logs the error
- **AND** does not send the event to subscribed clients
- **AND** continues processing other events

#### Scenario: Client disconnect during broadcast
- **WHEN** a client disconnects while an event is being sent
- **THEN** the system handles the error gracefully
- **AND** removes the connection from the subscription broker
- **AND** continues broadcasting to other clients

### Requirement: Subscription Limits

The system SHALL enforce limits on the number of subscriptions per connection to prevent resource exhaustion.

#### Scenario: Subscription limit enforcement
- **WHEN** a client attempts to exceed the maximum subscription limit (default 100)
- **THEN** the system rejects the subscription
- **AND** sends an error message indicating the limit was reached

#### Scenario: Rate limiting
- **WHEN** a client sends subscription requests too rapidly (default 10/second)
- **THEN** the system rejects subsequent requests temporarily
- **AND** sends a rate limit error message

