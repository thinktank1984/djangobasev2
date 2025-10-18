# Design: Add Realtime Pub/Sub Support

## Context

The application uses Emmett framework which includes built-in WebSocket support. Users need realtime notifications when data changes occur. This is inspired by PocketBase's realtime API which provides automatic event broadcasting for record changes and custom event support.

The system should work in single-process development mode and be extensible to support distributed deployments with Redis pub/sub if needed later.

## Goals / Non-Goals

### Goals
- Provide WebSocket-based realtime event subscription for clients
- Automatically broadcast CRUD events when records change
- Support wildcard subscriptions to collections (e.g., `posts.*` for all post records)
- Allow custom event broadcasting from application code
- Track client connections with authentication context
- Work in single-process mode without external dependencies
- Use Emmett's native WebSocket support

### Non-Goals
- Building a full message queue system
- Supporting complex query-based subscriptions (initial version)
- Implementing distributed pub/sub with Redis (can be added later)
- Replacing REST API with realtime-only interface
- Implementing complex event filtering beyond collection/record patterns

## Decisions

### Architecture: In-Process Subscription Broker

**Decision**: Implement subscription management in-process using Python data structures.

**Rationale**:
- Emmett WebSocket support handles connection management
- Single-process development is the primary use case
- Simpler to implement and maintain
- Can be extended to Redis later without API changes
- Follows "simplicity first" principle from OpenSpec

**Alternatives Considered**:
- Redis pub/sub from day one: Adds external dependency and complexity; not needed until horizontal scaling is required
- SSE (Server-Sent Events): One-way only; WebSocket provides bidirectional communication for more flexibility

### Event Format: JSON with Standard Fields

**Decision**: Use JSON format with standard fields:
```json
{
  "type": "record_event",
  "collection": "posts",
  "action": "create",
  "record": {
    "id": 123,
    "title": "New Post",
    ...
  },
  "timestamp": "2025-10-12T10:30:00Z"
}
```

**Rationale**:
- JSON is universal and easy to parse in JavaScript
- Standard fields make client code predictable
- Extensible for future metadata

### Subscription Pattern: Collection.Wildcard

**Decision**: Support subscription patterns like `posts.*` (all posts) or `posts.123` (specific post).

**Rationale**:
- Matches PocketBase API which users may be familiar with
- Simple wildcard matching is easy to implement
- Provides flexibility without complex query language
- `*` alone subscribes to all collections (admin use case)

**Alternatives Considered**:
- Complex query filters: Too complex for initial version
- Only collection-level subscriptions: Too coarse-grained

### ORM Integration: Model Callbacks

**Decision**: Use Emmett ORM's callback system (after_insert, after_update, after_delete) to automatically emit events.

**Rationale**:
- Emmett models already support callbacks via `set_callback()`
- Automatic - no need to manually emit events in application code
- Centralized in BaseModel for consistency
- Can be disabled per-model if needed

### Client Connection Tracking

**Decision**: Store connections in a dictionary keyed by unique connection ID with metadata:
```python
connections = {
    "conn-uuid-1": {
        "websocket": ws,
        "subscriptions": ["posts.*", "comments.*"],
        "auth_user": user_record,
        "connected_at": timestamp
    }
}
```

**Rationale**:
- Simple lookup for broadcasting
- Can check authentication per connection
- Easy to clean up on disconnect

### API for Custom Events

**Decision**: Provide `app.realtime.broadcast(collection, event_data)` method.

**Rationale**:
- Simple API for application code
- Matches subscription pattern (clients subscribe to collections)
- Can be used for custom non-CRUD events

## Risks / Trade-offs

### Risk: Memory Usage with Many Connections

**Mitigation**: 
- Implement connection limits
- Monitor active connection count
- Document scalability limits
- Plan for Redis-backed broker in future

### Risk: Event Storms

Many rapid CRUD operations could generate excessive events.

**Mitigation**:
- Rate limiting on subscription endpoint
- Consider debouncing/batching events (future optimization)
- Allow clients to unsubscribe easily

### Trade-off: Single Process vs Distributed

Current design works only in single process.

**Mitigation**:
- Document this limitation
- Design API to support Redis backend later
- Most development and small deployments are single-process

### Risk: Authentication Context Loss

WebSocket connections are long-lived; user permissions might change.

**Mitigation**:
- Revalidate permissions periodically (future enhancement)
- Document that permissions are checked at subscription time
- Consider adding session timeout

## Migration Plan

This is net-new functionality with no migration needed.

### Rollout Steps
1. Implement in development environment
2. Add feature flag or environment variable to enable/disable
3. Test with sample applications
4. Document usage patterns
5. Enable by default

### Rollback
- Remove WebSocket routes
- Remove ORM hooks
- No data migration needed

## Open Questions

1. **Rate Limiting**: What are appropriate limits for subscription requests per client?
   - *Suggestion*: Start with 100 subscriptions per connection, 10 subscribe requests per second

2. **Event History**: Should clients receive events that occurred while disconnected?
   - *Suggestion*: No for initial version; clients should poll on reconnect

3. **Permissions**: How do we check if a user can subscribe to a collection?
   - *Suggestion*: Use existing model permissions; admin can subscribe to all

4. **Event Size**: Should we limit the size of record data in events?
   - *Suggestion*: Include full record data initially; add field selection later if needed

5. **Compression**: Should we compress WebSocket messages?
   - *Suggestion*: Not needed initially; can add if bandwidth becomes an issue

