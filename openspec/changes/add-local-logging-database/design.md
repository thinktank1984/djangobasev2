## Context

This design document explains the technical architecture for implementing a local-only dedicated logging database in the Django SaaS boilerplate. The current application lacks comprehensive logging infrastructure, and adding a separate SQLite database for logs provides better observability without external dependencies.

**Constraints and Stakeholders:**
- Development team needs immediate access to logs without external services
- Production environments require minimal performance impact
- Security requirements mandate local storage of sensitive logs
- Operations team needs manageable log rotation and maintenance

## Goals / Non-Goals

**Goals:**
- Separate operational logs from business data for better data management
- Provide immediate local access to all logs without external dependencies
- Maintain Django conventions and compatibility with existing architecture
- Enable comprehensive audit trails for compliance and debugging
- Support high-volume logging with minimal performance impact

**Non-Goals:**
- Real-time log analysis dashboards (can be added later)
- External log service integration (beyond existing Bugsink integration)
- Complex log parsing and transformation (keep it simple)
- Cross-database joins (handled at application level)

## Decisions

### Decision 1: SQLite for Logging Database
**What:** Use SQLite as the dedicated logging database alongside PostgreSQL for business data.

**Why:**
- Zero operational overhead - no additional services required
- Excellent performance for write-heavy logging workloads
- Simple file-based backup and maintenance
- Mature Django integration with built-in SQLite backend
- Perfect for local-only requirement without external dependencies

**Alternatives considered:**
- PostgreSQL with separate database: More complex setup and resource usage
- In-memory logging: Not persistent across restarts
- File-based logs: Less structured and harder to query

### Decision 2: Django Database Router Pattern
**What:** Implement a custom Django database router to automatically direct logging models to SQLite.

**Why:**
- Transparent to application code - no need to specify database manually
- Leverages Django's built-in multi-database capabilities
- Clean separation of concerns with central routing logic
- Follows Django best practices for multi-database applications

**Alternatives considered:**
- Manual database specification: More verbose and error-prone
- Separate logging service: Overkill for current requirements

### Decision 3: Unified SystemLog Model
**What:** Create a single SystemLog model to store all types of operational logs.

**Why:**
- Simplifies querying and analysis across log types
- Consistent structure for all log entries
- Flexible JSON metadata field for varied data types
- Efficient storage with proper indexing

**Alternatives considered:**
- Separate models per log type: More complex querying and maintenance
- Document-based storage: Less integration with Django admin

### Decision 4: Django Admin Integration
**What:** Use Django admin as the primary interface for viewing and managing logs.

**Why:**
- Built-in interface that developers are familiar with
- Automatic forms, filtering, and search capabilities
- No additional frontend dependencies
- Easy to customize and extend

**Alternatives considered:**
- Custom web interface: More development effort required
- CLI-only interface: Less accessible for visual inspection

## Risks / Trade-offs

### Risk 1: Performance Impact
**Risk:** Additional database operations could slow down request processing.

**Mitigation:**
- Use optimized database routing to minimize overhead
- Implement async log writing where possible
- Add proper database indexes for common queries
- Consider log level thresholds for production

### Risk 2: Database Size Growth
**Risk:** SQLite database could grow indefinitely and consume disk space.

**Mitigation:**
- Implement automatic log rotation and cleanup
- Provide management commands for manual maintenance
- Monitor disk usage and set appropriate retention policies
- Use Docker volume mounts for persistent storage management

### Risk 3: Cross-Database Query Complexity
**Risk:** Querying related data across PostgreSQL and SQLite could be complex.

**Mitigation:**
- Store foreign references as integer fields without constraints
- Handle joins at application level when needed
- Optimize common query patterns with proper indexing
- Document the query patterns for developers

### Trade-off: Query Flexibility vs Performance
**Trade-off:** JSON metadata provides flexibility but may impact query performance.

**Resolution:**
- Index common metadata fields for frequent queries
- Use JSON field queries sparingly in performance-critical paths
- Provide both structured fields and flexible metadata storage
- Monitor query performance and optimize as needed

## Migration Plan

### Phase 1: Infrastructure Setup
1. Update Django settings for multi-database configuration
2. Create database router and logging app structure
3. Configure Docker volume mounting for log persistence
4. Test basic database connectivity

### Phase 2: Core Logging Implementation
1. Implement SystemLog model and basic admin interface
2. Create Django logging handler and middleware
3. Add management commands for log viewing and maintenance
4. Test basic logging functionality

### Phase 3: Advanced Features
1. Implement audit logging for model changes
2. Add security and privacy controls
3. Optimize performance with proper indexing
4. Implement automated cleanup processes

### Phase 4: Testing and Documentation
1. Create comprehensive test suite
2. Write documentation and examples
3. Validate in production-like environment
4. Train development team on usage

### Rollback Plan
- Remove logging app from INSTALLED_APPS
- Delete logging database router from settings
- Remove database configuration for logging database
- All changes are additive and can be safely reverted

## Open Questions

1. **Log Retention Period:** What should be the default retention period for different log levels?
2. **Performance Monitoring:** Should we implement performance metrics logging automatically?
3. **Export Formats:** What export formats should be supported for log data analysis?
4. **Access Control:** Should log viewing be restricted to certain user roles beyond superusers?

These questions can be addressed during implementation based on team feedback and requirements.