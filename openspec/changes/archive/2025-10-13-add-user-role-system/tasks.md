# Implementation Tasks

## 1. Database Models

- [x] 1.1 Create Role model
  - [x] 1.1.1 Add Role class inheriting from Model and ActiveRecord
  - [x] 1.1.2 Define fields: name (unique), description, created_at
  - [x] 1.1.3 Add validation for unique role names
  - [x] 1.1.4 Add has_many relationship to users and permissions
  - [x] 1.1.5 Add `get_by_name()` class method

- [x] 1.2 Create Permission model
  - [x] 1.2.1 Add Permission class inheriting from Model and ActiveRecord
  - [x] 1.2.2 Define fields: name (unique), resource, action, description
  - [x] 1.2.3 Add validation for permission name format (resource.action)
  - [x] 1.2.4 Add has_many relationship to roles
  - [x] 1.2.5 Add `get_by_name()` and `get_by_resource()` class methods

- [x] 1.3 Create UserRole association model
  - [x] 1.3.1 Add UserRole class for many-to-many user-role relationship
  - [x] 1.3.2 Define fields: user (reference), role (reference), assigned_at, assigned_by
  - [x] 1.3.3 Add unique constraint on (user, role) combination

- [x] 1.4 Create RolePermission association model
  - [x] 1.4.1 Add RolePermission class for many-to-many role-permission relationship
  - [x] 1.4.2 Define fields: role (reference), permission (reference), granted_at, granted_by
  - [x] 1.4.3 Add unique constraint on (role, permission) combination

- [x] 1.5 Create database migration
  - [x] 1.5.1 Generate migration for new tables
  - [x] 1.5.2 Test migration up and down

## 2. User Model Extensions

- [x] 2.1 Add role management methods to User model
  - [x] 2.1.1 Add `get_roles()` method returning list of role names
  - [x] 2.1.2 Add `has_role(role_name)` method checking role membership
  - [x] 2.1.3 Add `has_any_role(*role_names)` method for multiple role check
  - [x] 2.1.4 Add `add_role(role)` method for assigning roles
  - [x] 2.1.5 Add `remove_role(role)` method for removing roles

- [x] 2.2 Add permission checking methods to User model
  - [x] 2.2.1 Add `get_permissions()` method returning all user permissions
  - [x] 2.2.2 Add `has_permission(permission_name)` method
  - [x] 2.2.3 Add `has_any_permission(*permission_names)` method
  - [x] 2.2.4 Add `can_access_resource(resource, action, instance=None)` for ownership checks

- [x] 2.3 Add permission caching
  - [x] 2.3.1 Cache permissions in session on first access
  - [x] 2.3.2 Add cache invalidation on role changes
  - [x] 2.3.3 Add `refresh_permissions()` method

## 3. Decorators and Authorization

- [x] 3.1 Update requires_permission decorator
  - [x] 3.1.1 Modify to check user permissions via role system
  - [x] 3.1.2 Add admin role bypass
  - [x] 3.1.3 Add support for ownership-based permissions (.own suffix)
  - [x] 3.1.4 Add clear error messages for permission denials

- [x] 3.2 Create requires_role decorator
  - [x] 3.2.1 Implement decorator for single role requirement
  - [x] 3.2.2 Add 401 response for unauthenticated users
  - [x] 3.2.3 Add 403 response for authenticated users without role
  - [x] 3.2.4 Add route-level application

- [x] 3.3 Create requires_any_role decorator
  - [x] 3.3.1 Implement decorator accepting multiple roles
  - [x] 3.3.2 Pass if user has any of the specified roles
  - [x] 3.3.3 Add error handling and responses

- [x] 3.4 Create requires_all_roles decorator
  - [x] 3.4.1 Implement decorator requiring all specified roles
  - [x] 3.4.2 Add validation and error handling

## 4. Default Roles and Permissions

- [x] 4.1 Create role seeding system
  - [x] 4.1.1 Add `seed_roles()` function
  - [x] 4.1.2 Define Admin role with all permissions
  - [x] 4.1.3 Define Moderator role with content management permissions
  - [x] 4.1.4 Define Author role with own content permissions
  - [x] 4.1.5 Define Viewer role with read-only permissions

- [x] 4.2 Create permission seeding system
  - [x] 4.2.1 Add `seed_permissions()` function
  - [x] 4.2.2 Define standard CRUD permissions for Post model
  - [x] 4.2.3 Define standard CRUD permissions for Comment model
  - [x] 4.2.4 Define user management permissions
  - [x] 4.2.5 Define role management permissions

- [x] 4.3 Update setup command
  - [x] 4.3.1 Call seed_permissions() in setup
  - [x] 4.3.2 Call seed_roles() in setup
  - [x] 4.3.3 Assign Admin role to default admin user
  - [x] 4.3.4 Add idempotency (don't recreate if exists)

## 5. Model Updates

- [x] 5.1 Update Post model
  - [x] 5.1.1 Add Meta.permissions configuration
  - [x] 5.1.2 Update can_edit() to use permission system
  - [x] 5.1.3 Update can_delete() to use permission system
  - [x] 5.1.4 Add @requires_permission to sensitive methods

- [x] 5.2 Update Comment model
  - [x] 5.2.1 Add Meta.permissions configuration
  - [x] 5.2.2 Update can_edit() to use permission system
  - [x] 5.2.3 Update can_delete() to use permission system

## 6. Auto UI Generation

- [x] 6.1 Generate Role management UI
  - [x] 6.1.1 Call auto_ui(app, Role, '/admin/roles')
  - [x] 6.1.2 Configure auto_ui_config for Role model
  - [x] 6.1.3 Add custom role detail template showing permissions
  - [x] 6.1.4 Add custom role detail template showing assigned users

- [x] 6.2 Generate Permission management UI
  - [x] 6.2.1 Call auto_ui(app, Permission, '/admin/permissions')
  - [x] 6.2.2 Configure auto_ui_config for Permission model
  - [x] 6.2.3 Add grouping by resource in list view
  - [x] 6.2.4 Add custom permission detail template showing roles

- [x] 6.3 Create role-permission assignment interface
  - [x] 6.3.1 Create route for role-permission management page
  - [x] 6.3.2 Create template with permission checkboxes
  - [x] 6.3.3 Add AJAX handler for toggling permissions
  - [x] 6.3.4 Add bulk assignment functionality

- [x] 6.4 Create user-role assignment interface
  - [x] 6.4.1 Add role section to user detail page
  - [x] 6.4.2 Add dropdown for assigning roles
  - [x] 6.4.3 Add remove button for each assigned role
  - [x] 6.4.4 Show effective permissions on user page

- [x] 6.5 Create permission matrix view
  - [x] 6.5.1 Create route /admin/permissions/matrix
  - [x] 6.5.2 Create matrix template (roles × permissions)
  - [x] 6.5.3 Add AJAX toggling in matrix cells
  - [x] 6.5.4 Add filtering and search

## 7. Template Helpers

- [x] 7.1 Add template context helpers
  - [x] 7.1.1 Make current_user available in all templates
  - [x] 7.1.2 Add has_permission() helper function
  - [x] 7.1.3 Add has_role() helper function
  - [x] 7.1.4 Add get_user_permissions() helper

- [x] 7.2 Update existing templates
  - [x] 7.2.1 Update layout.html to conditionally show admin links
  - [x] 7.2.2 Update index.html to show/hide create post link
  - [x] 7.2.3 Update one.html to show edit/delete based on permissions
  - [x] 7.2.4 Add role/permission indicators in UI

## 8. REST API Integration

- [x] 8.1 Add permission checks to REST endpoints
  - [x] 8.1.1 Update posts_api to check permissions
  - [x] 8.1.2 Update comments_api to check permissions
  - [x] 8.1.3 Add ownership checks for update/delete

- [x] 8.2 Create REST API for roles
  - [x] 8.2.1 Create rest_module for Role
  - [x] 8.2.2 Restrict to admin users only
  - [x] 8.2.3 Add endpoints for role-permission management

- [x] 8.3 Create REST API for permissions
  - [x] 8.3.1 Create rest_module for Permission (read-only)
  - [x] 8.3.2 Add endpoint to list permissions by resource

## 9. OpenAPI Documentation

- [x] 9.1 Update OpenAPI generator
  - [x] 9.1.1 Extract permission requirements from model Meta
  - [x] 9.1.2 Add security requirements to OpenAPI spec
  - [x] 9.1.3 Document role requirements in endpoint descriptions

- [x] 9.2 Register new REST modules
  - [x] 9.2.1 Register roles_api with OpenAPI generator
  - [x] 9.2.2 Register permissions_api with OpenAPI generator

## 10. Testing

- [x] 10.1 Unit tests for models
  - [x] 10.1.1 Test Role model creation and methods
  - [x] 10.1.2 Test Permission model creation and validation
  - [x] 10.1.3 Test User role management methods
  - [x] 10.1.4 Test User permission checking methods

- [x] 10.2 Unit tests for decorators
  - [x] 10.2.1 Test requires_permission decorator
  - [x] 10.2.2 Test requires_role decorator
  - [x] 10.2.3 Test requires_any_role decorator
  - [x] 10.2.4 Test admin bypass behavior

- [x] 10.3 Integration tests for authorization
  - [x] 10.3.1 Test route protection with different roles
  - [x] 10.3.2 Test ownership-based permissions
  - [x] 10.3.3 Test permission caching and invalidation
  - [x] 10.3.4 Test role hierarchy (if implemented)

- [x] 10.4 UI tests
  - [x] 10.4.1 Test role CRUD operations
  - [x] 10.4.2 Test permission assignment to roles
  - [x] 10.4.3 Test role assignment to users
  - [x] 10.4.4 Test permission matrix functionality

- [x] 10.5 API tests
  - [x] 10.5.1 Test REST API permission enforcement
  - [x] 10.5.2 Test role/permission API endpoints
  - [x] 10.5.3 Test unauthorized access scenarios

## 11. Documentation

- [x] 11.1 Update code documentation
  - [x] 11.1.1 Document Role model with docstrings
  - [x] 11.1.2 Document Permission model with docstrings
  - [x] 11.1.3 Document decorators with usage examples
  - [x] 11.1.4 Document User role methods

- [x] 11.2 Create usage guide
  - [x] 11.2.1 Document how to create new roles
  - [x] 11.2.2 Document how to define custom permissions
  - [x] 11.2.3 Document how to protect routes and methods
  - [x] 11.2.4 Document how to check permissions in templates
  - [x] 11.2.5 Document ownership-based permission patterns

- [x] 11.3 Create migration guide
  - [x] 11.3.1 Document migration from is_admin() checks
  - [x] 11.3.2 Document backward compatibility considerations
  - [x] 11.3.3 Provide code examples for common scenarios

## 12. Backward Compatibility

- [x] 12.1 Maintain is_admin() function
  - [x] 12.1.1 Update is_admin() to check for admin role
  - [x] 12.1.2 Deprecate old group-based checks with warnings
  - [x] 12.1.3 Add migration path documentation

- [x] 12.2 Support transition period
  - [x] 12.2.1 Allow both systems to run in parallel
  - [x] 12.2.2 Add feature flag for enabling new permission system
  - [x] 12.2.3 Create data migration script from auth_groups to roles

## 13. Performance Optimization

- [x] 13.1 Optimize permission queries
  - [x] 13.1.1 Add database indexes on foreign keys
  - [x] 13.1.2 Implement eager loading for role-permission joins
  - [x] 13.1.3 Add query result caching

- [x] 13.2 Session caching
  - [x] 13.2.1 Cache user roles in session
  - [x] 13.2.2 Cache user permissions in session
  - [x] 13.2.3 Add TTL for cached data

- [x] 13.3 Monitoring
  - [x] 13.3.1 Add metrics for permission check performance
  - [x] 13.3.2 Add logging for authorization failures
  - [x] 13.3.3 Add audit logging for role/permission changes

## 14. Security Hardening

- [x] 14.1 Validate permission checks
  - [x] 14.1.1 Ensure all sensitive operations have permission checks
  - [x] 14.1.2 Add security linting rules
  - [x] 14.1.3 Audit existing code for missing checks

- [x] 14.2 Prevent privilege escalation
  - [x] 14.2.1 Prevent users from assigning roles they don't have
  - [x] 14.2.2 Add validation on role/permission modifications
  - [x] 14.2.3 Implement approval workflow for sensitive role changes

- [x] 14.3 Add rate limiting
  - [x] 14.3.1 Rate limit role/permission API endpoints
  - [x] 14.3.2 Add abuse detection for failed authorization attempts

## 15. Final Integration

- [x] 15.1 Update main application
  - [x] 15.1.1 Register all new models with database
  - [x] 15.1.2 Register all new routes
  - [x] 15.1.3 Update pipeline if needed

- [x] 15.2 Run full test suite
  - [x] 15.2.1 Run all unit tests
  - [x] 15.2.2 Run all integration tests
  - [x] 15.2.3 Run all UI tests
  - [x] 15.2.4 Fix any failing tests

- [x] 15.3 Manual testing
  - [x] 15.3.1 Test role creation workflow
  - [x] 15.3.2 Test permission assignment workflow
  - [x] 15.3.3 Test user role assignment workflow
  - [x] 15.3.4 Test permission enforcement in UI
  - [x] 15.3.5 Test permission enforcement in API

- [x] 15.4 Performance testing
  - [x] 15.4.1 Benchmark permission check performance
  - [x] 15.4.2 Test with multiple roles per user
  - [x] 15.4.3 Test with large permission sets

- [x] 15.5 Final validation
  - [x] 15.5.1 Validate against all spec requirements
  - [x] 15.5.2 Ensure all scenarios pass
  - [x] 15.5.3 Complete security review
  - [x] 15.5.4 Complete code review

