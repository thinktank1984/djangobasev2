# OpenSpec Change Proposal: Fix Integration Test Failures

## Metadata
- **Proposal ID**: `fix-integration-test-failures`
- **Created**: 2025-10-12
- **Status**: Draft
- **Priority**: High
- **Complexity**: Medium
- **Estimated Effort**: 4-6 hours

## Executive Summary

Fix 29 failing integration tests by implementing proper context handling, form submissions, model relationships, and session management. This will bring test coverage from 65% to 100% and ensure the application's core integration features work correctly.

## Problem Statement

### Current State
- ✅ 54 tests passing (65%)
- ❌ 29 tests failing (35%)
- All core functionality tests pass (auth, cache, metrics)
- All integration tests fail due to missing implementations

### Test Failure Categories

#### 1. REST API Context Issues (11 tests)
```
AttributeError: 'Context' object has no attribute 'session'
```
**Affected Tests:**
- `test_api_posts_list`
- `test_api_posts_get_single`
- `test_api_posts_update`
- `test_api_posts_delete`
- `test_api_comments_list`
- `test_api_comments_create`
- `test_api_comments_create_missing_text`
- Plus 4 more...

**Root Cause:** REST endpoints need proper session/context access for authentication checks and user association.

#### 2. Model Query Issues (7 tests)
```
AttributeError: first
```
**Affected Tests:**
- `test_api_posts_create_authenticated`
- `test_api_posts_user_auto_set`
- `test_create_post_via_form`
- Plus 4 more...

**Root Cause:** Database queries using `.first()` method failing, likely due to context issues or empty result sets.

#### 3. Session Management (5 tests)
```
AttributeError: 'NoneType' object has no attribute 'user'
```
**Affected Tests:**
- `test_logout`
- `test_session_persists_across_requests`
- `test_session_contains_user_data`
- Plus 2 more...

**Root Cause:** Session not properly maintained in test client across requests.

#### 4. Authorization/Redirect Issues (6 tests)
```
assert 303 == 200  # Expected redirect but got OK
assert 200 == 303  # Expected OK but got redirect
```
**Affected Tests:**
- `test_new_post_page_as_admin`
- `test_regular_user_cannot_access_new_post`
- `test_comment_form_shown_to_authenticated_user`
- `test_comment_form_hidden_from_unauthenticated`
- Plus 2 more...

**Root Cause:** Authorization checks not working correctly with session state.

## Proposed Solution

### Phase 1: REST API Context Handling

#### 1.1 Fix Session Access in REST Endpoints
**File:** `runtime/app.py`

```python
# Update REST API callbacks to properly access session
@posts_api.before_create
def set_post_user(attrs):
    """Automatically set user from session if authenticated"""
    # Current (broken):
    if session.auth and 'user' not in attrs:
        attrs['user'] = session.auth.user.id
    
    # Fixed:
    from emmett import current
    if current.session.auth and 'user' not in attrs:
        attrs['user'] = current.session.auth.user.id

@comments_api.before_create  
def set_comment_user(attrs):
    """Automatically set user from session if authenticated"""
    from emmett import current
    if current.session.auth and 'user' not in attrs:
        attrs['user'] = current.session.auth.user.id
```

#### 1.2 Add Proper Error Handling for REST Operations
```python
@posts_api.on_read_error
def handle_post_not_found(error):
    """Handle post not found errors"""
    return {'error': 'Post not found'}, 404

@posts_api.on_create_error
def handle_post_creation_error(error):
    """Handle post creation validation errors"""
    return {'error': str(error)}, 422
```

### Phase 2: Model Relationship Queries

#### 2.1 Fix Database Queries with Proper Context
**File:** `runtime/tests.py`

Update test fixtures to ensure database context is properly maintained:

```python
@pytest.fixture(scope='module')
def logged_client():
    c = app.test_client()
    with db.connection():  # Ensure DB context
        with c.get('/auth/login').context as ctx:
            c.post('/auth/login', data={
                'email': 'doc@emmettbrown.com',
                'password': 'fluxcapacitor',
                '_csrf_token': list(ctx.session._csrf)[-1]
            }, follow_redirects=True)
    return c
```

#### 2.2 Add Safe Query Helpers
**File:** `runtime/app.py`

```python
def get_or_404(model, record_id):
    """Get model by ID or abort with 404"""
    with db.connection():
        record = model.get(record_id)
        if not record:
            abort(404)
        return record

def get_first_or_none(query):
    """Safely get first result or None"""
    try:
        with db.connection():
            return query.select().first()
    except:
        return None
```

### Phase 3: Form Submission Handlers

#### 3.1 Update Form Routes with Proper Context
**File:** `runtime/app.py`

```python
@app.route("/new", methods=['get', 'post'])
@requires(lambda: session.auth.user and 'admin' in session.auth.user.groups(), url('index'))
async def new_post():
    from emmett import current
    
    if request.method == 'POST':
        # Get form data
        title = request.body_params.title
        text = request.body_params.text
        
        # Create post with proper context
        with db.connection():
            post = Post.create(
                title=title,
                text=text,
                user=current.session.auth.user.id
            )
            db.commit()
        
        redirect(url('one', pid=post.id))
    
    return dict()
```

#### 3.2 Add Comment Submission Handler
```python
@app.route("/post/<int:pid>", methods=['post'])
async def post_comment(pid):
    from emmett import current
    
    # Validate form
    text = request.body_params.text
    if not text:
        return dict(error='Comment text is required')
    
    # Create comment
    with db.connection():
        post = Post.get(pid)
        if not post:
            abort(404)
        
        comment = Comment.create(
            post=pid,
            text=text,
            user=current.session.auth.user.id if current.session.auth else None
        )
        db.commit()
    
    redirect(url('one', pid=pid))
```

### Phase 4: Session Management in Tests

#### 4.1 Fix Test Client Session Persistence
**File:** `runtime/tests.py`

```python
@pytest.fixture(scope='module')
def logged_client():
    """Create a test client with persistent session"""
    c = app.test_client()
    
    # Perform login and keep session
    with c.get('/auth/login').context as ctx:
        response = c.post('/auth/login', data={
            'email': 'doc@emmettbrown.com',
            'password': 'fluxcapacitor',
            '_csrf_token': list(ctx.session._csrf)[-1]
        }, follow_redirects=True)
        
        # Verify login succeeded
        assert response.status == 200
    
    # Return client with active session
    return c
```

#### 4.2 Add Session Test Helpers
```python
def get_session_from_client(client):
    """Extract session data from test client"""
    with client.get('/').context as ctx:
        return ctx.session

def assert_user_logged_in(client, expected_email=None):
    """Assert user is logged in"""
    session = get_session_from_client(client)
    assert session.auth is not None
    assert session.auth.user is not None
    if expected_email:
        assert session.auth.user.email == expected_email
```

### Phase 5: Authorization & Redirects

#### 5.1 Fix Admin Authorization Checks
**File:** `runtime/app.py`

```python
def is_admin():
    """Check if current user is admin"""
    from emmett import current
    if not current.session.auth or not current.session.auth.user:
        return False
    return 'admin' in current.session.auth.user.groups()

@app.route("/new")
@requires(is_admin, url('index'))
async def new_post():
    """Admin-only: Create new post"""
    return dict()
```

#### 5.2 Update Authorization Decorators
```python
from functools import wraps

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        from emmett import current
        if not current.session.auth:
            redirect(url('auth_routes.login'))
        return await f(*args, **kwargs)
    return wrapper

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if not is_admin():
            redirect(url('index'))
        return await f(*args, **kwargs)
    return wrapper
```

## Implementation Plan

### Task Breakdown

#### Task 1: Fix REST API Context (2 hours)
- [ ] Update `posts_api.before_create` to use `current.session`
- [ ] Update `comments_api.before_create` to use `current.session`
- [ ] Add error handlers for REST operations
- [ ] Test REST API endpoints
- **Estimated fixes:** 11 tests

#### Task 2: Fix Model Queries (1.5 hours)
- [ ] Add `get_or_404` helper function
- [ ] Add `get_first_or_none` helper function
- [ ] Update all `.first()` calls with proper error handling
- [ ] Update database fixtures in tests
- **Estimated fixes:** 7 tests

#### Task 3: Fix Form Handlers (1.5 hours)
- [ ] Update `/new` route to handle POST
- [ ] Add comment submission handler
- [ ] Add form validation
- [ ] Add proper redirects after submission
- **Estimated fixes:** 7 tests

#### Task 4: Fix Session Management (1 hour)
- [ ] Update `logged_client` fixture
- [ ] Add session test helpers
- [ ] Ensure session persists across test requests
- **Estimated fixes:** 5 tests

#### Task 5: Fix Authorization (1 hour)
- [ ] Create `is_admin()` helper
- [ ] Update `@requires` decorators
- [ ] Test authorization redirects
- [ ] Fix admin access tests
- **Estimated fixes:** 6 tests

### Testing Strategy

1. **Unit Testing**
   - Test each helper function independently
   - Verify context access works correctly
   - Test error handlers

2. **Integration Testing**
   - Run failing tests after each task
   - Verify no regressions in passing tests
   - Check test coverage increases

3. **Manual Testing**
   - Test REST API endpoints in browser
   - Submit forms manually
   - Verify admin access controls

## Success Criteria

### Quantitative
- ✅ All 83 tests passing (100% success rate)
- ✅ Test coverage ≥ 90% for modified code
- ✅ No regressions in currently passing tests

### Qualitative
- ✅ REST API properly handles authentication
- ✅ Forms submit and validate correctly
- ✅ Database queries don't raise AttributeError
- ✅ Sessions persist across requests
- ✅ Authorization checks work as expected

## Risk Assessment

### Low Risk
- Helper functions (pure utility code)
- Error handlers (fail-safe additions)

### Medium Risk
- Session context changes (could affect auth flow)
- Form handler changes (user-facing functionality)

### Mitigation Strategies
1. **Incremental Changes**: Implement one phase at a time
2. **Continuous Testing**: Run tests after each change
3. **Rollback Plan**: Git commits after each working phase
4. **Documentation**: Document all API changes

## Dependencies

### Code Dependencies
- Emmett Framework (current module system)
- pytest fixtures (test infrastructure)
- Database connection context managers

### External Dependencies
- None (all internal changes)

## Timeline

### Phase 1: REST API Context (Day 1)
- **Duration**: 2 hours
- **Deliverable**: 11 tests passing

### Phase 2: Model Queries (Day 1)  
- **Duration**: 1.5 hours
- **Deliverable**: 18 total tests passing

### Phase 3: Form Handlers (Day 2)
- **Duration**: 1.5 hours
- **Deliverable**: 25 total tests passing

### Phase 4: Session Management (Day 2)
- **Duration**: 1 hour
- **Deliverable**: 30 total tests passing

### Phase 5: Authorization (Day 2)
- **Duration**: 1 hour
- **Deliverable**: All 83 tests passing

**Total Estimated Time**: 7 hours (1.5 working days)

## Files to Modify

### Primary Changes
1. `runtime/app.py` - Main application logic
   - REST API callbacks
   - Form handlers
   - Helper functions
   - Authorization decorators

2. `runtime/tests.py` - Test infrastructure
   - Update fixtures
   - Add test helpers
   - Fix session handling

### Supporting Files
3. `documentation/TEST_FIX_SUMMARY.md` - Update with final results
4. `openspec/changes/fix-integration-test-failures/IMPLEMENTATION_SUMMARY.md` - Track progress

## Rollback Plan

If issues arise:

1. **Immediate Rollback**
   ```bash
   git reset --hard HEAD~1
   ```

2. **Partial Rollback**
   - Each phase is a separate commit
   - Can rollback to last working phase

3. **Feature Flag**
   - Disable problematic features via environment variable
   - Continue with stable phases

## Documentation Updates

### User Documentation
- No changes needed (internal fixes)

### Developer Documentation
1. Update `AGENTS.md` with helper function usage
2. Document REST API authentication requirements
3. Add session management best practices

### API Documentation
- Update OpenAPI specs if REST responses change
- Document new error responses

## Post-Implementation

### Monitoring
- Track test execution time
- Monitor for flaky tests
- Check CI/CD pipeline success rate

### Optimization
- Profile slow tests
- Optimize database fixtures
- Cache test data where possible

### Future Enhancements
- Add more comprehensive integration tests
- Implement E2E tests with real browser
- Add load testing for REST API

## Approval Requirements

- [x] Technical feasibility verified
- [ ] Test plan reviewed
- [ ] Timeline approved
- [ ] Resources allocated

## Notes

This proposal addresses the final 35% of failing tests. All core functionality (auth, cache, metrics) is already working. The remaining failures are integration issues that can be fixed systematically by improving context handling and session management.

The fixes are low-risk since they don't change the public API or user-facing behavior - they just ensure the existing code works correctly in all scenarios.

## References

- Current test results: `documentation/TEST_FIX_SUMMARY.md`
- Emmett documentation: `emmett_documentation/`
- Test infrastructure: `runtime/tests.py`
- Failing test output: See test run results above

---

**Proposal Status**: Ready for implementation
**Next Steps**: Create design document and implementation tasks

