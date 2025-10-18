# Design: 100% Integration Test Coverage

## Context

The Bloggy application currently has basic integration tests (~57 tests) covering authentication and Valkey cache functionality. To ensure reliability, maintainability, and confidence in the codebase, we need comprehensive integration test coverage for all application features.

### Current State
- Existing tests: authentication basics, cache operations
- Coverage: ~40-50% estimated
- Missing: REST API tests, full auth flows, post/comment operations, edge cases

### Constraints
- Must use Docker environment for all tests (per project requirements)
- Must use pytest as testing framework
- Must use Emmett's test client
- No changes to application code (tests only)
- Tests must be runnable in any order (no interdependencies)

### Stakeholders
- Developers: Need confidence when refactoring or adding features
- CI/CD: Automated testing and coverage enforcement
- Future maintainers: Tests serve as living documentation

## Goals / Non-Goals

### Goals
- Achieve 95%+ line coverage and 90%+ branch coverage
- Test all route handlers and REST API endpoints
- Test all authentication and authorization flows
- Test error handling and edge cases
- Provide reusable fixtures for common scenarios
- Make tests self-documenting with clear names and organization
- Ensure tests run reliably in Docker environment

### Non-Goals
- Unit tests (this is for integration tests only)
- Performance/load testing
- UI/browser testing (covered separately)
- Testing third-party libraries (Emmett, pyDAL, etc.)
- Changing application code or behavior
- Testing infrastructure/deployment scripts

## Decisions

### Decision 1: Test Organization Strategy

**Decision**: Organize tests by feature area within a single file (`tests.py`), using comments and logical grouping.

**Rationale**:
- Project convention is single test file (`tests.py`)
- Easier to navigate than multiple files for medium-sized application
- Comment headers provide clear section boundaries
- Consistent with existing test structure

**Alternatives Considered**:
- Multiple test files (test_auth.py, test_api.py, etc.): Rejected because project uses single file convention
- Test classes: Considered but not required for pytest; flat structure is simpler

**Implementation**:
```python
# =============================================================================
# Authentication Tests
# =============================================================================

def test_user_login_success(logged_client):
    ...

def test_user_login_failure(client):
    ...

# =============================================================================
# REST API - Posts Tests
# =============================================================================

def test_api_posts_list(client):
    ...
```

### Decision 2: Fixture Design Pattern

**Decision**: Create focused, composable fixtures for common scenarios:
- `client` - Anonymous test client (existing)
- `logged_client` - Authenticated admin client (existing)
- `regular_user_client` - Authenticated non-admin client (new)
- `test_posts` - Collection of test posts (new)
- `test_comments` - Collection of test comments (new)

**Rationale**:
- Fixtures eliminate duplicate setup code
- Composable fixtures allow combining behaviors
- Scoped fixtures (module, function) control lifecycle
- Automatic cleanup via fixture teardown

**Alternatives Considered**:
- Setup/teardown methods: Less Pythonic than fixtures
- Test utilities: Fixtures are more powerful and better integrated with pytest
- Class-based fixtures: Unnecessary complexity for our use case

**Implementation**:
```python
@pytest.fixture()
def regular_user_client():
    """Authenticated non-admin user client"""
    # Create user without admin group
    # Login and return client
    yield client
    # Cleanup user

@pytest.fixture()
def test_posts(logged_client):
    """Create test posts for testing"""
    posts = []
    # Create 3-5 test posts
    yield posts
    # Cleanup posts
```

### Decision 3: Coverage Thresholds

**Decision**: Target 95% line coverage, 90% branch coverage.

**Rationale**:
- 100% is often impractical (defensive code, error handling, etc.)
- 95% line / 90% branch is industry best practice
- Allows excluding truly unreachable code
- Focuses effort on meaningful coverage

**Exclusions**:
- Test files themselves
- Migration files (tested by running migrations)
- Setup scripts
- Debug/development-only code paths
- Conditional imports (try/except for optional dependencies)

**Configuration**:
```ini
[tool:pytest]
addopts = --cov=app --cov-report=term-missing --cov-fail-under=95
```

### Decision 4: Test Data Management

**Decision**: Use a hybrid approach:
1. Module-scoped fixtures for expensive setup (database, admin user)
2. Function-scoped fixtures for test data (posts, comments)
3. Explicit cleanup in fixture teardown
4. Use separate test database (databases/bloggy_test.db)

**Rationale**:
- Module scope avoids repeated database setup (faster)
- Function scope ensures test isolation for mutable data
- Explicit cleanup is more reliable than automatic rollback
- Separate database prevents interference with development

**Alternatives Considered**:
- Transaction rollback: Cleaner but more complex with Emmett
- In-memory database: Faster but less realistic
- Database per test: Too slow
- Shared test data: Risks test interdependencies

### Decision 5: Docker-Exclusive Testing

**Decision**: All tests must run in Docker; document Docker commands prominently.

**Rationale**:
- Project requirement (per AGENTS.md)
- Ensures consistent environment across developers
- Includes all dependencies (Gemini, packages, etc.)
- Matches production environment

**Impact**:
- Local test script (`./run_tests.sh`) is fallback only
- All documentation shows Docker commands first
- CI/CD must use Docker

**Commands**:
```bash
# Standard test run
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py

# With coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py --cov=app --cov-report=term-missing

# Specific test
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -k test_name
```

### Decision 6: REST API Testing Strategy

**Decision**: Test REST APIs via HTTP requests, not direct model calls.

**Rationale**:
- Integration tests should test complete request/response cycle
- Tests serialization, validation, routing
- Tests actual API contract users will experience
- Catches issues in request handling pipelines

**Implementation**:
```python
def test_api_posts_create(logged_client):
    # Test via POST request, not Post.create()
    response = logged_client.post('/api/posts', data={
        'title': 'Test Post',
        'text': 'Test content'
    })
    assert response.status == 201
    # Verify database state changed
    assert Post.where(lambda p: p.title == 'Test Post').count() == 1
```

### Decision 7: Test Naming Convention

**Decision**: Use descriptive names following pattern: `test_<feature>_<scenario>`

**Examples**:
- `test_api_posts_create_success`
- `test_api_posts_create_missing_title`
- `test_auth_login_invalid_password`
- `test_post_view_as_unauthenticated_user`

**Rationale**:
- Self-documenting
- Easy to understand test failures
- Groups related tests alphabetically
- Consistent with pytest conventions

### Decision 8: CSRF Token Handling

**Decision**: Extract CSRF tokens from session context for form submissions.

**Current Pattern** (from existing tests):
```python
with c.get('/auth/login').context as ctx:
    c.post('/auth/login', data={
        'email': 'doc@emmettbrown.com',
        'password': 'fluxcapacitor',
        '_csrf_token': list(ctx.session._csrf)[-1]
    })
```

**Rationale**:
- Matches existing test patterns
- Tests CSRF protection is working
- More realistic than disabling CSRF

## Risks / Trade-offs

### Risk: Test Maintenance Burden
- **Risk**: Large test suite takes time to maintain
- **Mitigation**: 
  - Clear test organization and naming
  - Reusable fixtures reduce duplication
  - Tests serve as documentation, reducing overall maintenance
  - Focus on stable APIs and behaviors

### Risk: Test Execution Time
- **Risk**: 100+ tests may be slow to run
- **Mitigation**:
  - Module-scoped fixtures for expensive setup
  - Parallel test execution (pytest-xdist) if needed
  - Focus on integration tests, not exhaustive permutations
  - Current test suite runs quickly (<10 seconds)

### Risk: False Sense of Security
- **Risk**: High coverage doesn't guarantee correctness
- **Mitigation**:
  - Test meaningful scenarios, not just lines
  - Include both success and failure cases
  - Test edge cases and boundary conditions
  - Manual testing still valuable for UX

### Risk: Docker Dependency
- **Risk**: Developers may not have Docker available
- **Mitigation**:
  - Strongly emphasize Docker requirement in docs
  - Provide local fallback script (but discourage use)
  - Docker is already project requirement

### Trade-off: Integration vs Unit Tests
- **Decision**: Focus on integration tests
- **Trade-off**: Integration tests are slower, less granular than unit tests
- **Justification**: 
  - Small application benefits more from integration tests
  - Emmett's architecture doesn't lend itself to isolated unit tests
  - Integration tests catch more real-world issues
  - Unit tests can be added later for complex logic

## Migration Plan

### Phase 1: Infrastructure (Tasks 1, 14)
1. Add coverage configuration
2. Create new fixtures (regular_user_client, test_posts, test_comments)
3. Add module docstring

### Phase 2: Core Functionality (Tasks 2-8)
1. REST API tests (posts, comments, users)
2. Post lifecycle tests
3. Comment tests
4. OpenAPI documentation tests

### Phase 3: Authentication & Authorization (Tasks 6, 9)
1. Complete authentication flow tests
2. Authorization tests

### Phase 4: Advanced Features (Tasks 10-13)
1. Database relationship tests
2. Error handling tests
3. Session management tests
4. Metrics tests (if enabled)

### Phase 5: Polish (Task 15-16)
1. Fill coverage gaps
2. Add docstrings
3. Documentation
4. Validation

### Rollback
- No rollback needed (only adding tests)
- Can disable individual tests with `@pytest.mark.skip` if issues arise
- Coverage thresholds can be adjusted if needed

## Open Questions

### Q1: Should we test Sentry error capture?
**Status**: Deferred
**Reasoning**: Error tracking is optional dependency; verify endpoints trigger errors, but don't test Sentry client behavior

### Q2: Should we test with different database backends?
**Status**: No
**Reasoning**: SQLite is default; pyDAL abstracts database differences; infrastructure testing is separate concern

### Q3: Should we test WebSocket functionality?
**Status**: No (not implemented yet)
**Reasoning**: Bloggy doesn't currently use WebSockets; add when feature is implemented

### Q4: Should we test email sending?
**Status**: Minimal
**Reasoning**: Mailer is configured with `suppress=True`; verify auth routes exist but don't test email delivery

### Q5: Coverage enforcement in CI/CD?
**Status**: Recommended, not required initially
**Reasoning**: Set up coverage reporting first; add enforcement once stable baseline achieved

## Success Metrics

### Quantitative
- Line coverage ≥ 95%
- Branch coverage ≥ 90%
- All endpoints tested (100% route coverage)
- All REST API methods tested
- All authentication flows tested
- 0 failing tests

### Qualitative
- Tests are readable and self-documenting
- Test failures clearly indicate what broke
- New developers can understand system behavior from tests
- Tests run reliably in Docker
- Coverage report identifies any gaps clearly

