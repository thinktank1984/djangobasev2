# Implementation Tasks

## 1. Remove Non-Existent Test Files from Runner
- [ ] 1.1 Update `run_tests.sh` --separate mode to remove test_auth_comprehensive.py
- [ ] 1.2 Update `run_tests.sh` --separate mode to remove test_model_utils.py
- [ ] 1.3 Update `run_tests.sh` --separate mode to remove test_base_model.py
- [ ] 1.4 Update `run_tests.sh` --app mode TEST_FILES array (remove 3 files)
- [ ] 1.5 Test that `./run_tests.sh --separate` runs without "file not found" errors

## 2. Fix test_oauth_real_user.py Database Setup
- [ ] 2.1 Add `_prepare_db` fixture at module scope
- [ ] 2.2 Implement table dropping logic (similar to test_oauth_real.py)
- [ ] 2.3 Run Emmett migrations to create users table
- [ ] 2.4 Run Emmett migrations to create oauth_accounts and oauth_tokens tables
- [ ] 2.5 Verify fixture runs before test_user_can_be_created_with_real_email
- [ ] 2.6 Run tests and confirm all 13 tests pass (currently 4 pass, 9 error)

## 3. Fix test_roles_rest_api.py Failures
- [ ] 3.1 Debug test_rest_api_update_role - check response status and body
- [ ] 3.2 Debug test_rest_api_create_permission - check why creation fails
- [ ] 3.3 Debug test_user_inherits_permissions_from_role_via_api - verify permission inheritance
- [ ] 3.4 Debug test_rest_api_create_role_forbidden_for_regular_user - verify 403 response
- [ ] 3.5 Debug test_multiple_roles_crud_operations - check multi-role scenarios
- [ ] 3.6 Fix identified issues (likely API endpoint bugs or test assertions)
- [ ] 3.7 Run tests and confirm all 17 tests pass (currently 12 pass, 5 fail)

## 4. Update Documentation
- [ ] 4.1 Update TEST_TYPES_SUMMARY.md - reduce from 11 to 8 active test suites
- [ ] 4.2 Update README_TEST_SCRIPT.md - adjust test counts (220+ → ~165)
- [ ] 4.3 Update run_tests.sh header comment to show 8 test suites
- [ ] 4.4 Add note about Playwright requirement for Chrome tests
- [ ] 4.5 Document known issues (if any remain after fixes)

## 5. Verification
- [ ] 5.1 Run `./run_tests.sh --separate` and verify no "file not found" errors
- [ ] 5.2 Verify test summary shows 8 test suites (not 11)
- [ ] 5.3 Check test_oauth_real_user.py shows all tests passing
- [ ] 5.4 Check test_roles_rest_api.py shows all tests passing
- [ ] 5.5 Verify total test count is ~165 tests (83+23+19+14+5+13+...)
- [ ] 5.6 Confirm Chrome tests show clear "Playwright not installed" message
- [ ] 5.7 Run `./run_tests.sh --app` and verify it passes

## 6. Commit and Push
- [ ] 6.1 Stage all changes
- [ ] 6.2 Commit with descriptive message
- [ ] 6.3 Push to master
- [ ] 6.4 Verify CI/CD pipeline passes (if exists)

