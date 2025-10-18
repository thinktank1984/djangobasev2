# Testing Specification Delta

## MODIFIED Requirements

### Requirement: PostgreSQL Integration Test Support
The test infrastructure SHALL support PostgreSQL as the database backend for all integration tests, using PostgreSQL-compatible SQL syntax and proper migration handling.

#### Scenario: Raw SQL queries use PostgreSQL placeholders
- **WHEN** a test fixture executes raw SQL with parameters
- **THEN** it SHALL use `%s` placeholders instead of SQLite `?` placeholders
- **AND** parameters SHALL be passed as a list or tuple
- **AND** queries SHALL execute without syntax errors

#### Scenario: Migration state is handled properly
- **WHEN** test fixtures run database migrations
- **THEN** they SHALL check if tables already exist before creating them
- **AND** they SHALL NOT raise "DuplicateTable" errors
- **AND** they SHALL work correctly on both fresh and existing databases

#### Scenario: Table name conflicts are avoided
- **WHEN** auto-routes or REST APIs query multiple tables
- **THEN** pyDAL SHALL NOT raise "Name conflict in table list" errors
- **AND** table aliases SHALL be used when necessary
- **AND** queries SHALL execute successfully with PostgreSQL

### Requirement: Test Fixture Database Cleanup
Test fixtures SHALL properly clean up database state between test runs to ensure test isolation and repeatability with PostgreSQL.

#### Scenario: Session-scoped database is reset
- **WHEN** a test session starts
- **THEN** the test database SHALL be dropped and recreated
- **AND** all migrations SHALL run successfully
- **AND** the database SHALL be in a clean state

#### Scenario: Test isolation is maintained
- **WHEN** individual tests create data
- **THEN** data SHALL NOT leak between tests
- **AND** test order SHALL NOT affect results
- **AND** concurrent test runs SHALL NOT interfere with each other

### Requirement: OAuth Test Fixtures
OAuth integration test fixtures SHALL handle missing OAuth tokens gracefully without failing during fixture setup.

#### Scenario: Missing OAuth tokens are handled gracefully
- **WHEN** OAuth token file does not exist
- **THEN** dependent tests SHALL fail with clear error messages
- **AND** pytest.fail() SHALL be called in the test body, not fixture setup
- **AND** other tests SHALL continue to run normally
- **AND** instructions for obtaining tokens SHALL be displayed

#### Scenario: OAuth user creation uses PostgreSQL syntax
- **WHEN** creating test users for OAuth tests
- **THEN** raw SQL queries SHALL use PostgreSQL `%s` placeholders
- **AND** user creation SHALL succeed without syntax errors
- **AND** existing users SHALL be detected correctly

## ADDED Requirements

### Requirement: PostgreSQL SQL Placeholder Validation
The test infrastructure SHALL validate that all raw SQL queries use PostgreSQL-compatible placeholder syntax.

#### Scenario: SQLite placeholder syntax is detected and rejected
- **WHEN** reviewing test code for PostgreSQL compatibility
- **THEN** any usage of `?` placeholders SHALL be identified
- **AND** they SHALL be replaced with `%s` placeholders
- **AND** no SQLite-specific syntax SHALL remain in test fixtures

#### Scenario: Migration execution is idempotent
- **WHEN** migrations are executed multiple times
- **THEN** they SHALL NOT fail with duplicate table errors
- **AND** they SHALL check table existence before creating
- **AND** they SHALL handle PostgreSQL-specific constraints correctly

