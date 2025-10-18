# Fix PostgreSQL Test Failures (Phase 2)

## Why

After migrating from SQLite to PostgreSQL, three test suites are failing with database-related errors:

1. **test_oauth_real_user.py**: 9 errors - SQL syntax errors using SQLite placeholders (`?`) instead of PostgreSQL placeholders (`%s`)
2. **test_roles_integration.py**: 19 errors - Duplicate table errors when running migrations 
3. **test_roles_rest_api.py**: 16 errors + 1 failure - Query execution failures and table name conflicts

These failures prevent the test suite from passing and indicate PostgreSQL compatibility issues in test fixtures and raw SQL queries.

## What Changes

- **Fix SQL placeholder syntax**: Replace SQLite `?` placeholders with PostgreSQL `%s` placeholders in raw SQL queries
- **Fix migration state handling**: Ensure test fixtures properly handle existing tables and migration state for PostgreSQL
- **Fix table name conflicts**: Resolve pyDAL table name conflicts in auto-routes that occur with PostgreSQL
- **Fix OAuth token fixtures**: Update OAuth test fixtures to handle missing tokens without pytest.fail() in setup
- **Add database cleanup**: Implement proper database cleanup between test runs to avoid state pollution

## Impact

- **Affected specs**: `testing` (integration test infrastructure)
- **Affected code**:
  - `integration_tests/test_oauth_real_user.py` - Fix SQL placeholder syntax
  - `integration_tests/test_roles_integration.py` - Fix migration duplicate table handling
  - `integration_tests/test_roles_rest_api.py` - Fix query execution and table conflicts
  - `integration_tests/conftest.py` - Improve PostgreSQL test fixture cleanup
  - `runtime/auto_routes.py` - Fix table name conflicts with pyDAL

## Success Criteria

- All OAuth real user tests pass (0 errors out of 13 tests)
- All roles integration tests pass (0 errors out of 19 tests)  
- All roles REST API tests pass (0 errors, 0 failures out of 17 tests)
- Tests run cleanly in Docker with PostgreSQL backend
- No SQL syntax errors or table conflicts

## Breaking Changes

None - only fixes test infrastructure to work with PostgreSQL.

