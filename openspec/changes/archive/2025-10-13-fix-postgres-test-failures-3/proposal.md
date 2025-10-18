# Fix PostgreSQL Test Failures (Phase 3)

## Why

After the PostgreSQL migration, the main integration test suite (`tests.py`) has 17 failures and 28 errors. The root cause is that PostgreSQL requires explicit database connection context management that wasn't needed with SQLite.

**Critical Issue**: The `logged_client` fixture fails during setup with a 500 error, cascading to cause 28 test errors. All affected tests depend on authentication, which is failing because database queries in the auth flow aren't wrapped in proper connection contexts.

**Error Pattern**:
```python
ValueError: SELECT count(*) FROM "users" WHERE (("users"."id" IS NOT NULL) AND ("users"."id" = 1));
```

This occurs when pyDAL's PostgreSQL adapter tries to execute queries outside of a proper connection context.

## What Changes

- **Fix logged_client fixture**: Wrap authentication database operations in `with db.connection():` contexts
- **Fix test utilities**: Update `create_test_user()` and `create_test_post()` to use connection contexts
- **Fix query execution**: Ensure all database queries in tests use proper connection management
- **Fix validation queries**: Update model validators to work within PostgreSQL connection contexts
- **Fix test setup/teardown**: Ensure database operations in fixtures use connection contexts
- **Add connection context helper**: Create reusable context manager for test database operations

## Impact

### Affected Specs
- `testing` - Integration test infrastructure

### Affected Code
- `integration_tests/conftest.py` - Fix `logged_client` and other database fixtures
- `integration_tests/tests.py` - Fix test utilities and helper functions
- Test execution - 45 tests currently failing/erroring will be fixed

### Test Categories Affected
1. **Authentication tests** (28 errors) - `logged_client` fixture setup failing
2. **Query tests** (17 failures) - SELECT queries raising ValueError
3. **API endpoint tests** - All endpoints requiring auth
4. **View/template tests** - Pages requiring database queries
5. **Model relationship tests** - Foreign key operations failing

### Success Criteria
- `logged_client` fixture succeeds (status 200 during login)
- All 28 fixture setup errors resolved
- All 17 query execution failures resolved
- Total passing tests: 55/55 (currently 38/55)
- Zero ValueError exceptions from PostgreSQL adapter

## Breaking Changes

None - this fixes broken functionality introduced by PostgreSQL migration.

