# testing Specification

## Purpose
TBD - created by archiving change add-100-integration-test-coverage. Update Purpose after archive.
## Requirements
### Requirement: REST API Endpoint Testing

The test suite SHALL provide comprehensive integration tests for all REST API endpoints, validating CRUD operations, validation rules, and error handling.

#### Scenario: List all posts via REST API
- **WHEN** a GET request is made to `/api/posts`
- **THEN** the response status is 200
- **AND** the response contains a paginated list of posts
- **AND** each post includes id, title, text, date, and user fields

#### Scenario: Get single post via REST API
- **WHEN** a GET request is made to `/api/posts/<valid_id>`
- **THEN** the response status is 200
- **AND** the response contains the complete post object
- **AND** all fields match the database record

#### Scenario: Create post via REST API with authentication
- **WHEN** an authenticated user makes a POST request to `/api/posts` with valid data
- **THEN** the response status is 201
- **AND** a new post is created in the database
- **AND** the post.user field is automatically set from session
- **AND** the response includes the created post with id

#### Scenario: Create post via REST API without authentication
- **WHEN** an unauthenticated user makes a POST request to `/api/posts`
- **THEN** the post is created with user field set from request data or null
- **AND** the response status is 201 or 401 based on configuration

#### Scenario: Create post via REST API with invalid data
- **WHEN** a POST request is made to `/api/posts` with missing required fields
- **THEN** the response status is 422 (validation error)
- **AND** the response contains validation error details

#### Scenario: Update post via REST API
- **WHEN** a PUT request is made to `/api/posts/<id>` with valid data
- **THEN** the response status is 200
- **AND** the post is updated in the database
- **AND** the date field is not modified

#### Scenario: Delete post via REST API
- **WHEN** a DELETE request is made to `/api/posts/<id>`
- **THEN** the response status is 200 or 204
- **AND** the post is removed from the database

#### Scenario: Get non-existent post via REST API
- **WHEN** a GET request is made to `/api/posts/99999` (non-existent ID)
- **THEN** the response status is 404
- **AND** an appropriate error message is returned

#### Scenario: List all comments via REST API
- **WHEN** a GET request is made to `/api/comments`
- **THEN** the response status is 200
- **AND** the response contains a paginated list of comments

#### Scenario: Create comment via REST API
- **WHEN** a POST request is made to `/api/comments` with valid post_id, text
- **THEN** the response status is 201
- **AND** a new comment is created linked to the post
- **AND** the user field is set automatically

#### Scenario: Create comment with invalid post_id
- **WHEN** a POST request is made to `/api/comments` with non-existent post_id
- **THEN** the response status is 422 or 404
- **AND** the comment is not created

#### Scenario: List users via REST API (read-only)
- **WHEN** a GET request is made to `/api/users`
- **THEN** the response status is 200
- **AND** the response contains user data without sensitive fields

#### Scenario: Attempt to create user via REST API
- **WHEN** a POST request is made to `/api/users`
- **THEN** the response status is 405 (method not allowed)
- **AND** the user is not created (endpoint disabled)

#### Scenario: Attempt to update user via REST API
- **WHEN** a PUT request is made to `/api/users/<id>`
- **THEN** the response status is 405 (method not allowed)

#### Scenario: Attempt to delete user via REST API
- **WHEN** a DELETE request is made to `/api/users/<id>`
- **THEN** the response status is 405 (method not allowed)

### Requirement: OpenAPI Documentation Testing

The test suite SHALL validate OpenAPI specification generation and Swagger UI functionality.

#### Scenario: Retrieve OpenAPI specification
- **WHEN** a GET request is made to `/api/openapi.json`
- **THEN** the response status is 200
- **AND** the response is valid JSON
- **AND** the JSON contains OpenAPI 3.0 schema
- **AND** the schema includes paths for /api/posts, /api/comments, /api/users

#### Scenario: Validate OpenAPI schema structure
- **WHEN** the OpenAPI specification is retrieved
- **THEN** it includes 'info' section with title and version
- **AND** it includes 'paths' with all REST endpoints
- **AND** it includes 'components' with schema definitions
- **AND** each endpoint has proper method definitions (GET, POST, PUT, DELETE)

#### Scenario: Access Swagger UI documentation
- **WHEN** a GET request is made to `/api/docs`
- **THEN** the response status is 200
- **AND** the response content type is text/html
- **AND** the HTML contains Swagger UI JavaScript initialization

#### Scenario: API root documentation links
- **WHEN** a GET request is made to `/api`
- **THEN** the response status is 200
- **AND** the response contains links to /api/docs and /api/openapi.json
- **AND** the response lists available endpoints

### Requirement: Authentication Flow Testing

The test suite SHALL comprehensively test all authentication flows including registration, login, logout, and password operations.

#### Scenario: User registration with valid data
- **WHEN** a POST request is made to `/auth/register` with valid email, password, names
- **THEN** the response status is 200 or 302 (redirect)
- **AND** a new user is created in the database
- **AND** the password is properly hashed
- **AND** the user is logged in (session created)

#### Scenario: User registration with duplicate email
- **WHEN** a POST request is made to `/auth/register` with an existing email
- **THEN** the response indicates the email is already registered
- **AND** no duplicate user is created

#### Scenario: User registration with invalid email
- **WHEN** a POST request is made to `/auth/register` with invalid email format
- **THEN** the response status indicates validation error
- **AND** no user is created

#### Scenario: User registration with weak password
- **WHEN** a POST request is made to `/auth/register` with password not meeting requirements
- **THEN** the response indicates password validation error
- **AND** no user is created

#### Scenario: User login with correct credentials
- **WHEN** a POST request is made to `/auth/login` with valid email and password
- **THEN** the response status is 200 or 302 (redirect)
- **AND** a session is created
- **AND** subsequent requests have authenticated session

#### Scenario: User login with incorrect password
- **WHEN** a POST request is made to `/auth/login` with valid email but wrong password
- **THEN** the response indicates authentication failure
- **AND** no session is created

#### Scenario: User login with non-existent email
- **WHEN** a POST request is made to `/auth/login` with non-existent email
- **THEN** the response indicates authentication failure
- **AND** no session is created

#### Scenario: User logout
- **WHEN** an authenticated user makes a request to `/auth/logout`
- **THEN** the response status is 200 or 302 (redirect)
- **AND** the session is destroyed
- **AND** subsequent requests are not authenticated

#### Scenario: Access auth routes list
- **WHEN** a GET request is made to `/auth/login` page
- **THEN** the response status is 200
- **AND** the response contains login form

#### Scenario: Access registration page
- **WHEN** a GET request is made to `/auth/register` (if enabled)
- **THEN** the response status is 200 or 404 based on configuration
- **AND** if enabled, the response contains registration form

### Requirement: Post Lifecycle Testing

The test suite SHALL validate the complete lifecycle of blog posts including creation, viewing, editing, and deletion.

#### Scenario: Create post via web form as admin
- **WHEN** an authenticated admin user accesses `/new`
- **AND** submits the form with valid title and text
- **THEN** the response redirects to the created post
- **AND** the post is saved in the database
- **AND** the post.user is set to the admin user
- **AND** the post.date is set to current time

#### Scenario: Create post with missing title
- **WHEN** an admin submits post form with empty title
- **THEN** the form displays validation error
- **AND** the post is not created

#### Scenario: Create post with missing text
- **WHEN** an admin submits post form with empty text
- **THEN** the form displays validation error
- **AND** the post is not created

#### Scenario: View single post
- **WHEN** a GET request is made to `/post/<valid_id>`
- **THEN** the response status is 200
- **AND** the post title and text are displayed
- **AND** the post's comments are listed
- **AND** if authenticated, a comment form is shown

#### Scenario: View non-existent post
- **WHEN** a GET request is made to `/post/99999`
- **THEN** the response status is 404
- **AND** an error page is displayed

#### Scenario: List all posts on homepage
- **WHEN** a GET request is made to `/`
- **THEN** the response status is 200
- **AND** all posts are displayed in reverse chronological order (newest first)
- **AND** each post shows title, author, and date

#### Scenario: Empty blog homepage
- **WHEN** a GET request is made to `/` with no posts in database
- **THEN** the response status is 200
- **AND** the message "No posts here so far" is displayed

### Requirement: Comment Testing

The test suite SHALL validate comment creation, validation, and relationship with posts.

#### Scenario: Add comment to post as authenticated user
- **WHEN** an authenticated user submits comment form on `/post/<id>`
- **AND** provides valid text
- **THEN** the response redirects back to the post
- **AND** the comment is created in the database
- **AND** the comment is linked to the correct post
- **AND** the comment.user is set to the authenticated user

#### Scenario: Add comment with empty text
- **WHEN** an authenticated user submits comment form with empty text
- **THEN** the form displays validation error
- **AND** the comment is not created

#### Scenario: Comment form not shown to unauthenticated users
- **WHEN** an unauthenticated user views `/post/<id>`
- **THEN** the response status is 200
- **AND** no comment form is displayed
- **AND** existing comments are still visible

#### Scenario: Comments displayed in reverse chronological order
- **WHEN** a post has multiple comments
- **AND** a GET request is made to `/post/<id>`
- **THEN** comments are displayed newest first

### Requirement: Authorization Testing

The test suite SHALL validate that protected routes are properly secured and unauthorized access is prevented.

#### Scenario: Authenticated admin can access new post page
- **WHEN** an authenticated user in admin group accesses `/new`
- **THEN** the response status is 200
- **AND** the new post form is displayed

#### Scenario: Non-admin authenticated user cannot access new post page
- **WHEN** an authenticated user NOT in admin group accesses `/new`
- **THEN** the response status is 303 (redirect)
- **AND** the user is redirected to `/`

#### Scenario: Unauthenticated user cannot access new post page
- **WHEN** an unauthenticated user attempts to access `/new`
- **THEN** the response status is 303 (redirect)
- **AND** the user is redirected to `/`

#### Scenario: Admin group membership validation
- **WHEN** a user is added to admin group
- **THEN** the membership is stored in auth_memberships table
- **AND** the user has admin role access

### Requirement: Database Relationship Testing

The test suite SHALL validate database relationships and referential integrity.

#### Scenario: User has many posts relationship
- **WHEN** a user creates multiple posts
- **THEN** user.posts() returns all posts by that user
- **AND** each post.user references the correct user

#### Scenario: Post has many comments relationship
- **WHEN** multiple comments are added to a post
- **THEN** post.comments() returns all comments for that post
- **AND** each comment.post references the correct post

#### Scenario: User has many comments relationship
- **WHEN** a user creates multiple comments
- **THEN** user.comments() returns all comments by that user
- **AND** each comment.user references the correct user

#### Scenario: Comment foreign key constraints
- **WHEN** creating a comment
- **THEN** the comment.post must reference an existing post
- **AND** the comment.user must reference an existing user (or be null if allowed)

### Requirement: Error Handling and Edge Cases

The test suite SHALL validate error handling, edge cases, and boundary conditions.

#### Scenario: Test error endpoint triggers exception
- **WHEN** a GET request is made to `/test-error`
- **THEN** an Exception is raised with message about Bugsink
- **AND** if Sentry is enabled, the error is captured

#### Scenario: Test division by zero error endpoint
- **WHEN** a GET request is made to `/test-error-division`
- **THEN** a ZeroDivisionError is raised
- **AND** if Sentry is enabled, the error is captured

#### Scenario: Invalid route returns 404
- **WHEN** a GET request is made to `/nonexistent-route`
- **THEN** the response status is 404

#### Scenario: Invalid HTTP method on route
- **WHEN** a POST request is made to a GET-only route
- **THEN** the response status is 405 (method not allowed)

#### Scenario: Large text input validation
- **WHEN** a post is created with extremely long title or text
- **THEN** the data is accepted or rejected based on validation rules
- **AND** database constraints are respected

#### Scenario: Special characters in post content
- **WHEN** a post contains special characters (quotes, HTML, Unicode)
- **THEN** the content is properly escaped in HTML output
- **AND** the content is correctly stored and retrieved

### Requirement: Session Management Testing

The test suite SHALL validate session creation, persistence, and expiration.

#### Scenario: Session persists across requests
- **WHEN** a user logs in
- **AND** makes multiple subsequent requests
- **THEN** the session remains active
- **AND** the user remains authenticated

#### Scenario: Session contains user data
- **WHEN** a user is authenticated
- **THEN** session.auth.user contains user information
- **AND** user id, email, and name are accessible

#### Scenario: CSRF token validation
- **WHEN** a form is submitted
- **THEN** the CSRF token from session is validated
- **AND** requests with invalid tokens are rejected

### Requirement: Metrics and Monitoring Testing

The test suite SHALL validate metrics collection and monitoring endpoints when enabled.

#### Scenario: Metrics endpoint returns Prometheus format
- **WHEN** Prometheus is enabled
- **AND** a GET request is made to `/metrics`
- **THEN** the response status is 200
- **AND** the content type is Prometheus text format
- **AND** the response contains metric definitions

#### Scenario: HTTP request metrics are collected
- **WHEN** Prometheus is enabled
- **AND** requests are made to various endpoints
- **THEN** emmett_http_requests_total counter is incremented
- **AND** metrics include method, endpoint, and status labels

#### Scenario: Metrics endpoint when Prometheus disabled
- **WHEN** Prometheus is disabled
- **AND** a GET request is made to `/metrics`
- **THEN** the response status is 404 (endpoint not registered)

### Requirement: Test Fixtures and Test Data Management

The test suite SHALL provide reusable fixtures for common testing scenarios and ensure proper test data cleanup.

#### Scenario: Database setup and teardown
- **WHEN** tests are run
- **THEN** a test database is created with schema
- **AND** migrations are applied
- **AND** after tests, the database is cleaned up

#### Scenario: Admin user fixture
- **WHEN** tests require an admin user
- **THEN** a fixture provides pre-authenticated admin client
- **AND** the admin user exists in the database
- **AND** the admin is a member of admin group

#### Scenario: Regular user fixture
- **WHEN** tests require a non-admin user
- **THEN** a fixture provides authenticated regular user client
- **AND** the user is not in admin group

#### Scenario: Test data cleanup
- **WHEN** each test completes
- **THEN** test-created posts are cleaned up
- **AND** test-created comments are cleaned up
- **AND** test-created users are cleaned up
- **AND** the database state is reset for next test

#### Scenario: Isolated test execution
- **WHEN** tests run in any order
- **THEN** each test has independent database state
- **AND** tests do not interfere with each other
- **AND** all tests pass regardless of execution order

### Requirement: Test Coverage Reporting

The test suite SHALL provide comprehensive coverage reporting and enforce coverage thresholds.

#### Scenario: Generate coverage report
- **WHEN** tests are run with coverage enabled
- **THEN** a coverage report is generated
- **AND** the report shows line coverage percentage
- **AND** the report shows branch coverage percentage
- **AND** the report identifies uncovered lines

#### Scenario: Coverage threshold enforcement
- **WHEN** tests complete
- **THEN** line coverage is at least 95%
- **AND** branch coverage is at least 90%
- **AND** all critical code paths are covered

#### Scenario: Coverage report in CI/CD
- **WHEN** tests run in continuous integration
- **THEN** coverage reports are generated
- **AND** coverage metrics are reported
- **AND** builds fail if coverage drops below threshold

#### Scenario: Exclude test files from coverage
- **WHEN** coverage is calculated
- **THEN** test files themselves are excluded
- **AND** only application code is measured

### Requirement: Test Documentation

The test suite SHALL be self-documenting with clear test names, docstrings, and organization.

#### Scenario: Test functions have descriptive names
- **WHEN** reviewing test code
- **THEN** each test function name clearly describes what is being tested
- **AND** test names follow pattern test_<feature>_<scenario>

#### Scenario: Test functions have docstrings
- **WHEN** reviewing test code
- **THEN** each test has a docstring explaining its purpose
- **AND** complex tests document their setup and assertions

#### Scenario: Tests are organized by feature
- **WHEN** reviewing test file
- **THEN** tests are grouped by feature area (auth, posts, comments, API, etc.)
- **AND** test organization mirrors application structure
- **AND** related tests are kept together

#### Scenario: Test file has header documentation
- **WHEN** opening tests.py
- **THEN** the file begins with module docstring
- **AND** the docstring explains test coverage goals
- **AND** running instructions are documented

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

### Requirement: Integration Test Database Setup
Integration tests SHALL use PostgreSQL as the test database backend, matching the production database engine.

#### Scenario: Test database connection established
- **GIVEN** pytest test suite is initializing
- **WHEN** test fixtures set up the database connection
- **THEN** the system SHALL connect to PostgreSQL test database
- **AND** SHALL use a separate database from the application database
- **AND** the test database name SHALL be "bloggy_test"

#### Scenario: Test database schema creation
- **GIVEN** test database connection is established
- **WHEN** test setup runs
- **THEN** the system SHALL run Emmett migrations to create schema
- **AND** all models SHALL be properly registered
- **AND** database tables SHALL be created with correct structure

#### Scenario: Test database cleanup between tests
- **GIVEN** a test completes execution
- **WHEN** test teardown runs
- **THEN** the system SHALL clean up test data
- **AND** SHALL maintain referential integrity
- **AND** the database SHALL be ready for the next test

#### Scenario: Test isolation with PostgreSQL
- **GIVEN** multiple tests modifying database state
- **WHEN** tests run in sequence or parallel
- **THEN** each test SHALL have isolated database state
- **AND** tests SHALL NOT interfere with each other
- **AND** connection pool SHALL handle concurrent connections

#### Scenario: Real database operations in tests
- **GIVEN** integration tests following "no mocking" policy
- **WHEN** tests perform CRUD operations
- **THEN** all operations SHALL execute against real PostgreSQL database
- **AND** database constraints SHALL be enforced
- **AND** transactions SHALL behave as in production

### Requirement: Test Database Configuration
Test database configuration SHALL support PostgreSQL-specific settings optimized for test execution speed.

#### Scenario: Test database connection string
- **GIVEN** tests are initializing
- **WHEN** test database connection is configured
- **THEN** the system SHALL use TEST_DATABASE_URL if provided
- **OR** SHALL use default test database connection string
- **AND** connection string SHALL point to PostgreSQL service

#### Scenario: Test connection pool settings
- **GIVEN** test database connection is established
- **WHEN** connection pool is configured
- **THEN** the pool size SHALL be appropriate for test execution
- **AND** SHALL handle concurrent test operations
- **AND** SHALL NOT exhaust available connections

#### Scenario: Test database initialization speed
- **GIVEN** test suite starts
- **WHEN** database setup runs
- **THEN** database SHALL initialize within reasonable time
- **AND** migrations SHALL complete successfully
- **AND** test execution SHALL complete in reasonable time

