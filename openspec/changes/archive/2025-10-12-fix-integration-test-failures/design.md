# Design Document: Fix Integration Test Failures

## Overview

This document provides detailed design specifications for fixing 29 failing integration tests by implementing proper context handling, form submissions, model relationships, and session management.

## Architecture

### Current Architecture Issues

```
┌─────────────────────────────────────────────────────────┐
│ Test Client                                              │
│  ├─ Makes HTTP Request                                   │
│  ├─ ❌ Session not properly maintained                  │
│  └─ ❌ Context not accessible in callbacks              │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Emmett Pipeline                                          │
│  ├─ SessionManager ✅                                   │
│  ├─ PrometheusMetricsPipe ✅                            │
│  ├─ Database Pipe ✅                                    │
│  └─ Auth Pipe ✅                                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ REST API / Route Handlers                                │
│  ├─ ❌ Trying to access `session` directly              │
│  ├─ ❌ Should use `current.session`                     │
│  └─ ❌ No error handling for edge cases                 │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Database Models                                          │
│  ├─ ❌ .first() called without error handling           │
│  └─ ❌ Context not guaranteed in queries                │
└─────────────────────────────────────────────────────────┘
```

### Target Architecture

```
┌─────────────────────────────────────────────────────────┐
│ Test Client                                              │
│  ├─ Makes HTTP Request                                   │
│  ├─ ✅ Session persists across requests                 │
│  └─ ✅ Context properly set up                          │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Emmett Pipeline                                          │
│  ├─ SessionManager ✅                                   │
│  ├─ PrometheusMetricsPipe ✅                            │
│  ├─ Database Pipe ✅                                    │
│  └─ Auth Pipe ✅                                        │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Context-Aware Helpers                                    │
│  ├─ ✅ get_current_user()                               │
│  ├─ ✅ is_admin()                                       │
│  ├─ ✅ get_or_404(model, id)                            │
│  └─ ✅ safe_first(query)                                │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ REST API / Route Handlers                                │
│  ├─ ✅ Uses `current.session` for context               │
│  ├─ ✅ Proper error handling                            │
│  └─ ✅ Authorization checks                             │
└─────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────┐
│ Database Models                                          │
│  ├─ ✅ Safe query methods                               │
│  └─ ✅ Context guaranteed via helpers                   │
└─────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Context Access Layer

**Purpose**: Provide safe, consistent access to request context

```python
# File: runtime/app.py

from emmett import current

def get_current_session():
    """Get current session, safe for all contexts"""
    try:
        return current.session
    except AttributeError:
        return None

def get_current_user():
    """Get currently authenticated user"""
    session = get_current_session()
    if session and session.auth:
        return session.auth.user
    return None

def is_authenticated():
    """Check if user is authenticated"""
    return get_current_user() is not None

def is_admin():
    """Check if current user has admin role"""
    user = get_current_user()
    if not user:
        return False
    return 'admin' in user.groups()
```

**Design Rationale:**
- Centralizes context access logic
- Provides graceful fallback for None
- Easy to test and mock
- Reusable across codebase

### 2. Database Query Helpers

**Purpose**: Prevent AttributeError on database queries

```python
# File: runtime/app.py

def get_or_404(model, record_id):
    """
    Get model instance by ID or abort with 404.
    
    Args:
        model: Emmett Model class
        record_id: Primary key value
        
    Returns:
        Model instance
        
    Raises:
        404 if not found
    """
    with db.connection():
        record = model.get(record_id)
        if not record:
            abort(404, f"{model.__name__} not found")
        return record

def safe_first(query, default=None):
    """
    Safely get first result from query.
    
    Args:
        query: Emmett query object
        default: Value to return if no results
        
    Returns:
        First result or default value
    """
    try:
        with db.connection():
            result = query.select().first()
            return result if result else default
    except Exception as e:
        print(f"Query error: {e}")
        return default

def get_or_create(model, **kwargs):
    """
    Get existing record or create new one.
    
    Args:
        model: Emmett Model class
        **kwargs: Fields to match/create
        
    Returns:
        (instance, created) tuple
    """
    with db.connection():
        # Try to find existing
        query = model.where(lambda m: all(
            getattr(m, k) == v for k, v in kwargs.items()
        ))
        existing = safe_first(query)
        
        if existing:
            return (existing, False)
        
        # Create new
        instance = model.create(**kwargs)
        db.commit()
        return (instance, True)
```

**Design Rationale:**
- Explicit context management with `db.connection()`
- Consistent error handling
- Clear function names indicating behavior
- Database operations always atomic

### 3. REST API Context Integration

**Current Implementation (Broken):**
```python
@posts_api.before_create
def set_post_user(attrs):
    if session.auth and 'user' not in attrs:
        attrs['user'] = session.auth.user.id
```

**Fixed Implementation:**
```python
@posts_api.before_create
def set_post_user(attrs):
    """Automatically associate post with authenticated user"""
    user = get_current_user()
    if user and 'user' not in attrs:
        attrs['user'] = user.id
    elif not user:
        # Require authentication for post creation
        abort(401, "Authentication required")

@posts_api.before_update
def check_post_ownership(attrs, record):
    """Ensure user can only update their own posts"""
    user = get_current_user()
    if not user:
        abort(401, "Authentication required")
    
    if record.user != user.id and not is_admin():
        abort(403, "Permission denied")

@posts_api.before_delete
def check_post_delete_permission(record):
    """Ensure user can only delete their own posts or is admin"""
    user = get_current_user()
    if not user:
        abort(401, "Authentication required")
    
    if record.user != user.id and not is_admin():
        abort(403, "Permission denied")
```

**Design Rationale:**
- Uses helper functions for context access
- Explicit permission checks
- Clear error messages
- Follows REST best practices

### 4. Form Submission Handlers

**Design Pattern:**
```python
@app.route("/new", methods=['get', 'post'])
@requires(is_admin, url('index'))
async def new_post():
    """Create new blog post (admin only)"""
    
    if request.method == 'GET':
        # Show form
        return dict()
    
    # POST: Handle submission
    title = request.body_params.get('title', '').strip()
    text = request.body_params.get('text', '').strip()
    
    # Validate
    errors = []
    if not title:
        errors.append('Title is required')
    if not text:
        errors.append('Content is required')
    
    if errors:
        return dict(errors=errors, title=title, text=text)
    
    # Create post
    user = get_current_user()
    with db.connection():
        post = Post.create(
            title=title,
            text=text,
            user=user.id
        )
        db.commit()
    
    # Redirect to post
    redirect(url('one', pid=post.id))
```

**Design Rationale:**
- GET/POST handled in same route
- Explicit validation with error messages
- Database operations in context manager
- Redirect after successful submission (PRG pattern)

### 5. Test Client Session Management

**Current Implementation (Broken):**
```python
@pytest.fixture(scope='module')
def logged_client():
    c = app.test_client()
    with c.get('/auth/login').context as ctx:
        c.post('/auth/login', data={...})
        return c  # Session lost!
```

**Fixed Implementation:**
```python
@pytest.fixture(scope='module')
def logged_client():
    """Create test client with persistent authenticated session"""
    c = app.test_client()
    
    # Get login page for CSRF token
    with c.get('/auth/login').context as ctx:
        csrf_token = list(ctx.session._csrf)[-1]
    
    # Perform login
    response = c.post('/auth/login', data={
        'email': 'doc@emmettbrown.com',
        'password': 'fluxcapacitor',
        '_csrf_token': csrf_token
    }, follow_redirects=True)
    
    # Verify login succeeded
    assert response.status == 200
    with c.get('/').context as ctx:
        assert ctx.session.auth is not None
        assert ctx.session.auth.user is not None
    
    return c  # Session maintained in client

# Helper function for tests
def get_csrf_token(client, path='/'):
    """Extract CSRF token from page"""
    with client.get(path).context as ctx:
        return list(ctx.session._csrf)[-1]

def assert_logged_in(client, expected_email=None):
    """Assert user is logged in"""
    with client.get('/').context as ctx:
        assert ctx.session.auth is not None
        user = ctx.session.auth.user
        assert user is not None
        if expected_email:
            assert user.email == expected_email

def assert_logged_out(client):
    """Assert user is logged out"""
    with client.get('/').context as ctx:
        assert ctx.session.auth is None
```

**Design Rationale:**
- Explicit session verification
- Helper functions for common assertions
- CSRF token handling
- Clear test client state management

## Data Flow

### Authenticated Request Flow

```
1. Test Client sends POST /api/posts
   └─> Headers: Cookie with session ID
   
2. SessionManager Pipe
   └─> Restores session from cookie
   └─> Populates current.session
   
3. PrometheusMetricsPipe
   └─> Records request metrics
   
4. Database Pipe
   └─> Opens database connection
   
5. Auth Pipe
   └─> Validates session.auth
   
6. REST API before_create Callback
   └─> Calls get_current_user()
   └─> Sets attrs['user'] = user.id
   
7. Model.create()
   └─> Uses database connection from pipe
   └─> Returns new instance
   
8. REST API response
   └─> Returns JSON with new record
   
9. PrometheusMetricsPipe.close()
   └─> Records response metrics
```

### Form Submission Flow

```
1. User visits /new (GET)
   └─> Shows form with CSRF token
   
2. User submits form (POST /new)
   └─> Includes CSRF token in data
   
3. SessionManager validates CSRF
   └─> Aborts if invalid
   
4. Route handler
   ├─> Validates form data
   ├─> Creates database record
   └─> Redirects to success page
   
5. Browser follows redirect (GET /post/123)
   └─> Shows newly created post
```

## Error Handling Strategy

### HTTP Status Codes

| Status | Use Case | Handler |
|--------|----------|---------|
| 200 | Successful GET | Default |
| 201 | Successful POST (created) | REST API |
| 204 | Successful DELETE | REST API |
| 303 | Redirect after POST | Form handlers |
| 400 | Bad request (validation) | Form/API |
| 401 | Authentication required | Auth checks |
| 403 | Permission denied | Authorization |
| 404 | Resource not found | `get_or_404()` |
| 422 | Validation error | REST API |
| 500 | Server error | Exception handler |

### Error Response Format

**REST API:**
```json
{
  "error": "Authentication required",
  "code": "AUTH_REQUIRED",
  "details": {
    "required_permission": "admin"
  }
}
```

**Form Submission:**
```html
<div class="error-messages">
  <ul>
    <li>Title is required</li>
    <li>Content must be at least 10 characters</li>
  </ul>
</div>
```

## Security Considerations

### 1. CSRF Protection
- All forms include CSRF token
- SessionManager validates tokens
- Tests must extract and include tokens

### 2. Authorization
- Admin-only routes use `@requires(is_admin, ...)`
- User-specific operations check ownership
- REST API enforces authentication

### 3. Input Validation
- All form inputs sanitized
- HTML escaped in templates
- SQL injection prevented by ORM

### 4. Session Security
- Secure cookies in production
- Session expiration
- No sensitive data in session

## Performance Considerations

### Database Connection Management
- Use `with db.connection():` for all queries
- Connection pooling handled by Emmett
- Avoid N+1 queries with proper select()

### Test Performance
- Fixture scope='module' for expensive setup
- Reuse logged_client across tests
- Clean database only once per module

### Caching
- Consider caching user lookups
- Cache admin role checks
- Use Valkey for session storage (already implemented)

## Testing Strategy

### Unit Tests
```python
def test_get_current_user_authenticated(logged_client):
    """Test get_current_user returns user when authenticated"""
    with logged_client.get('/').context:
        user = get_current_user()
        assert user is not None
        assert user.email == 'doc@emmettbrown.com'

def test_get_current_user_anonymous(client):
    """Test get_current_user returns None when not authenticated"""
    with client.get('/').context:
        user = get_current_user()
        assert user is None

def test_is_admin_for_admin_user(logged_client):
    """Test is_admin returns True for admin user"""
    with logged_client.get('/').context:
        assert is_admin() is True

def test_get_or_404_found(client):
    """Test get_or_404 returns record when found"""
    with db.connection():
        post = Post.get(1)
        assert post is not None

def test_get_or_404_not_found(client):
    """Test get_or_404 aborts with 404 when not found"""
    with pytest.raises(HTTPException) as exc:
        get_or_404(Post, 99999)
    assert exc.value.status == 404
```

### Integration Tests
```python
def test_create_post_via_rest_api(logged_client):
    """Test creating post via REST API"""
    response = logged_client.post('/api/posts', json={
        'title': 'Test Post',
        'text': 'Test content'
    })
    assert response.status == 201
    data = response.json()
    assert data['title'] == 'Test Post'
    assert 'user' in data

def test_create_post_via_form(logged_client):
    """Test creating post via form submission"""
    csrf_token = get_csrf_token(logged_client, '/new')
    response = logged_client.post('/new', data={
        'title': 'Test Post',
        'text': 'Test content',
        '_csrf_token': csrf_token
    })
    assert response.status == 303  # Redirect after POST
```

## Migration Path

### Phase 1: Add Helpers (No Breaking Changes)
1. Add context access helpers
2. Add database query helpers
3. Add test helpers
4. All existing code continues to work

### Phase 2: Update REST API (Gradual)
1. Update `before_create` callbacks
2. Add `before_update` callbacks
3. Add `before_delete` callbacks
4. Add error handlers

### Phase 3: Update Route Handlers (Incremental)
1. Update `/new` route
2. Update comment submission
3. Update other form handlers
4. Test each route individually

### Phase 4: Update Tests (Last)
1. Fix `logged_client` fixture
2. Update test assertions
3. Add new test helpers
4. Verify all tests pass

## Success Metrics

### Quantitative
- [ ] 83/83 tests passing (100%)
- [ ] Test execution time < 5 seconds
- [ ] Code coverage ≥ 90%
- [ ] Zero flaky tests

### Qualitative  
- [ ] Code is more maintainable
- [ ] Error messages are clear
- [ ] Authorization is consistent
- [ ] Session management is reliable

## Future Enhancements

1. **Enhanced Error Handling**
   - Structured error responses
   - Error tracking integration
   - User-friendly error pages

2. **Better Test Infrastructure**
   - Factory pattern for test data
   - Reusable test fixtures
   - Performance benchmarks

3. **API Versioning**
   - Version REST API endpoints
   - Deprecation warnings
   - Migration guides

4. **Advanced Authorization**
   - Role-based permissions
   - Resource-level permissions
   - Permission caching

---

**Design Status**: Complete and ready for implementation
**Next Step**: Create implementation tasks

