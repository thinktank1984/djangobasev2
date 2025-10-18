# Permissions Auto-Generation Specification

## ADDED Requirements

### Requirement: Automatic Permission Enforcement
The system SHALL automatically generate and enforce permission checks for all auto-generated API endpoints and pages based on model decorators and metadata.

#### Scenario: Require authentication for write operations
- **WHEN** model has `Meta.require_auth_for_write = True` (default)
- **THEN** POST, PUT, DELETE requests require authenticated user
- **AND** return 401 Unauthorized if user not authenticated
- **AND** GET requests are public unless `require_auth_for_read = True`

#### Scenario: Require authentication for all operations
- **WHEN** model has `Meta.require_auth_for_read = True`
- **THEN** all API requests (GET, POST, PUT, DELETE) require authentication
- **AND** return 401 Unauthorized if user not authenticated

#### Scenario: Check resource ownership for updates
- **WHEN** authenticated user attempts PUT `/api/posts/:id`
- **THEN** verify user owns the resource (via `Meta.ownership_field`)
- **AND** allow update if `user.id == post.user_id` OR user is admin
- **AND** return 403 Forbidden if neither condition is met

#### Scenario: Check resource ownership for deletes
- **WHEN** authenticated user attempts DELETE `/api/posts/:id`
- **THEN** verify user owns the resource or is admin
- **AND** allow delete if ownership or admin check passes
- **AND** return 403 Forbidden otherwise

---

### Requirement: Method-Level Permission Decorators
The system SHALL enforce permissions specified via `@requires_permission` decorators on model methods.

#### Scenario: Require specific permission for method
- **WHEN** model method has `@requires_permission('admin')` decorator
- **THEN** check if current user has 'admin' permission before executing
- **AND** raise 403 Forbidden if user lacks permission
- **AND** execute method if user has permission

#### Scenario: Multiple required permissions
- **WHEN** model method has `@requires_permission('admin', 'moderator')` decorator with multiple values
- **THEN** require user to have ANY of the specified permissions (OR logic)
- **AND** raise 403 if user has none of the permissions

#### Scenario: All required permissions
- **WHEN** model method has `@requires_all_permissions('editor', 'published')` decorator
- **THEN** require user to have ALL of the specified permissions (AND logic)
- **AND** raise 403 if user lacks any permission

---

### Requirement: Role-Based Access Control (RBAC)
The system SHALL support role-based permissions with admin, user, and custom roles.

#### Scenario: Admin bypass for ownership checks
- **WHEN** user has 'admin' role
- **THEN** allow access to all resources regardless of ownership
- **AND** skip ownership field checks for admin users

#### Scenario: Check user role membership
- **WHEN** user has specific role (e.g., 'moderator')
- **THEN** grant permissions associated with that role
- **AND** allow role-specific operations

#### Scenario: Custom role definition
- **WHEN** application defines custom role with permissions
- **THEN** respect custom role in permission checks
- **AND** allow configuration of role hierarchy

---

### Requirement: Field-Level Permissions
The system SHALL support field-level read and write permissions.

#### Scenario: Hide sensitive fields from non-admin users
- **WHEN** field has `@readonly(unless='admin')` decorator
- **THEN** exclude field from API responses for non-admin users
- **AND** include field for admin users
- **AND** ignore field in update requests from non-admin users

#### Scenario: Prevent field modification
- **WHEN** field has `@readonly` decorator
- **THEN** ignore field in POST/PUT requests
- **AND** return validation error if client attempts to modify
- **AND** allow field to be set programmatically in model methods

#### Scenario: Field visible only to owner
- **WHEN** field has `@visible_to_owner` decorator
- **THEN** include field in API response only if requesting user owns the record
- **AND** exclude field for other users (even admins, unless specified)

---

### Requirement: Permission Inheritance
The system SHALL support permission inheritance from related models and parent classes.

#### Scenario: Inherit permissions from parent model
- **WHEN** model has `Meta.inherit_permissions_from = 'post'`
- **THEN** apply parent model's permission checks to child model
- **AND** check parent ownership (e.g., comment inherits post permissions)

#### Scenario: Parent-child permission propagation
- **WHEN** user lacks permission for parent resource
- **THEN** also deny permission for child resources
- **AND** example: if user can't read post, they can't read post's comments

---

### Requirement: Conditional Permissions
The system SHALL support dynamic permissions based on model state.

#### Scenario: Conditional write permission
- **WHEN** model has `can_edit()` method returning boolean
- **THEN** call method to determine if current user can edit
- **AND** allow update only if method returns True
- **AND** return 403 if method returns False

#### Scenario: Time-based permissions
- **WHEN** model has `can_edit()` checking time constraints
- **THEN** enforce time-based restrictions (e.g., no edits after 24 hours)
- **AND** return 403 with appropriate error message

#### Scenario: State-based permissions
- **WHEN** model has `can_delete()` checking model state
- **THEN** enforce state restrictions (e.g., can't delete published posts)
- **AND** return 403 with state-specific error message

---

### Requirement: Permission Scoping
The system SHALL automatically scope queries to only return records the current user has permission to access.

#### Scenario: Auto-scope list queries
- **WHEN** user requests GET `/api/posts`
- **THEN** automatically filter results to records user can access
- **AND** apply ownership filter if `Meta.auto_scope = True`
- **AND** return only user's own posts unless user is admin

#### Scenario: Disable auto-scoping for public resources
- **WHEN** model has `Meta.auto_scope = False`
- **THEN** return all records in list queries
- **AND** still enforce permissions on individual record operations

#### Scenario: Custom scope method
- **WHEN** model defines `scope_for_user(user, query)` method
- **THEN** call method to apply custom query filters
- **AND** use returned query for all list operations

---

### Requirement: API Key and Token Permissions
The system SHALL support permission management for API keys and tokens.

#### Scenario: API key with limited permissions
- **WHEN** request authenticated with API key
- **THEN** enforce permissions associated with that API key
- **AND** deny operations exceeding key's permission scope

#### Scenario: Token-based permission scopes
- **WHEN** request authenticated with OAuth/JWT token
- **THEN** respect token scopes (e.g., `read:posts`, `write:posts`)
- **AND** deny operations not in token scope
- **AND** return 403 with scope requirements

---

### Requirement: Permission Audit Logging
The system SHALL log all permission checks and denials for audit purposes.

#### Scenario: Log permission denial
- **WHEN** permission check fails
- **THEN** log event with user ID, resource, action, and timestamp
- **AND** include reason for denial
- **AND** provide audit trail for security review

#### Scenario: Log successful sensitive operations
- **WHEN** admin performs privileged operation
- **THEN** log event with full context
- **AND** include IP address and user agent
- **AND** enable security monitoring and compliance

---

### Requirement: Permission Testing Utilities
The system SHALL provide utilities for testing permissions in development and test environments.

#### Scenario: Test permission for user
- **WHEN** calling `Post.test_permission(user, 'update', post)`
- **THEN** return boolean indicating if permission would be granted
- **AND** include explanation if permission would be denied
- **AND** don't actually perform the operation

#### Scenario: List user permissions for model
- **WHEN** calling `Post.get_permissions(user)`
- **THEN** return list of all operations user can perform
- **AND** include: `['read', 'create', 'update:own', 'delete:own']`

---

## Permission Configuration Reference

### Model Meta Options

```python
class Post(Model, ActiveRecord):
    class Meta:
        # Authentication Requirements
        require_auth_for_read = False      # Default: False
        require_auth_for_write = True      # Default: True
        
        # Ownership
        ownership_field = 'user_id'        # Default: 'user_id'
        auto_scope = True                  # Default: True (filter by ownership)
        
        # Admin Override
        admin_bypass_ownership = True      # Default: True
        admin_roles = ['admin', 'superuser']  # Default: ['admin']
        
        # Inheritance
        inherit_permissions_from = None    # Default: None
        
        # Conditional Methods
        permission_methods = {
            'update': 'can_edit',          # Call post.can_edit(user) for updates
            'delete': 'can_delete'         # Call post.can_delete(user) for deletes
        }
```

### Field-Level Permission Decorators

```python
class User(Model, ActiveRecord):
    email = Field.string()
    
    @readonly
    def created_at(self):
        """Cannot be modified after creation."""
        pass
    
    @readonly(unless='admin')
    def is_verified(self):
        """Only admins can modify."""
        pass
    
    @visible_to_owner
    def api_key(self):
        """Only visible to resource owner."""
        pass
    
    @requires_permission('admin')
    def ban(self):
        """Only admins can ban users."""
        self.status = 'banned'
        self.save()
```

---

## Permission Check Flow

```
Request arrives
    ↓
Authentication Check
    ├─ No user → Check if auth required → 401 if required
    └─ User authenticated → Continue
    ↓
Operation Permission Check
    ├─ Is admin? → Allow (if admin_bypass_ownership = True)
    ├─ Read operation? → Check require_auth_for_read
    └─ Write operation? → Check require_auth_for_write
    ↓
Ownership Check (if applicable)
    ├─ Resource has ownership_field? → Check user.id == resource[ownership_field]
    └─ No ownership field → Skip
    ↓
Custom Permission Method (if defined)
    ├─ Model has can_edit/can_delete? → Call method
    └─ Method returns False → 403 Forbidden
    ↓
Field-Level Permissions
    ├─ Filter response fields based on @visible_to_owner, @readonly
    └─ Validate request doesn't modify @readonly fields
    ↓
Permission Granted → Process Request
```

---

## Integration Examples

### Example 1: Blog Post with Ownership

```python
class Post(Model, ActiveRecord):
    title = Field.string()
    content = Field.text()
    user_id = Field.int()
    published = Field.bool()
    
    def can_edit(self, user):
        """Custom edit permission: owner or admin, and not if published."""
        is_owner_or_admin = user.id == self.user_id or user.is_admin()
        return is_owner_or_admin and not self.published
    
    @requires_permission('admin')
    def feature(self):
        """Only admins can feature posts."""
        self.featured = True
        self.save()
    
    class Meta:
        ownership_field = 'user_id'
        permission_methods = {
            'update': 'can_edit',
            'delete': 'can_edit'
        }
```

**Resulting Permissions**:
- Anyone can read posts (GET /api/posts, GET /api/posts/:id)
- Authenticated users can create posts (POST /api/posts)
- Owners can edit unpublished posts (PUT /api/posts/:id)
- Owners cannot edit published posts
- Admins can edit any post, even published
- Only admins can call `post.feature()`

---

### Example 2: Private User Profile

```python
class UserProfile(Model, ActiveRecord):
    user_id = Field.int()
    bio = Field.text()
    
    @visible_to_owner
    def email(self):
        """Email only visible to profile owner."""
        pass
    
    @readonly(unless='admin')
    def reputation_score(self):
        """Only admins can modify reputation."""
        pass
    
    class Meta:
        require_auth_for_read = True
        ownership_field = 'user_id'
        auto_scope = True  # Users only see their own profile
```

**Resulting Permissions**:
- Must be authenticated to read profiles (GET /api/profiles)
- Users only see their own profile in list
- Email field excluded unless requesting user owns profile
- Reputation score is readonly for non-admins

---

### Example 3: Hierarchical Permissions (Comment inherits from Post)

```python
class Comment(Model, ActiveRecord):
    post_id = Field.int()
    user_id = Field.int()
    content = Field.text()
    
    def can_edit(self, user):
        """Can edit if owns comment AND can access parent post."""
        post = Post.get(self.post_id)
        if not post:
            return False
        
        # Must own comment
        if user.id != self.user_id and not user.is_admin():
            return False
        
        # Must have read access to post
        return post.can_read(user)
    
    class Meta:
        ownership_field = 'user_id'
        inherit_permissions_from = 'post'
        permission_methods = {
            'update': 'can_edit',
            'delete': 'can_edit'
        }
```

**Resulting Permissions**:
- Comment permissions inherit from parent post
- User must have post read access to read comments
- User must own comment to edit/delete (even if they own post)
- Admins can moderate any comment

---

## Permission Error Responses

### 401 Unauthorized
```json
{
  "error": "Authentication required",
  "code": "unauthorized",
  "required_auth": true
}
```

### 403 Forbidden (Ownership)
```json
{
  "error": "You don't have permission to modify this resource",
  "code": "forbidden",
  "reason": "not_owner",
  "required_permission": "ownership or admin role"
}
```

### 403 Forbidden (Role)
```json
{
  "error": "Insufficient permissions",
  "code": "forbidden",
  "reason": "missing_role",
  "required_roles": ["admin", "moderator"]
}
```

### 403 Forbidden (State)
```json
{
  "error": "Cannot edit published posts",
  "code": "forbidden",
  "reason": "invalid_state",
  "current_state": "published"
}
```

