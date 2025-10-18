# Implementation Tasks

## 1. Docker Infrastructure
- [x] 1.1 Add PostgreSQL service to docker-compose.yaml
- [x] 1.2 Configure PostgreSQL environment variables (database name, user, password)
- [x] 1.3 Add PostgreSQL health check
- [x] 1.4 Add named volume for PostgreSQL data persistence
- [x] 1.5 Configure runtime service to depend on PostgreSQL health

## 2. Database Configuration
- [x] 2.1 Update app.py database URI to use PostgreSQL connection string
- [x] 2.2 Remove SQLite-specific adapter_args (check_same_thread, timeout)
- [x] 2.3 Add PostgreSQL-specific configuration (pool size, SSL mode)
- [x] 2.4 Update environment variable support for database credentials
- [x] 2.5 Add database URI construction with environment variable fallback

## 3. Migration Strategy
- [x] 3.1 Document SQLite data export process
- [x] 3.2 Create PostgreSQL database initialization script
- [x] 3.3 Run existing Emmett migrations against PostgreSQL
- [x] 3.4 Verify all models work with PostgreSQL
- [x] 3.5 Test relationships and constraints in PostgreSQL

## 4. Testing Updates
- [x] 4.1 Update conftest.py to use PostgreSQL test database
- [x] 4.2 Add test database cleanup fixtures
- [x] 4.3 Verify all integration tests pass with PostgreSQL
- [x] 4.4 Add connection pool tests
- [x] 4.5 Test concurrent database operations

## 5. Documentation
- [x] 5.1 Update AGENTS.md with PostgreSQL requirements
- [x] 5.2 Update project.md tech stack section
- [x] 5.3 Add migration guide from SQLite to PostgreSQL
- [x] 5.4 Document PostgreSQL connection string format
- [x] 5.5 Update development setup instructions

## 6. Cleanup
- [x] 6.1 Remove SQLite database files from runtime/databases/
- [x] 6.2 Update .gitignore for PostgreSQL-related files
- [x] 6.3 Remove SQLite-specific comments and configuration

