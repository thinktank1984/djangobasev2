# Replace SQLite with PostgreSQL

## Why

SQLite, while convenient for development, has limitations for production environments:
- Limited concurrent write performance due to file-based locking
- No support for concurrent migrations
- Weaker concurrency guarantees compared to client-server databases
- Not suitable for multi-instance deployments or high-traffic applications

PostgreSQL provides robust production-ready features including ACID compliance, better concurrency, advanced indexing, full-text search, and proven scalability.

## What Changes

- **BREAKING**: Replace SQLite with PostgreSQL as the primary database
- Add PostgreSQL service to Docker Compose
- Update database configuration to use PostgreSQL connection string
- Update connection pool settings optimized for PostgreSQL
- Remove SQLite-specific adapter arguments (`check_same_thread`, `timeout`)
- Add PostgreSQL-specific configuration (SSL, search path, etc.)
- Update database initialization to use PostgreSQL
- Migrate existing SQLite data to PostgreSQL (migration script)
- Update all tests to use PostgreSQL test database
- Update documentation to reflect PostgreSQL as the database

## Impact

### Affected Specs
- `database` (new capability) - Database connection and configuration requirements
- `testing` - Test database setup using PostgreSQL

### Affected Code
- `runtime/app.py` - Database URI and adapter configuration (lines 62-70)
- `docker/docker-compose.yaml` - Add PostgreSQL service
- `integration_tests/conftest.py` - Test database configuration
- `documentation/AGENTS.md` - Update database documentation
- `openspec/project.md` - Update tech stack documentation

### Migration Path
1. Export existing SQLite data using emmett migrations
2. Create PostgreSQL database in Docker
3. Run migrations against PostgreSQL
4. Verify data integrity
5. Update application configuration
6. Update tests

### Breaking Changes
- **BREAKING**: Database files in `runtime/databases/` will no longer be used
- **BREAKING**: SQLite-specific SQL queries or features must be replaced with PostgreSQL equivalents
- **BREAKING**: Development setup requires Docker with PostgreSQL service running

