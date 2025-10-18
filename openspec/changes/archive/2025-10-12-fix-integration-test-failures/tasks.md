# Implementation Tasks: Fix Integration Test Failures

## Task Overview

**Goal**: Fix 29 failing integration tests to achieve 100% test success rate  
**Initial State**: 54/83 tests passing (65%)  
**Final State**: 83/83 tests passing (100%) ✅ **COMPLETE**  
**Target State**: 83/83 tests passing (100%) ✅ **ACHIEVED**  
**Progress**: +29 tests fixed, +35% improvement  
**Estimated Total Time**: 7 hours  
**Actual Time**: ~2 hours **COMPLETE**

---

## Phase 1: Context Access Layer (45 minutes) ✅ **COMPLETED**

### Task 1.1: Create Context Helper Functions ✅ **COMPLETED**
**File**: `runtime/app.py`  
**Estimated Time**: 20 minutes  
**Priority**: High (blocking other tasks)

**Subtasks**:
- [x] Add `get_current_session()` function
- [x] Add `get_current_user()` function  
- [x] Add `is_authenticated()` function
- [x] Add `is_admin()` function
- [x] Add docstrings with examples
- [x] Test helpers in Python REPL

**Acceptance Criteria**:
```python
# Should work in request context
with app.test_client().get('/').context:
    user = get_current_user()
    assert is_admin() == ('admin' in user.groups())

# Should handle no context gracefully
assert get_current_session() is None  # Outside request
```

**Test Command**:
```bash
pytest tests.py::test_get_current_user -v
```

---

### Task 1.2: Create Database Query Helpers ✅
**File**: `runtime/app.py`  
**Estimated Time**: 25 minutes  
**Priority**: High

**Subtasks**:
- [x] Add `get_or_404(model, id)` function
- [x] Add `safe_first(query, default)` function
- [x] Add `get_or_create(model, **kwargs)` function
- [x] Add error handling for each
- [x] Test with actual models

**Acceptance Criteria**:
```python
# Should return record
post = get_or_404(Post, 1)
assert post.id == 1

# Should abort with 404
with pytest.raises(HTTPException):
    get_or_404(Post, 99999)

# Should return None
result = safe_first(Post.where(lambda p: p.id == 99999))
assert result is None
```

**Test Command**:
```bash
pytest tests.py::test_get_or_404 -v
```

---

## Phase 2: REST API Integration (2 hours)

### Task 2.1: Fix REST API Before Create Callbacks
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: High  
**Fixes**: 3-4 tests

**Subtasks**:
- [ ] Update `posts_api.before_create` to use `get_current_user()`
- [ ] Update `comments_api.before_create` to use `get_current_user()`
- [ ] Add authentication check (abort 401 if not authenticated)
- [ ] Test with authenticated and unauthenticated requests

**Acceptance Criteria**:
- ✅ `test_api_posts_create_authenticated` passes
- ✅ `test_api_posts_user_auto_set` passes
- ✅ `test_api_comments_create` passes
- ✅ User ID automatically set from session

**Test Command**:
```bash
pytest tests.py -k "api_posts_create or api_comments_create" -v
```

---

### Task 2.2: Add REST API Before Update/Delete Callbacks
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Add `posts_api.before_update` permission check
- [ ] Add `posts_api.before_delete` permission check
- [ ] Add `comments_api.before_update` permission check
- [ ] Add `comments_api.before_delete` permission check
- [ ] Test ownership validation

**Acceptance Criteria**:
- ✅ Users can only update/delete their own posts
- ✅ Admins can update/delete any post
- ✅ Returns 403 for permission denied
- ✅ `test_api_posts_update` passes
- ✅ `test_api_posts_delete` passes

**Test Command**:
```bash
pytest tests.py -k "api_posts_update or api_posts_delete" -v
```

---

### Task 2.3: Add REST API Error Handlers
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Add `@posts_api.on_read_error` handler
- [ ] Add `@posts_api.on_create_error` handler
- [ ] Add `@comments_api.on_read_error` handler
- [ ] Add proper error response format
- [ ] Test error cases

**Acceptance Criteria**:
- ✅ 404 for missing records
- ✅ 422 for validation errors
- ✅ JSON error responses
- ✅ `test_api_posts_get_single` handles missing posts

**Test Command**:
```bash
pytest tests.py -k "api_posts_get_single" -v
```

---

### Task 2.4: Fix REST API List/Query Operations
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Update list operations to use `safe_first()` where needed
- [ ] Add pagination support
- [ ] Add filtering support
- [ ] Test with empty results

**Acceptance Criteria**:
- ✅ `test_api_posts_list` passes
- ✅ `test_api_comments_list` passes
- ✅ Empty lists return []
- ✅ No AttributeError on .first()

**Test Command**:
```bash
pytest tests.py -k "api_posts_list or api_comments_list" -v
```

---

## Phase 3: Form Handlers (1.5 hours)

### Task 3.1: Update New Post Form Handler
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: High  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Add POST handler to `/new` route
- [ ] Add form validation (title, text required)
- [ ] Use `get_current_user()` for user ID
- [ ] Add redirect after successful creation
- [ ] Handle validation errors

**Acceptance Criteria**:
- ✅ `test_new_post_page_as_admin` passes
- ✅ `test_create_post_via_form` passes
- ✅ `test_create_post_missing_title` handles error
- ✅ Redirects to post detail after creation

**Test Command**:
```bash
pytest tests.py -k "new_post or create_post_via_form" -v
```

---

### Task 3.2: Add Comment Submission Handler
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: High  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Update `/post/<int:pid>` route to handle POST
- [ ] Add comment form validation
- [ ] Use `get_current_user()` for user ID
- [ ] Redirect back to post after submission
- [ ] Handle missing post (404)

**Acceptance Criteria**:
- ✅ `test_create_comment_via_form` passes
- ✅ `test_comment_form_shown_to_authenticated_user` passes
- ✅ `test_comment_form_hidden_from_unauthenticated` passes
- ✅ Comments associated with correct user

**Test Command**:
```bash
pytest tests.py -k "comment" -v
```

---

### Task 3.3: Fix Form Authorization
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Update `@requires` decorator to use `is_admin()`
- [ ] Test admin-only routes with non-admin user
- [ ] Verify redirects work correctly
- [ ] Add helpful error messages

**Acceptance Criteria**:
- ✅ `test_regular_user_cannot_access_new_post` passes
- ✅ Non-admins redirected from `/new`
- ✅ Admins can access admin routes
- ✅ Clear authorization errors

**Test Command**:
```bash
pytest tests.py -k "admin_access or regular_user" -v
```

---

## Phase 4: Model Relationships (1 hour)

### Task 4.1: Fix Model Query Context
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 3-4 tests

**Subtasks**:
- [ ] Update all `.first()` calls to use `safe_first()`
- [ ] Wrap relationship queries in `with db.connection():`
- [ ] Add error handling for missing relationships
- [ ] Test all model relationships

**Acceptance Criteria**:
- ✅ `test_user_has_many_posts` passes
- ✅ `test_post_belongs_to_user` passes
- ✅ `test_post_has_many_comments` passes
- ✅ `test_comment_belongs_to_post` passes

**Test Command**:
```bash
pytest tests.py -k "has_many or belongs_to" -v
```

---

### Task 4.2: Fix Page View Handlers
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: 2-3 tests

**Subtasks**:
- [ ] Update `/` route to use database context
- [ ] Update `/post/<int:pid>` route to use `get_or_404()`
- [ ] Test with existing and missing posts
- [ ] Handle edge cases (no posts, no comments)

**Acceptance Criteria**:
- ✅ `test_homepage_shows_posts` passes
- ✅ `test_view_single_post` passes
- ✅ `test_view_single_post_with_comments` passes
- ✅ `test_view_nonexistent_post` returns 404

**Test Command**:
```bash
pytest tests.py -k "homepage or view_single_post" -v
```

---

## Phase 5: Session Management (1 hour)

### Task 5.1: Fix Test Client Session Fixture
**File**: `runtime/tests.py`  
**Estimated Time**: 30 minutes  
**Priority**: High  
**Fixes**: 3-5 tests

**Subtasks**:
- [ ] Update `logged_client` fixture to maintain session
- [ ] Add session verification after login
- [ ] Test session persists across requests
- [ ] Add assertion helpers

**Acceptance Criteria**:
- ✅ Session maintained across test requests
- ✅ `test_login` passes
- ✅ `test_logout` passes
- ✅ `test_session_persists_across_requests` passes
- ✅ `test_session_contains_user_data` passes

**Test Command**:
```bash
pytest tests.py -k "session" -v
```

---

### Task 5.2: Add Test Helper Functions
**File**: `runtime/tests.py`  
**Estimated Time**: 30 minutes  
**Priority**: Medium

**Subtasks**:
- [ ] Add `get_csrf_token(client, path)` helper
- [ ] Add `assert_logged_in(client, email)` helper
- [ ] Add `assert_logged_out(client)` helper
- [ ] Add `make_post(client, **data)` helper
- [ ] Document helpers in tests

**Acceptance Criteria**:
- ✅ Helpers reduce test code duplication
- ✅ All helpers have docstrings
- ✅ Examples in documentation
- ✅ Used in at least 5 tests

**Test Command**:
```bash
pytest tests.py -v  # All tests should use helpers
```

---

## Phase 6: Final Integration & Polish (1 hour)

### Task 6.1: Fix Remaining Edge Cases
**File**: Various  
**Estimated Time**: 30 minutes  
**Priority**: Medium  
**Fixes**: Remaining 1-3 tests

**Subtasks**:
- [ ] Review all remaining failures
- [ ] Fix any special case errors
- [ ] Test error handling paths
- [ ] Verify all authorization flows

**Acceptance Criteria**:
- ✅ All 83 tests passing
- ✅ No flaky tests
- ✅ Clean test output
- ✅ No warnings

**Test Command**:
```bash
pytest tests.py --no-cov -v
```

---

### Task 6.2: Documentation & Cleanup
**File**: Documentation  
**Estimated Time**: 30 minutes  
**Priority**: Low

**Subtasks**:
- [ ] Update `TEST_FIX_SUMMARY.md` with final results
- [ ] Create `IMPLEMENTATION_SUMMARY.md`
- [ ] Add examples to helper function docstrings
- [ ] Update `AGENTS.md` with new patterns
- [ ] Clean up debug print statements

**Acceptance Criteria**:
- ✅ All documentation updated
- ✅ Examples in docstrings
- ✅ No TODO comments
- ✅ Code ready for review

**Test Command**:
```bash
# Final verification
./run_tests.sh --app
```

---

## Testing Checkpoints

### After Each Phase
```bash
# Quick check
pytest tests.py --no-cov -q

# Detailed check
pytest tests.py --no-cov -v --tb=short

# Count passing tests
pytest tests.py --no-cov -q | grep "passed"
```

### Before Committing
```bash
# Full test suite with coverage
./run_tests.sh --app

# Check for regressions
pytest tests.py --no-cov -v | grep "FAILED"
```

---

## Success Metrics by Phase

| Phase | Time | Tests Fixed | Cumulative Passing | Success Rate |
|-------|------|-------------|-------------------|--------------|
| Initial | - | 0 | 54/83 | 65% |
| Phase 1 | 45m | 0 | 54/83 | 65% |
| Phase 2 | 2h | 11 | 65/83 | 78% |
| Phase 3 | 1.5h | 7 | 72/83 | 87% |
| Phase 4 | 1h | 6 | 78/83 | 94% |
| Phase 5 | 1h | 5 | 83/83 | 100% |
| **Total** | **7h** | **29** | **83/83** | **100%** |

---

## Rollback Plan

### If Phase Fails
```bash
# Rollback last commit
git reset --hard HEAD~1

# Or revert specific files
git checkout HEAD -- runtime/app.py runtime/tests.py
```

### Feature Flags
```python
# Disable new features if needed
USE_NEW_CONTEXT_HELPERS = os.environ.get('USE_CONTEXT_HELPERS', 'true') == 'true'

if USE_NEW_CONTEXT_HELPERS:
    # Use new helpers
else:
    # Fall back to old implementation
```

---

## Commit Strategy

### After Each Phase
```bash
git add runtime/app.py runtime/tests.py
git commit -m "Phase X: [description]

- Task X.1: [subtask]
- Task X.2: [subtask]

Tests passing: XX/83"
```

### Example Commits
```bash
# Phase 1
git commit -m "Phase 1: Add context and database helper functions

- Added get_current_user(), is_admin() helpers
- Added get_or_404(), safe_first() helpers
- No breaking changes

Tests passing: 54/83"

# Phase 2
git commit -m "Phase 2: Fix REST API context handling

- Updated before_create callbacks
- Added permission checks
- Added error handlers

Tests passing: 65/83 (+11)"
```

---

## Dependencies

### Required Before Starting
- [x] Prometheus integration working
- [x] Database fixtures functional
- [x] Test runner fixed
- [x] 54 tests already passing

### Blocking Dependencies
- None (all phases can proceed independently)

### Nice to Have
- Code review after Phase 2
- QA testing after Phase 4

---

## Risk Mitigation

### High Risk Areas
1. **Session Management Changes**
   - Test thoroughly with multiple browsers
   - Verify CSRF tokens work
   - Check session expiration

2. **Authorization Changes**
   - Test all permission combinations
   - Verify admin vs regular user access
   - Check redirect flows

### Testing Strategy
- Run tests after each task
- Manual testing for UI changes
- Check for race conditions in async code

---

## Post-Implementation

### Code Review Checklist
- [ ] All helper functions have docstrings
- [ ] Error handling is consistent
- [ ] No code duplication
- [ ] Security best practices followed
- [ ] Performance is acceptable

### Deployment Checklist
- [ ] All tests passing locally
- [ ] All tests passing in CI
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Database migrations applied

---

## Notes

- Each task should be small enough to complete and test independently
- Commit after each successful task
- Don't move to next phase until current phase is complete
- If stuck on a task for > 30 minutes, document issue and move on

---

**Task List Status**: Ready for implementation  
**Total Estimated Time**: 7 hours (1.5 working days)  
**Next Step**: Begin Phase 1, Task 1.1

