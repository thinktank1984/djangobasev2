## MODIFIED Requirements
### Requirement: PostgreSQL Database Connection
The system SHALL use PostgreSQL as the primary database backend for business data while supporting a secondary SQLite database for logging and audit operations.

#### Scenario: Application connects to PostgreSQL on startup
- **GIVEN** a Docker environment with PostgreSQL service running
- **WHEN** the application starts
- **THEN** the application SHALL successfully connect to PostgreSQL for business data
- **AND** the application SHALL also connect to SQLite for logging data
- **AND** both connections SHALL be verified via health checks

#### Scenario: Database URI configuration via environment variable
- **GIVEN** a DATABASE_URL environment variable is set
- **WHEN** the application initializes the database connections
- **THEN** the system SHALL use the DATABASE_URL value as the PostgreSQL connection string
- **AND** SHALL use a separate SQLite database for logging
- **AND** SHALL route log models to SQLite automatically

## ADDED Requirements
### Requirement: Multi-Database Configuration
The system SHALL support multiple database backends with automatic routing based on model type.

#### Scenario: Logging database setup
- **GIVEN** the application starts
- **WHEN** the logging database is initialized
- **THEN** the system SHALL create a SQLite database at `logs/logs.sqlite3`
- **AND** the logs directory SHALL be created if it doesn't exist
- **AND** the SQLite database SHALL be used for all log-related models

#### Scenario: Database routing configuration
- **GIVEN** multiple database backends are configured
- **WHEN** a model operation is performed
- **THEN** the system SHALL automatically route logging models to SQLite
- **AND** the system SHALL route business models to PostgreSQL
- **AND** the routing SHALL be transparent to application code

### Requirement: Logging Database Persistence
The system SHALL ensure the logging database is persistent across container restarts and deployments.

#### Scenario: Docker volume mounting
- **GIVEN** Docker Compose configuration
- **WHEN** the application container starts
- **THEN** the logs directory SHALL be mounted as a Docker volume
- **AND** the SQLite database SHALL persist across container restarts
- **AND** log data SHALL not be lost during deployments

#### Scenario: Database initialization
- **GIVEN** the logging database doesn't exist
- **WHEN** the application starts
- **THEN** the system SHALL create the SQLite database
- **AND** SHALL run logging app migrations
- **AND** SHALL be ready to store log data

### Requirement: Cross-Database Relationships
The system SHALL handle the constraints of cross-database relationships between business and logging data.

#### Scenario: Foreign key references
- **GIVEN** a log entry references a business object
- **WHEN** the log entry is created
- **THEN** the system SHALL store the business object ID as an integer field
- **AND** SHALL NOT enforce foreign key constraints across databases
- **AND** SHALL handle cases where the referenced object doesn't exist

#### Scenario: Query optimization
- **GIVEN** queries that need both business and logging data
- **WHEN** the query is executed
- **THEN** the system SHALL efficiently query each database separately
- **AND** SHALL combine results in application memory
- **AND** SHALL avoid performance issues