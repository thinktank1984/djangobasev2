# Design: PostgreSQL Connection Context Management for Tests

## Context

The PostgreSQL migration revealed that pyDAL's PostgreSQL adapter requires explicit database connection contexts for query execution. SQLite was more forgiving and allowed queries without explicit connection management. This affects:

- Test fixtures that create database records
- Authentication flows during test setup
- Model validators that execute queries
- All test utility functions

**Current State**: 45 tests failing/erroring due to connection context issues
**Goal**: All tests pass with proper PostgreSQL connection management

## Goals / Non-Goals

### Goals
- Fix all database operations in tests to use connection contexts
- Create reusable patterns for test database access
- Maintain test isolation and cleanup
- Ensure logged_client fixture works reliably
- Document best practices for writing PostgreSQL-compatible tests

### Non-Goals
- Changing application code (only test code)
- Adding connection pooling changes (already configured)
- Modifying pyDAL or Emmett framework behavior
- Creating test-specific database wrapper abstractions

## Decisions

### Decision 1: Use with db.connection() Explicitly
**What**: Wrap all database operations in tests with `with db.connection():` blocks
**Why**: 
- PostgreSQL adapter requires explicit connection contexts
- Clear and explicit - developers understand what's happening
- Matches Emmett documentation patterns
- No magic/hidden behavior

**Alternatives Considered**:
- Auto-connecting decorator: Too magic, hides behavior
- Fixture-level connection: Doesn't work with nested operations
- Monkey-patching pyDAL: Fragile and breaks on updates

**Example**:
```python
def create_test_user(email="test@example.com"):
    with db.connection():
        user = User.create(
            email=email,
            password="test123",
            first_name="Test"
        )
        return user.id
```

### Decision 2: Fix Validators to Work Within Connection Contexts
**What**: Ensure model validators (especially `belongs_to`) execute queries within the existing connection context
**Why**:
- Validators run during `Model.create()` and `model.update_record()`
- They execute database queries for foreign key validation
- Must work within the same transaction as the create/update

**Approach**:
- Validators inherit the connection context from the parent operation
- If already in a connection context, validators reuse it
- No need to wrap individual validators

### Decision 3: Create Helper for Connection Context Management
**What**: Add a helper function in conftest.py to ensure connection context
**Why**:
- Provides consistent pattern across all tests
- Handles edge cases (nested contexts, already connected)
- Makes test code cleaner and more maintainable

**Implementation**:
```python
@contextmanager
def ensure_db_connection():
    """Ensure database connection context exists."""
    # Check if already in a connection context
    if hasattr(db, '_adapter') and db._adapter.connection:
        # Already connected, just yield
        yield
    else:
        # Need to establish connection
        with db.connection():
            yield
```

### Decision 4: Fix logged_client Fixture First
**What**: Prioritize fixing the `logged_client` fixture since 28 tests depend on it
**Why**:
- Highest impact fix - unblocks majority of failing tests
- Auth flow is critical for many test scenarios
- Demonstrates pattern for other fixtures to follow

**Order of Operations**:
1. Fix admin user creation in fixture
2. Fix auth.login() database queries
3. Verify fixture setup completes with status 200
4. Test dependent tests work

## Risks / Trade-offs

### Risk: Connection Context Overhead
**Risk**: Adding explicit connection contexts might impact test performance
**Mitigation**: 
- Connection pooling already configured (20 connections)
- Tests run in Docker with local PostgreSQL (minimal latency)
- Expected impact < 10% increase in test runtime
- **Trade-off**: Correctness over speed - tests must pass

### Risk: Nested Connection Contexts
**Risk**: Some operations might try to nest connection contexts incorrectly
**Mitigation**:
- Use `ensure_db_connection()` helper that checks for existing context
- Document pattern for nested operations
- Test fixtures that use multiple database operations

### Risk: Inconsistent Application
**Risk**: Developers might forget to add connection contexts to new tests
**Mitigation**:
- Document pattern clearly in test writing guide
- Add examples to conftest.py
- Linter/validator could check for pattern (future enhancement)

## Migration Plan

### Phase 1: Fix Critical Fixtures (Tasks 1-2)
1. Implement `ensure_db_connection()` helper
2. Fix `logged_client` fixture
3. Fix `admin_user` and `regular_user` fixtures
4. Verify 28 fixture errors resolved

### Phase 2: Fix Test Utilities (Task 3)
1. Update `create_test_user()`
2. Update `create_test_post()`
3. Update `create_test_comment()`
4. Test utilities work correctly

### Phase 3: Fix Query Execution Tests (Tasks 6-7)
1. Fix all tests with ValueError from SELECT queries
2. Fix authentication flow tests
3. Verify all query-based tests pass

### Phase 4: Fix API Tests (Task 8)
1. Fix tests depending on logged_client
2. Verify all API endpoint tests pass
3. Verify all view/template tests pass

### Rollback Strategy
- Changes are isolated to test code only
- Can revert individual test file changes
- Application code unaffected
- No database schema changes

## Testing Strategy

### Validation Steps
1. Run tests.py: `docker compose exec runtime pytest integration_tests/tests.py -v`
2. Check for ValueError exceptions (should be 0)
3. Check logged_client fixture success (should be 200 status)
4. Verify test count: 55 passed, 0 failed, 0 errors
5. Check test runtime (should be < 15 seconds total)

### Success Metrics
- ✅ 0 ValueError exceptions from PostgreSQL adapter
- ✅ 0 fixture setup errors
- ✅ 55/55 tests passing
- ✅ logged_client fixture reliable
- ✅ No connection leaks or warnings

## Open Questions

1. **Should we add connection context assertions?**
   - Could add helper to verify tests are using contexts correctly
   - Might be overkill for now
   - Decision: Document pattern first, add validation later if needed

2. **How to handle async test operations?**
   - Current tests are mostly sync
   - If async tests added later, may need async context manager
   - Decision: Address when needed (YAGNI)

3. **Should application code also use explicit contexts?**
   - Application routes might benefit from explicit contexts
   - Out of scope for this change (test-only fix)
   - Decision: Create separate proposal if needed

