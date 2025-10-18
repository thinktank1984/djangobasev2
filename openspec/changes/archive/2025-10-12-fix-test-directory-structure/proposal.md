# Fix Test Directory Structure

## Why

The test suite has been reorganized from `runtime/tests.py` to a dedicated top-level `tests/` directory to better separate test code from application code. However, the test runner script (`run_tests.sh`) is still pointing to the old location, causing all tests to be skipped (0 tests collected).

This is blocking the ability to run any tests and verify application functionality.

## What Changes

- Update `run_tests.sh` to point to the new `tests/` directory location
- Update test discovery paths in Docker container from `/app/runtime/tests.py` to `/app/tests/`
- Ensure coverage reporting points to the correct source directories
- Update any documentation referencing the old test location

## Impact

- **Affected specs**: `testing` (test organization requirement)
- **Affected code**: 
  - `run_tests.sh` (lines 193, 220, and related test discovery)
  - Any CI/CD configurations that hardcode test paths
- **Breaking changes**: None - this restores functionality that was broken by the directory reorganization
- **Risk**: Low - straightforward path update

