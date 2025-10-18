# Testing Specification Deltas

## ADDED Requirements

### Requirement: Test Directory Organization

The test suite SHALL be organized in a dedicated top-level `tests/` directory, separate from application code, to maintain clear separation of concerns and improve project structure.

#### Scenario: Test files in dedicated directory
- **WHEN** examining the project structure
- **THEN** all test files are located in the top-level `tests/` directory
- **AND** application code remains in the `runtime/` directory
- **AND** test files follow naming convention `test_*.py` or `tests.py`

#### Scenario: Test runner discovers tests in correct location
- **WHEN** running the test suite via `./run_tests.sh`
- **THEN** pytest discovers tests from the `tests/` directory
- **AND** all test files are collected and executed
- **AND** the test count is greater than 0

#### Scenario: Coverage measures application code
- **WHEN** tests run with coverage enabled
- **THEN** coverage is measured against source code in `runtime/` directory
- **AND** test code in `tests/` directory is excluded from coverage
- **AND** coverage reports accurately reflect application code coverage

#### Scenario: Test runner handles both Docker and local execution
- **WHEN** tests are run in Docker container
- **THEN** test discovery uses path `/app/tests/`
- **AND** source code coverage uses path `/app/runtime/`
- **WHEN** tests are run locally
- **THEN** test discovery uses relative path `tests/`
- **AND** source code coverage uses relative path `runtime/`

### Requirement: Test File Organization

The test suite SHALL organize test files by feature area within the `tests/` directory, with clear naming conventions.

#### Scenario: Core application tests
- **WHEN** examining the `tests/` directory
- **THEN** `tests.py` contains core application integration tests
- **AND** tests cover authentication, posts, comments, and API endpoints

#### Scenario: Feature-specific test files
- **WHEN** examining the `tests/` directory
- **THEN** `test_auto_ui.py` contains auto UI generation tests
- **AND** `test_oauth_real.py` contains OAuth/social login tests
- **AND** `test_ui_chrome_real.py` contains Chrome DevTools UI tests
- **AND** `chrome_integration_tests.py` contains Chrome integration tests

#### Scenario: Test file discovery
- **WHEN** pytest runs test discovery
- **THEN** all files matching `test_*.py` pattern are discovered
- **AND** all files matching `*_test.py` pattern are discovered
- **AND** files named `tests.py` are discovered
- **AND** nested test directories are discovered recursively

