# Fix Integration Test Failures

## Why

After consolidating test scripts and running all 11 test suites, we discovered several test failures that prevent a clean test run. Currently 4 of 11 test suites are failing, which reduces confidence in the codebase and blocks CI/CD deployment.

**Test Results:**
- ✓ tests.py: 83 passed
- ✓ test_oauth_real.py: 23 passed  
- ✓ test_roles_integration.py: 19 passed
- ✓ test_auto_ui.py: 14 passed
- ✓ test_roles.py: 5 passed
- ✗ test_ui_chrome_real.py: No test results (expected - needs Playwright)
- ✗ test_auth_comprehensive.py: File not found
- ✗ test_model_utils.py: File not found
- ✗ test_base_model.py: File not found
- ✗ test_roles_rest_api.py: 5 failed, 12 passed
- ✗ test_oauth_real_user.py: 4 passed, 9 errors

## What Changes

1. **Remove non-existent test files from test runner**
   - Remove test_auth_comprehensive.py
   - Remove test_model_utils.py
   - Remove test_base_model.py

2. **Fix test_oauth_real_user.py database setup**
   - Add _prepare_db fixture with proper table creation
   - Ensure users table exists before OAuth tests run
   - Fix "no such table: users" errors (9 errors)

3. **Fix test_roles_rest_api.py failures**
   - Fix test_rest_api_update_role (assertion failure)
   - Fix test_rest_api_create_permission (likely 403/500 error)
   - Fix test_user_inherits_permissions_from_role_via_api
   - Fix test_rest_api_create_role_forbidden_for_regular_user
   - Fix test_multiple_roles_crud_operations

4. **Update documentation**
   - Update TEST_TYPES_SUMMARY.md to reflect only existing tests
   - Update test counts and active suites
   - Mark Chrome tests as requiring Playwright setup

## Impact

**Affected specs:**
- `testing` capability (test infrastructure)
- No production code changes required

**Affected code:**
- `run_tests.sh` - Remove 3 non-existent test files from --separate mode
- `integration_tests/test_oauth_real_user.py` - Add database setup fixture
- `integration_tests/test_roles_rest_api.py` - Fix 5 failing assertions/API calls
- `TEST_TYPES_SUMMARY.md` - Update to reflect only 8 working test suites
- `README_TEST_SCRIPT.md` - Update test counts

**Expected outcome:**
- 6 test suites passing (139+ tests)
- 1 test suite requiring setup (Chrome/Playwright)
- 1 test suite with known failures to be fixed
- Clean, maintainable test infrastructure

