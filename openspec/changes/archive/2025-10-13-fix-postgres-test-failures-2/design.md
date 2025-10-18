# Design Document: PostgreSQL Test Failures Fix

## Context

The codebase recently migrated from SQLite to PostgreSQL (change: `replace-sqlite-with-postgres`). While the main application works, the integration test suite has significant failures due to PostgreSQL compatibility issues in test fixtures and raw SQL queries.

**Current State:**
- 3 test files failing with 44+ errors
- SQLite-style SQL syntax in test fixtures
- Migration state conflicts
- Table name collisions in pyDAL with PostgreSQL

**Constraints:**
- Must maintain NO MOCKING policy - all tests are real integration tests
- Must work in Docker environment with PostgreSQL 17
- Must not break existing passing tests
- Cannot skip tests - they must either pass or fail with clear messages

**Stakeholders:**
- Developers running tests locally and in CI
- Test infrastructure maintainers

## Goals / Non-Goals

**Goals:**
- Fix all PostgreSQL-related test failures
- Ensure SQL syntax is PostgreSQL-compatible throughout test suite
- Make migrations idempotent and state-aware
- Maintain test isolation with proper cleanup
- Provide clear error messages for expected failures (e.g., missing OAuth tokens)

**Non-Goals:**
- Rewriting tests to support both SQLite and PostgreSQL (PostgreSQL-only is acceptable)
- Adding new test coverage (focus on fixing existing tests)
- Changing application code (only test infrastructure changes)
- Performance optimization of tests

## Decisions

### Decision 1: SQL Placeholder Syntax Standardization

**Choice:** Replace all SQLite `?` placeholders with PostgreSQL `%s` placeholders in raw SQL queries.

**Rationale:**
- PostgreSQL uses `%s` style placeholders (psycopg2 format)
- SQLite uses `?` style placeholders
- Mixing styles causes syntax errors
- pyDAL ORM handles this automatically, but raw SQL in tests does not

**Implementation:**
```python
# BEFORE (SQLite style)
db.executesql("SELECT id FROM users WHERE email = ? LIMIT 1", [email])

# AFTER (PostgreSQL style)  
db.executesql("SELECT id FROM users WHERE email = %s LIMIT 1", [email])
```

**Files affected:**
- `integration_tests/test_oauth_real_user.py` (line 135)
- Any other test files with raw SQL

### Decision 2: Migration Idempotency Strategy

**Choice:** Check table existence before running migrations in test fixtures.

**Rationale:**
- PostgreSQL strictly enforces table uniqueness
- Test fixtures may run migrations multiple times in same session
- Emmett migrations don't automatically skip existing tables
- Better to check explicitly than handle exceptions

**Implementation:**
```python
# Check if tables exist before running migrations
if not _tables_exist(db, ['users', 'roles', 'permissions']):
    migration.up()
else:
    print("   ℹ️  Tables already exist, skipping migrations")
```

**Alternatives considered:**
- ❌ Drop all tables before migrations: Too slow, loses seeded data
- ❌ Use try/except on DuplicateTable: Masks other migration errors
- ✅ Check table existence: Fast, explicit, clear intent

### Decision 3: Table Name Conflict Resolution

**Choice:** Ensure auto-routes uses unique table aliases when joining tables.

**Rationale:**
- pyDAL raises "Name conflict in table list" when same table appears multiple times
- Auto-routes may generate queries that reference related tables
- PostgreSQL schema requires explicit aliasing

**Implementation:**
Review and fix auto-routes query generation to use proper aliases:
```python
# Ensure queries use aliases when needed
query = db.roles.on(db.user_roles.role == db.roles.id)
# Should generate: SELECT ... FROM roles AS t1 JOIN user_roles AS t2 ...
```

### Decision 4: OAuth Token Fixture Error Handling

**Choice:** Move pytest.fail() from fixture setup to test body.

**Rationale:**
- Failing in fixture setup (as it does now) prevents fixture cleanup
- pytest best practice is to fail in test body, not setup
- Other tests can still run even if OAuth token is missing
- Provides better error messages to users

**Implementation:**
```python
@pytest.fixture
def real_oauth_token():
    token = _load_token_if_exists()
    if token is None:
        # Don't fail here - let test handle it
        return None
    return token

def test_use_oauth_token(real_oauth_token):
    if real_oauth_token is None:
        pytest.fail("OAuth token required. Run: python integration_tests/oauth_token_helper.py")
    # Test continues...
```

### Decision 5: Database Cleanup Strategy

**Choice:** Drop and recreate test database at session scope, use transactions for test isolation.

**Rationale:**
- PostgreSQL handles transactions better than SQLite
- Session-level cleanup ensures clean state between full test runs
- Transaction rollback provides test-level isolation
- Prevents state pollution between tests

**Implementation:**
```python
@pytest.fixture(scope="session")
def postgres_test_db():
    # Drop and recreate database
    _recreate_database("bloggy_test")
    yield db
    # Cleanup after all tests

@pytest.fixture
def clean_db_transaction(postgres_test_db):
    # Start transaction
    with postgres_test_db.connection():
        yield postgres_test_db
        # Rollback at end of test
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Breaking existing passing tests | Run full test suite before/after changes |
| PostgreSQL-only tests won't work with SQLite | Acceptable - project is PostgreSQL-only now |
| Migration state issues in CI | Document proper test database setup |
| Slow test execution with DB cleanup | Use transactions for isolation, not full DB recreation |

## Migration Plan

### Phase 1: Fix SQL Syntax (Low Risk)
1. Search for all `?` placeholders in test files: `rg '\?' integration_tests/`
2. Replace with `%s` placeholders
3. Test each affected file individually
4. Verify no regressions

### Phase 2: Fix Migration State (Medium Risk)
1. Add table existence checks to test fixtures
2. Update `_prepare_db` functions
3. Test migration idempotency
4. Verify all role tests pass

### Phase 3: Fix Query Errors (Medium Risk)
1. Debug User.get() failures in REST API tests
2. Fix table name conflicts in auto-routes
3. Test REST API endpoints
4. Verify all 17 tests pass

### Phase 4: Improve Infrastructure (Low Risk)
1. Enhance database cleanup in conftest.py
2. Add PostgreSQL connection handling
3. Document setup requirements
4. Add troubleshooting guide

### Rollback Strategy
- Each phase is independent and can be rolled back separately
- Git branch: `fix/postgres-test-failures-2`
- If tests regress, revert specific commits
- No database schema changes, so rollback is safe

## Validation

**Success metrics:**
- ✅ test_oauth_real_user.py: 0 SQL syntax errors (4 pass, 9 expected failures on missing tokens OK)
- ✅ test_roles_integration.py: 19 tests pass
- ✅ test_roles_rest_api.py: 17 tests pass, 0 failures
- ✅ Full test suite runs in Docker without errors
- ✅ Tests can run multiple times without state conflicts

**Testing approach:**
```bash
# Run individual test files
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_oauth_real_user.py -v
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_roles_integration.py -v  
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/test_roles_rest_api.py -v

# Run full suite
docker compose -f docker/docker-compose.yaml exec runtime pytest integration_tests/ -v
```

## Open Questions

1. **Q:** Should we add a PostgreSQL compatibility checker tool?
   **A:** Not needed now, but could be useful for future test additions

2. **Q:** How do we prevent SQLite syntax from creeping back in?
   **A:** Document PostgreSQL requirements in AGENTS.md and add to code review checklist

3. **Q:** Should conftest.py use database-specific fixtures?
   **A:** Yes, rename `test_db` to `postgres_test_db` for clarity

4. **Q:** Do we need transaction isolation for all tests?
   **A:** Evaluate per test file - some may need it, others may not

