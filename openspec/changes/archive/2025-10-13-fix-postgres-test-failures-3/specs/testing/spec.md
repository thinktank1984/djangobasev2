## MODIFIED Requirements

### Requirement: Database Connection Management in Tests
Integration tests MUST properly manage PostgreSQL database connections to ensure queries execute successfully.

#### Scenario: Query execution within connection context
- **WHEN** a test needs to query the database
- **THEN** the query MUST be wrapped in `with db.connection():` context
- **AND** the query SHALL execute without ValueError exceptions

#### Scenario: Test fixture database operations
- **WHEN** a test fixture creates database records
- **THEN** all database operations SHALL use connection contexts
- **AND** the fixture SHALL complete without 500 errors

#### Scenario: Authentication in test fixtures
- **WHEN** `logged_client` fixture logs in a user
- **THEN** the authentication database queries SHALL use connection contexts
- **AND** the login SHALL return status 200
- **AND** the fixture SHALL provide an authenticated client

#### Scenario: Model validation queries
- **WHEN** creating a record that validates foreign keys
- **THEN** the validation query SHALL execute within a connection context
- **AND** the validation SHALL complete without ValueError

#### Scenario: Test utility functions
- **WHEN** helper functions create test data
- **THEN** all database operations SHALL use connection contexts
- **AND** the utilities SHALL create records successfully
- **AND** queries SHALL not raise adapter exceptions

## ADDED Requirements

### Requirement: PostgreSQL Connection Context Helper
Tests SHALL have access to a helper for managing database connection contexts.

#### Scenario: Using connection context helper
- **WHEN** a test needs to perform database operations
- **THEN** a helper function SHALL be available to ensure connection context
- **AND** the helper SHALL handle nested connection contexts safely

#### Scenario: Reusable connection wrapper
- **WHEN** multiple tests need database access
- **THEN** they SHALL use a consistent connection context pattern
- **AND** the pattern SHALL prevent connection leaks
- **AND** the pattern SHALL work with both pyDAL and Emmett ORM operations

