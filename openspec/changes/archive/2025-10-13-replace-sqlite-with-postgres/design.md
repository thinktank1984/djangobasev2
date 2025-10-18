# Design: Replace SQLite with PostgreSQL

## Context

The application currently uses SQLite as the database backend. While SQLite is excellent for development and testing, it has limitations for production use:
- File-based locking limits concurrent writes
- No network-based client-server model
- Limited scalability for high-traffic applications
- Weaker concurrency compared to PostgreSQL

PostgreSQL is already in use by the Bugsink error tracking service in the Docker environment, so adding a PostgreSQL instance for the main application fits the existing infrastructure pattern.

### Stakeholders
- Developers: Need reliable local development environment
- DevOps: Need production-ready database solution
- QA/Testing: Need consistent test database behavior

## Goals / Non-Goals

### Goals
- Replace SQLite with PostgreSQL as primary database
- Maintain development workflow simplicity via Docker
- Improve production readiness
- Support concurrent database operations
- Provide clear migration path from existing SQLite data

### Non-Goals
- Support both SQLite and PostgreSQL simultaneously
- Implement database-agnostic abstraction layer
- Add database replication or clustering (future work)
- Migrate to other databases (MySQL, MariaDB, etc.)

## Decisions

### Decision 1: PostgreSQL Version
**Choice**: PostgreSQL 16 (Alpine image)

**Rationale**:
- Latest stable release with excellent performance
- Alpine image reduces container size
- Matches Bugsink's PostgreSQL version (consistency)
- Well-supported by pyDAL

**Alternatives Considered**:
- PostgreSQL 15: Older but still supported (rejected: no compelling reason not to use 16)
- PostgreSQL 17: Too new, less battle-tested (rejected: prefer stability)

### Decision 2: Connection String Format
**Choice**: Environment variable with fallback to hardcoded default

**Rationale**:
- Flexibility for different environments (dev, staging, prod)
- Secure: avoid committing credentials
- Docker-friendly: use Docker Compose environment variables
- Fallback ensures development "just works"

**Format**:
```python
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://bloggy:bloggy_password@postgres:5432/bloggy'
)
app.config.db.uri = DATABASE_URL
```

**Alternatives Considered**:
- Hardcoded connection string: Rejected (not production-ready)
- Config file only: Rejected (less flexible than env vars)

### Decision 3: Connection Pool Settings
**Choice**: Pool size of 20 connections (up from 10)

**Rationale**:
- PostgreSQL handles concurrent connections better than SQLite
- Granian ASGI server benefits from larger connection pool
- 20 is reasonable default balancing performance and resource usage
- Can be overridden via environment variable

**Configuration**:
```python
app.config.db.pool_size = int(os.environ.get('DB_POOL_SIZE', '20'))
app.config.db.adapter_args = {
    'sslmode': 'prefer',  # Use SSL if available
}
```

**Alternatives Considered**:
- Keep pool_size=10: Rejected (underutilizes PostgreSQL capabilities)
- pool_size=50: Rejected (excessive for typical workload)

### Decision 4: Test Database Strategy
**Choice**: Use separate PostgreSQL database for tests with automatic cleanup

**Rationale**:
- Isolated test environment
- Real integration tests against actual database
- Consistent with "no mocking" policy
- pytest fixtures handle database lifecycle

**Implementation**:
```python
# conftest.py
@pytest.fixture(scope="session")
def test_db():
    """Create test database."""
    db_name = "bloggy_test"
    # Create database, run migrations
    yield db_name
    # Cleanup after all tests
```

**Alternatives Considered**:
- Shared database with transaction rollback: Rejected (less isolated)
- SQLite for tests, PostgreSQL for prod: Rejected (violates parity principle)

### Decision 5: Data Migration Approach
**Choice**: Manual export/import with documentation (no automated migration tool)

**Rationale**:
- One-time migration (not repeatable)
- Small dataset (development data)
- Emmett migrations handle schema
- Users can export/import or start fresh

**Process**:
1. Export SQLite data using emmett shell or custom script
2. Create fresh PostgreSQL database
3. Run emmett migrations to create schema
4. Import data using SQL INSERT statements or Python script
5. Verify data integrity

**Alternatives Considered**:
- pgloader tool: Rejected (adds dependency, overkill for small dataset)
- Automated migration script: Rejected (one-time operation, not worth complexity)

## Risks / Trade-offs

### Risk 1: Breaking Existing Development Environments
**Mitigation**: 
- Clear documentation in AGENTS.md and project.md
- Update error messages to point to PostgreSQL requirement
- Provide troubleshooting guide for common connection issues

### Risk 2: Test Execution Speed
**Trade-off**: PostgreSQL tests may be slightly slower than SQLite
**Mitigation**: 
- Use test database with optimized settings
- Connection pooling reduces overhead
- Benefits of real integration tests outweigh minor speed difference

### Risk 3: Data Loss During Migration
**Mitigation**:
- Document export process clearly
- Recommend backup of SQLite database before migration
- Provide verification steps post-migration

### Risk 4: Increased Infrastructure Complexity
**Trade-off**: Additional Docker service adds complexity
**Mitigation**:
- Docker Compose handles orchestration
- Health checks ensure database ready before app starts
- Clear documentation for troubleshooting

## Migration Plan

### Pre-Migration
1. Backup existing SQLite database: `cp runtime/databases/bloggy.db runtime/databases/bloggy.db.backup`
2. Document current database state (row counts, key data)

### Migration Steps
1. Stop running application
2. Pull latest code with PostgreSQL changes
3. Start Docker Compose (PostgreSQL will initialize)
4. Export data from SQLite (optional - development data)
5. Run migrations: `docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up`
6. Import data into PostgreSQL (optional)
7. Verify application functionality
8. Run integration tests to verify database operations

### Rollback Plan
If migration fails:
1. Stop Docker Compose
2. Restore previous version of code
3. Restore SQLite database from backup
4. Restart application with SQLite

### Post-Migration
1. Monitor logs for database connection errors
2. Verify all CRUD operations working
3. Check query performance
4. Remove SQLite database files after verification

## Open Questions

1. **Q**: Should we provide a data migration script?
   **A**: No - one-time operation, users can start fresh or manually migrate if needed

2. **Q**: Should connection pool size be configurable per environment?
   **A**: Yes - use environment variable `DB_POOL_SIZE` with default of 20

3. **Q**: Do we need SSL for PostgreSQL connection in development?
   **A**: Use `sslmode=prefer` to allow SSL if available but not require it

