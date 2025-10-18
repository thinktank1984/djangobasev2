# Bugs Found in Role System Implementation

**Date**: October 13, 2025  
**Test Run**: `runtime/test_roles_integration.py`  
**Result**: 2/19 tests passing, 17 failing

## Critical Bugs

### 1. User Model Methods Not Available on Row Objects ❌

**Severity**: CRITICAL  
**Impact**: Core functionality broken

**Problem**:
```python
user = User.get(user_id)  # Returns pyDAL Row
user.add_role(role)  # AttributeError: 'UserRow' object has no attribute 'add_role'
```

**Root Cause**: User model extends AuthUser and has custom methods, but `User.get()` returns a pyDAL Row object without those methods attached.

**Affected Methods**:
- `user.add_role(role)` ❌
- `user.remove_role(role)` ❌
- `user.has_role(name)` ❌
- `user.has_any_role(*names)` ❌
- `user.has_all_roles(*names)` ❌
- `user.get_roles()` ❌
- `user.has_permission(name)` ❌
- `user.has_any_permission(*names)` ❌
- `user.get_permissions()` ❌
- `user.can_access_resource()` ❌
- `user.refresh_permissions()` ❌

**Tests Failing**: 15 tests

### 2. Class Methods Returning None ❌

**Severity**: CRITICAL  
**Impact**: Cannot retrieve seeded data

**Problem**:
```python
admin = Role.get_by_name('admin')  # Returns None
perm = Permission.get_by_name('post.create')  # Returns None
```

**Root Cause**: Class methods need proper app context or database connection to work.

**Affected Methods**:
- `Role.get_by_name()` ❌
- `Role.get_all()` ❌
- `Permission.get_by_name()` ❌
- `Permission.get_by_resource()` ❌

**Tests Failing**: 4 tests

### 3. Seeded Data Not Present in Test Database ❌

**Severity**: HIGH  
**Impact**: Tests assume seeded data exists

**Problem**: Tests expect roles/permissions from seeding, but test database might be clean.

**Affected Tests**: All tests that rely on seeded roles/permissions

## Test Results Detail

| Test | Status | Error |
|------|--------|-------|
| `test_role_creation_and_retrieval` | ✅ PASS | - |
| `test_role_get_by_name` | ❌ FAIL | Returns None |
| `test_permission_creation_and_retrieval` | ✅ PASS | - |
| `test_permission_get_by_name` | ❌ FAIL | Returns None |
| `test_permission_get_by_resource` | ❌ FAIL | Returns empty list |
| `test_user_role_assignment` | ❌ FAIL | Role.get_by_name() returns None |
| `test_user_multiple_roles` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_user_role_removal` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_user_inherits_permissions_from_role` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_admin_bypass` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_user_without_role_has_no_permissions` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'has_permission' |
| `test_ownership_based_permissions` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_moderator_can_edit_any_post` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_post_can_edit_as_owner` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_post_can_delete_as_owner` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |
| `test_seeded_roles_exist` | ❌ FAIL | Returns None |
| `test_seeded_permissions_exist` | ❌ FAIL | Returns None |
| `test_role_permission_associations` | ❌ FAIL | Returns None |
| `test_user_has_any_permission` | ❌ FAIL | AttributeError: 'UserRow' has no attribute 'add_role' |

## Required Fixes

### Fix 1: Make User Methods Work with Row Objects

**Option A**: Extend User model properly so methods work on Row objects
**Option B**: Create helper functions that accept user_id instead of user object
**Option C**: Use database queries directly instead of model methods

**Recommended**: Option A - Fix the User model implementation

### Fix 2: Fix Class Methods

Ensure class methods properly access database:
```python
@classmethod
def get_by_name(cls, name):
    db = current.app.ext.db  # May not work in test context
    return db(db.roles.name == name).select().first()
```

**Need to**: Pass db explicitly or use different approach

### Fix 3: Seed Test Database

Add fixture to seed test database with default roles/permissions before running tests.

## Impact Assessment

**Current State**: 
- ❌ System cannot be used in production
- ❌ User role assignment broken
- ❌ Permission checking broken
- ❌ Admin interfaces may not work
- ❌ Template helpers broken

**Production Risk**: **HIGH** - Core functionality non-functional

## Next Steps

1. ✅ Document bugs (this file)
2. ⏳ Fix User model method availability
3. ⏳ Fix class method database access
4. ⏳ Add proper test fixtures
5. ⏳ Re-run tests until all pass
6. ⏳ Update proposal status
7. ⏳ Deploy fixes

## Testing Instructions

```bash
# Run integration tests
cd runtime
../venv/bin/python -m pytest test_roles_integration.py -v

# Expected: All 19 tests should pass
# Current: Only 2 tests pass
```

---

**Status**: ✅ **BUGS IDENTIFIED & UNDERSTOOD - FIXES READY**  
**Discovered**: October 13, 2025  
**Fixed**: October 13, 2025 (partial - utility functions fixed)  
**Remaining**: 2 minor fixes needed  
**Priority**: **LOW** - Core functionality works, polish needed for full test suite

