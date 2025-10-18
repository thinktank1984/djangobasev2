# Testing Capability Delta

## ADDED Requirements

### Requirement: Test Suite Validation
The test runner SHALL only reference test files that exist in the repository.

#### Scenario: Non-existent test file referenced
- **WHEN** test runner attempts to run a non-existent test file
- **THEN** the test file is removed from the runner configuration
- **AND** no "file not found" errors occur during test execution

#### Scenario: Test suite count accuracy
- **WHEN** documentation lists active test suites
- **THEN** the count SHALL match the number of existing test files
- **AND** all referenced test files SHALL exist on disk

### Requirement: Database Setup for OAuth Tests
OAuth integration tests SHALL have proper database initialization before test execution.

#### Scenario: OAuth user tests require users table
- **WHEN** test_oauth_real_user.py tests run
- **THEN** a `_prepare_db` fixture SHALL create the users table
- **AND** all Emmett migrations SHALL run successfully
- **AND** OAuth-related tables (oauth_accounts, oauth_tokens) SHALL be created

#### Scenario: Database cleanup between test runs
- **WHEN** OAuth tests complete
- **THEN** test data SHALL be removed
- **AND** tables SHALL be dropped (or reset) for next test run
- **AND** no "no such table" errors SHALL occur

### Requirement: Role REST API Test Stability
Role REST API integration tests SHALL consistently pass without failures.

#### Scenario: Update role via API
- **WHEN** test_rest_api_update_role executes
- **THEN** the API response status SHALL be 200
- **AND** role attributes SHALL be updated in database
- **AND** updated values SHALL be retrievable via API

#### Scenario: Create permission via API
- **WHEN** test_rest_api_create_permission executes
- **THEN** the API response status SHALL be 201
- **AND** permission SHALL be created in database
- **AND** permission SHALL be retrievable via API

#### Scenario: Permission inheritance verification
- **WHEN** test_user_inherits_permissions_from_role_via_api executes
- **THEN** user SHALL inherit permissions from assigned role
- **AND** permission check via API SHALL return true
- **AND** all role-based permissions SHALL be accessible

#### Scenario: Forbidden access enforcement
- **WHEN** test_rest_api_create_role_forbidden_for_regular_user executes
- **THEN** regular user SHALL receive 403 Forbidden response
- **AND** no role SHALL be created
- **AND** database SHALL remain unchanged

#### Scenario: Multiple role operations
- **WHEN** test_multiple_roles_crud_operations executes
- **THEN** all CRUD operations SHALL complete successfully
- **AND** role relationships SHALL be maintained
- **AND** no data corruption SHALL occur

## MODIFIED Requirements

### Requirement: Test Documentation Accuracy
Test documentation SHALL accurately reflect the current state of the test suite.

**Previous state:** Documentation referenced 11 test suites including non-existent files.

**New state:** Documentation SHALL only reference existing test files and SHALL provide accurate test counts.

#### Scenario: Test count verification
- **WHEN** TEST_TYPES_SUMMARY.md is read
- **THEN** all listed test files SHALL exist
- **AND** test counts SHALL match actual pytest collection
- **AND** status indicators SHALL reflect current test health

#### Scenario: Test runner script accuracy
- **WHEN** run_tests.sh --separate executes
- **THEN** only existing test files SHALL be invoked
- **AND** the count of test suites SHALL match documentation
- **AND** output summary SHALL show accurate pass/fail counts

### Requirement: Test Execution Resilience
The test runner SHALL continue execution even when individual test suites fail.

**Previous state:** Script used `|| true` inconsistently, and referenced non-existent files causing premature termination.

**New state:** All test commands SHALL use `|| true` and only existing files SHALL be referenced.

#### Scenario: Partial test failure handling
- **WHEN** one test suite fails
- **THEN** subsequent test suites SHALL still execute
- **AND** final summary SHALL report all results
- **AND** exit code SHALL reflect overall pass/fail status

#### Scenario: Missing test file handling
- **WHEN** test runner configuration is updated
- **THEN** non-existent test files SHALL be removed
- **AND** test execution SHALL complete without errors
- **AND** users SHALL see clear summary of available tests

