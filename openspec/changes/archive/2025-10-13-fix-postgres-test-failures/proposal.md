# Fix PostgreSQL Test Failures

## Why

After migrating from SQLite to PostgreSQL, 17 tests are failing and 28 have errors in the main integration test suite (`tests.py`). The primary issue is that database operations are failing with `ValueError` exceptions from the PostgreSQL adapter.

**Root Cause**: PostgreSQL adapter in pyDAL requires explicit database connection context management, whereas SQLite was more forgiving. Tests that worked with SQLite now fail because:
1. Database operations aren't wrapped in `with db.connection()` contexts
2. The test fixtures don't establish proper connection pooling
3. Auth-related database queries (`auth_groups`, `auth_users`) fail during test setup

**Test Results**:
- **17 FAILED**: Query execution failures, authentication errors
- **28 ERRORS**: Test setup failures (logged_client fixture failing)
- **38 PASSED**: Tests that don't require complex DB operations

## What Changes

- Fix database connection context management in test fixtures
- Wrap all database operations in `with db.connection():` blocks
- Update `conftest.py` to properly manage PostgreSQL connections for tests
- Fix auth-related database queries to work with PostgreSQL
- Ensure test data setup/teardown uses connection contexts
- Update test utilities (`create_test_post`, `create_test_user`) to handle PostgreSQL
- Add proper transaction management for test isolation

## Impact

### Affected Specs
- `testing` - Integration test database setup and execution

### Affected Code
- `integration_tests/conftest.py` - Database connection fixtures
- `integration_tests/tests.py` - Test utilities and helper functions
- Test execution - All database-dependent tests

### Test Categories Affected
1. **Authentication tests** (5 errors) - Login/logout failing
2. **API endpoint tests** (13 errors) - POST/PUT/DELETE operations failing  
3. **Model relationship tests** (7 errors) - Foreign key operations failing
4. **View/template tests** (3 errors) - Page rendering with DB queries failing
5. **Query tests** (17 failed) - SELECT queries raising ValueError

### Breaking Changes
None - this fixes broken functionality introduced by PostgreSQL migration

