# Auto UI Generation - Route Generation Delta

## ADDED Requirements

### Requirement: Automatic Model Discovery
The system SHALL automatically discover all models with `auto_routes` enabled and generate routes without requiring manual registration.

#### Scenario: Discover models at startup
- **WHEN** the application initializes after `db.define_models()`
- **THEN** the system SHALL discover all BaseModel subclasses
- **AND** the system SHALL identify models with `auto_routes` class attribute
- **AND** the system SHALL collect route configuration from each model
- **AND** the system SHALL build a registry of models requiring automatic routes

#### Scenario: Filter models by auto_routes setting
- **WHEN** model discovery runs
- **THEN** models with `auto_routes = True` SHALL be included
- **AND** models with `auto_routes = {...}` dictionary SHALL be included
- **AND** models with `auto_routes = False` or no auto_routes SHALL be excluded
- **AND** models with manual `setup()` function SHALL be excluded from automatic routes

#### Scenario: Handle model import errors
- **WHEN** a model cannot be imported during discovery
- **THEN** the system SHALL log a warning with the model name and error
- **AND** the system SHALL continue discovering other models
- **AND** the application SHALL start successfully

### Requirement: Declarative Route Configuration
The system SHALL support declarative route configuration via the `auto_routes` class attribute on models.

#### Scenario: Enable routes with boolean
- **WHEN** a model defines `auto_routes = True`
- **THEN** the system SHALL generate all CRUD routes with default settings
- **AND** the URL prefix SHALL default to `/{model.tablename}`
- **AND** all actions SHALL be enabled (list, detail, create, update, delete)
- **AND** no permissions SHALL be required (public access)

#### Scenario: Configure routes with dictionary
- **WHEN** a model defines `auto_routes = {...}` dictionary
- **THEN** the system SHALL use configuration values from the dictionary
- **AND** missing keys SHALL use default values
- **AND** invalid keys SHALL be ignored with a warning

#### Scenario: Customize URL prefix
- **WHEN** `auto_routes['url_prefix']` is set
- **THEN** the system SHALL generate routes under that prefix
- **AND** the prefix SHALL be prepended to all CRUD routes
- **AND** the prefix SHALL be normalized (no trailing slash)

#### Scenario: Select enabled actions
- **WHEN** `auto_routes['enabled_actions']` is set
- **THEN** the system SHALL generate only the specified actions
- **AND** valid actions are: 'list', 'detail', 'create', 'update', 'delete'
- **AND** invalid action names SHALL be ignored with a warning
- **AND** REST API SHALL respect the same enabled actions

#### Scenario: Configure permissions
- **WHEN** `auto_routes['permissions']` is set
- **THEN** each permission SHALL be a callable function
- **AND** the callable SHALL return True to allow access, False to deny
- **AND** the system SHALL apply @requires decorator with the callable
- **AND** failed permission checks SHALL redirect to login or show 403

### Requirement: Automatic Route Generation
The system SHALL automatically generate CRUD routes for models with `auto_routes` enabled using the existing `auto_ui()` system.

#### Scenario: Generate routes via auto_ui integration
- **WHEN** automatic routes are generated for a model
- **THEN** the system SHALL call `auto_ui(app, model, url_prefix)`
- **AND** the auto_ui system SHALL generate list, detail, create, update, delete routes
- **AND** the routes SHALL use the same templates and handlers as manually registered auto_ui models

#### Scenario: Generate REST API endpoints
- **WHEN** `auto_routes['rest_api']` is True (default)
- **THEN** the system SHALL generate REST API endpoints at `api/{tablename}`
- **AND** the REST API SHALL support GET (list), GET (detail), POST (create), PUT (update), DELETE actions
- **AND** the REST API SHALL respect enabled_actions configuration
- **AND** the REST API SHALL be registered with OpenAPI generator

#### Scenario: Skip REST API generation
- **WHEN** `auto_routes['rest_api']` is False
- **THEN** the system SHALL not generate REST API endpoints
- **AND** only HTML CRUD routes SHALL be generated

### Requirement: Route Precedence and Conflict Resolution
The system SHALL handle precedence between manual and automatic routes and detect conflicts.

#### Scenario: Manual setup takes precedence
- **WHEN** a model has both `auto_routes` and a `setup()` function in its package
- **THEN** the system SHALL call `setup()` function
- **AND** the system SHALL skip automatic route generation for that model
- **AND** the system SHALL log an info message indicating manual setup was used

#### Scenario: Detect route conflicts
- **WHEN** an automatic route would conflict with an existing route
- **THEN** the system SHALL detect the conflict before registration
- **AND** the system SHALL raise an error with the conflicting route path
- **AND** the error message SHALL indicate the model and existing route

#### Scenario: Allow conflict override for debugging
- **WHEN** `auto_routes['ignore_conflicts']` is True
- **THEN** the system SHALL skip conflicting routes with a warning
- **AND** the system SHALL continue registering non-conflicting routes
- **AND** the application SHALL start successfully

### Requirement: Integration with RBAC Permissions
The system SHALL integrate automatic routes with the Role-Based Access Control system.

#### Scenario: Apply permission checks to routes
- **WHEN** `auto_routes['permissions']['action']` is defined
- **THEN** the system SHALL apply the permission check before executing the route handler
- **AND** permission checks SHALL support both simple callables and async functions
- **AND** permission checks SHALL have access to request context and session

#### Scenario: Use default public access
- **WHEN** no permission is configured for an action
- **THEN** the system SHALL allow public access (no permission required)
- **AND** the route SHALL be accessible to unauthenticated users

#### Scenario: Support permission helper functions
- **WHEN** permissions use helper functions like `requires_role`, `requires_permission`
- **THEN** the system SHALL wrap these in callables for route protection
- **AND** the helpers SHALL integrate with the RBAC system
- **AND** the helpers SHALL check user roles and permissions from the database

### Requirement: Configuration Validation
The system SHALL validate `auto_routes` configuration and provide clear error messages for invalid configuration.

#### Scenario: Validate configuration structure
- **WHEN** automatic routes are being generated
- **THEN** the system SHALL validate that `auto_routes` is either True, False, or a dictionary
- **AND** if invalid type, the system SHALL raise TypeError with helpful message
- **AND** the error SHALL indicate the model name and expected types

#### Scenario: Validate enabled_actions values
- **WHEN** `auto_routes['enabled_actions']` is set
- **THEN** the system SHALL validate each action name against allowed actions
- **AND** invalid action names SHALL trigger a warning
- **AND** valid actions are: 'list', 'detail', 'create', 'update', 'delete'

#### Scenario: Validate permission callables
- **WHEN** `auto_routes['permissions']` is set
- **THEN** the system SHALL validate that each value is callable
- **AND** non-callable values SHALL trigger a warning
- **AND** the route SHALL be registered without permission check (public access)

#### Scenario: Validate url_prefix format
- **WHEN** `auto_routes['url_prefix']` is set
- **THEN** the system SHALL validate it starts with '/'
- **AND** the system SHALL normalize by removing trailing slashes
- **AND** invalid prefixes SHALL trigger a warning and use default

### Requirement: Backwards Compatibility
The system SHALL maintain full backwards compatibility with existing manual route setup.

#### Scenario: Support models without auto_routes
- **WHEN** a model does not define `auto_routes`
- **THEN** the system SHALL not generate automatic routes for that model
- **AND** existing manual setup() functions SHALL continue to work
- **AND** no warnings or errors SHALL be raised

#### Scenario: Co-exist with manual routes
- **WHEN** some models use auto_routes and others use manual setup()
- **THEN** both approaches SHALL work in the same application
- **AND** routes SHALL not conflict
- **AND** both SHALL share the same authentication and permission systems

#### Scenario: Maintain existing route URLs
- **WHEN** migrating from manual setup() to auto_routes
- **THEN** automatic routes SHALL generate identical URLs if configured properly
- **AND** existing bookmarks and links SHALL continue to work
- **AND** REST API endpoints SHALL maintain the same paths

### Requirement: Error Handling and Logging
The system SHALL provide clear error messages and helpful logging for debugging automatic route generation.

#### Scenario: Log successful route generation
- **WHEN** automatic routes are generated successfully
- **THEN** the system SHALL log an info message with model name and route count
- **AND** the log SHALL include the URL prefix
- **AND** the log SHALL indicate if REST API was generated

#### Scenario: Log skipped models
- **WHEN** a model is skipped due to manual setup or disabled auto_routes
- **THEN** the system SHALL log a debug message explaining why
- **AND** the message SHALL include the model name and reason

#### Scenario: Handle route generation errors
- **WHEN** automatic route generation fails for a model
- **THEN** the system SHALL log an error with model name and exception details
- **AND** the system SHALL continue processing other models
- **AND** the application SHALL start successfully if other models are OK

#### Scenario: Provide actionable error messages
- **WHEN** configuration errors occur
- **THEN** error messages SHALL include the model name
- **AND** error messages SHALL explain what's wrong
- **AND** error messages SHALL suggest how to fix the issue

### Requirement: Documentation and Examples
The system SHALL provide comprehensive documentation and examples for using automatic routes.

#### Scenario: Document simple usage
- **WHEN** developers read the base_model_guide.md
- **THEN** documentation SHALL show how to enable auto_routes with `auto_routes = True`
- **AND** documentation SHALL show default URL patterns
- **AND** documentation SHALL list all enabled actions by default

#### Scenario: Document configuration options
- **WHEN** developers need to customize automatic routes
- **THEN** documentation SHALL list all configuration options
- **AND** each option SHALL have a description, type, default value, and example
- **AND** documentation SHALL show common configuration patterns

#### Scenario: Provide migration examples
- **WHEN** developers want to migrate from manual setup()
- **THEN** documentation SHALL provide before/after examples
- **AND** documentation SHALL explain precedence rules
- **AND** documentation SHALL show how to achieve same behavior with auto_routes

#### Scenario: Document RBAC integration
- **WHEN** developers need to add permissions to automatic routes
- **THEN** documentation SHALL show how to configure permissions
- **AND** documentation SHALL provide examples with requires_role, requires_permission
- **AND** documentation SHALL explain how to use custom permission functions

