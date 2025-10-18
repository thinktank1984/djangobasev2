# Implementation Tasks

## 1. Fix Database Connection Context Management
- [ ] 1.1 Analyze where database operations need connection contexts
- [ ] 1.2 Create helper function `ensure_db_connection()` in conftest.py
- [ ] 1.3 Wrap all database queries in `with db.connection():` blocks
- [ ] 1.4 Test that connection contexts are properly managed

## 2. Fix logged_client Fixture
- [ ] 2.1 Debug why auth.login() fails with 500 error in fixture
- [ ] 2.2 Wrap admin user creation in connection context
- [ ] 2.3 Wrap login operation in connection context
- [ ] 2.4 Verify fixture returns 200 status on login
- [ ] 2.5 Test that logged_client fixture works for all dependent tests

## 3. Fix Test Utility Functions
- [ ] 3.1 Update `create_test_user()` to use connection context
- [ ] 3.2 Update `create_test_post()` to use connection context
- [ ] 3.3 Update `create_test_comment()` to use connection context
- [ ] 3.4 Verify all test utilities work with PostgreSQL
- [ ] 3.5 Test that utilities properly clean up connections

## 4. Fix Model Validation Queries
- [ ] 4.1 Identify validators that execute database queries
- [ ] 4.2 Fix `belongs_to` validators to work within connection contexts
- [ ] 4.3 Fix `has_many` relationship queries
- [ ] 4.4 Test that model validation works during create/update
- [ ] 4.5 Verify no ValueError exceptions during validation

## 5. Fix Test Setup and Teardown
- [ ] 5.1 Update `client` fixture database setup
- [ ] 5.2 Update `admin_user` fixture to use connection context
- [ ] 5.3 Update `regular_user` fixture to use connection context
- [ ] 5.4 Add proper connection cleanup in teardown
- [ ] 5.5 Test that fixtures set up database state correctly

## 6. Fix Query Execution Failures
- [ ] 6.1 Fix `test_empty_db` - query execution ValueError
- [ ] 6.2 Fix `test_api_posts_list` - SELECT query failure
- [ ] 6.3 Fix `test_api_comments_list` - SELECT query failure
- [ ] 6.4 Fix `test_homepage_shows_posts` - query in view
- [ ] 6.5 Fix `test_view_single_post` - query in view
- [ ] 6.6 Fix all remaining query execution failures (12 more tests)

## 7. Fix Authentication Flow Tests
- [ ] 7.1 Fix `test_login_correct_credentials` - auth database query
- [ ] 7.2 Fix `test_login_incorrect_password` - auth validation
- [ ] 7.3 Fix `test_login_nonexistent_email` - auth query
- [ ] 7.4 Fix `test_logout` - session cleanup
- [ ] 7.5 Verify all auth tests pass

## 8. Fix API Endpoint Tests (logged_client dependent)
- [ ] 8.1 Fix `test_api_posts_create_authenticated`
- [ ] 8.2 Fix `test_api_posts_update`
- [ ] 8.3 Fix `test_api_posts_delete`
- [ ] 8.4 Fix `test_api_comments_create`
- [ ] 8.5 Fix all remaining API tests (20 more tests)

## 9. Testing and Validation
- [ ] 9.1 Run full test suite: `docker compose exec runtime pytest integration_tests/tests.py -v`
- [ ] 9.2 Verify 0 errors in logged_client fixture setup
- [ ] 9.3 Verify 0 ValueError exceptions from PostgreSQL adapter
- [ ] 9.4 Verify 55/55 tests passing
- [ ] 9.5 Check for any warnings about connection management

## 10. Documentation
- [ ] 10.1 Document PostgreSQL connection context requirements
- [ ] 10.2 Add examples of proper database operation wrapping
- [ ] 10.3 Update test writing guide with PostgreSQL patterns
- [ ] 10.4 Document common pitfalls and solutions

