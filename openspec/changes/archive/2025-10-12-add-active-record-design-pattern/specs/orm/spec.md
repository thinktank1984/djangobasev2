# ORM Specification - Active Record Design Pattern

## ADDED Requirements

### Requirement: Active Record Base Class
The system SHALL provide an `ActiveRecord` base class or mixin that enforces clean model architecture and provides introspection capabilities.

#### Scenario: Model inherits from ActiveRecord
- **WHEN** a model class inherits from `ActiveRecord`
- **THEN** the model gains introspection methods: `get_attributes()`, `get_methods()`, `get_ui_overrides()`, `get_validators()`
- **AND** the model can be validated for anti-patterns

#### Scenario: Introspect model attributes
- **WHEN** calling `Model.get_attributes()` on an ActiveRecord model
- **THEN** return a dictionary of all field definitions with their types and constraints
- **AND** exclude methods and computed fields from the attributes list

#### Scenario: Introspect model methods
- **WHEN** calling `Model.get_methods()` on an ActiveRecord model
- **THEN** return a list of all business logic methods (excluding private and infrastructure methods)
- **AND** include method signatures and decorators

---

### Requirement: Model Structure Enforcement
The system SHALL enforce a clear structure for Active Record models with distinct sections for attributes, decorators, and methods.

#### Scenario: Model with proper structure
- **WHEN** a model defines attributes at the top, decorators in the middle, and methods at the bottom
- **THEN** pattern validation passes without warnings
- **AND** introspection returns organized metadata

#### Scenario: Detect anti-patterns in models
- **WHEN** a model contains HTTP request handling, template rendering, or external API calls
- **THEN** pattern validation fails with specific error messages
- **AND** the system suggests how to refactor the code

#### Scenario: Validate model on save
- **WHEN** an ActiveRecord model is instantiated or modified
- **THEN** all attribute validators are executed automatically
- **AND** validation errors prevent saving with clear error messages

---

### Requirement: Attribute Decorators
The system SHALL provide decorators for extending attribute behavior including validation, computation, and formatting.

#### Scenario: Validate attribute with decorator
- **WHEN** a model uses `@validates('field_name')` decorator
- **THEN** the decorated function is called before saving the model
- **AND** validation errors are collected and returned as a dictionary

#### Scenario: Define computed field
- **WHEN** a model uses `@computed_field` decorator on a method
- **THEN** the method acts as a read-only property derived from other attributes
- **AND** the computed field is excluded from database saves

#### Scenario: Format attribute value
- **WHEN** a model uses `@format('field_name')` decorator
- **THEN** the decorated function transforms the field value before saving
- **AND** formatting is applied consistently across all save operations

---

### Requirement: UI Element Mapping Decorators
The system SHALL provide decorators for specifying default UI widget overrides for automatic UI generation.

#### Scenario: Override field widget
- **WHEN** a model uses `@ui_override(field='content', widget='rich_text_editor')` decorator
- **THEN** the auto-UI generator uses the specified widget instead of the default
- **AND** the decorator can return widget configuration options

#### Scenario: Multiple UI overrides
- **WHEN** a model has multiple `@ui_override` decorators for different fields
- **THEN** each field's widget is customized independently
- **AND** fields without overrides use default widgets based on their type

#### Scenario: Conditional UI override
- **WHEN** a `@ui_override` decorator returns configuration based on model state
- **THEN** the UI generator applies the appropriate configuration dynamically
- **AND** the model instance is passed to the decorator function

---

### Requirement: Method Decorators
The system SHALL provide decorators for extending method behavior including authorization, caching, and lifecycle hooks.

#### Scenario: Require permission for method
- **WHEN** a model method uses `@requires_permission('admin')` decorator
- **THEN** the method checks current user permissions before execution
- **AND** unauthorized access raises a 403 Forbidden error

#### Scenario: Cache method result
- **WHEN** a model method uses `@cached(ttl=300)` decorator
- **THEN** the method result is cached for 300 seconds
- **AND** subsequent calls within TTL return cached result without execution

#### Scenario: Lifecycle hook
- **WHEN** a model method uses `@before_save` or `@after_save` decorator
- **THEN** the method is automatically called at the appropriate time
- **AND** lifecycle hooks can modify the model or perform side effects

---

### Requirement: Model Validation CLI
The system SHALL provide a command-line tool to validate all models against the Active Record pattern.

#### Scenario: Validate all models
- **WHEN** running `python validate_models.py --all`
- **THEN** all model classes are checked for anti-patterns and structural issues
- **AND** violations are reported with file locations and suggestions

#### Scenario: JSON output for CI/CD
- **WHEN** running `python validate_models.py --json`
- **THEN** validation results are output as structured JSON
- **AND** the exit code is non-zero if any violations are found

#### Scenario: Auto-fix suggestions
- **WHEN** validation detects common anti-patterns
- **THEN** the tool suggests specific refactoring actions
- **AND** provides code snippets for the recommended changes

---

## MODIFIED Requirements

### Requirement: Model Definition
Models MUST inherit from Emmett's `Model` class and SHOULD inherit from `ActiveRecord` for standardized structure and introspection.

**Previous requirement focused only on basic Emmett Model inheritance. Now emphasizing Active Record pattern as the preferred approach.**

#### Scenario: Define model with Active Record
- **WHEN** creating a new model class
- **THEN** inherit from both `Model` and `ActiveRecord`: `class Post(Model, ActiveRecord)`
- **AND** organize class content following the Active Record structure

#### Scenario: Legacy model without Active Record
- **WHEN** using an existing model that only inherits from `Model`
- **THEN** the model still functions correctly
- **AND** a deprecation warning suggests migrating to Active Record pattern

---

### Requirement: Model Organization
Models MUST organize their code into distinct sections: attributes, attribute decorators, UI overrides, methods, and method decorators.

**Previous requirement had no specific organization guidance. Now enforcing clear structure.**

#### Scenario: Well-organized model
- **WHEN** a model follows the recommended section order
- **THEN** the structure is: 1) attributes, 2) attribute decorators, 3) UI overrides, 4) business methods, 5) method decorators
- **AND** introspection tools can reliably extract metadata

#### Scenario: Disorganized model
- **WHEN** a model mixes concerns or has unclear organization
- **THEN** pattern validation issues warnings
- **AND** suggests reorganizing into the standard structure

---

## Anti-Pattern Guidelines

### Models MUST NOT Contain

1. **HTTP Request Handling**
   - Don't accept `request` objects as parameters
   - Don't call HTTP client libraries
   - Don't handle routing or URL generation

2. **Template Rendering**
   - Don't call template engines
   - Don't return HTML strings
   - Don't contain presentation logic

3. **External Service Integration**
   - Don't make API calls to external services
   - Don't send emails directly
   - Don't enqueue background jobs

4. **UI Logic**
   - Don't contain JavaScript or CSS
   - Don't build HTML elements
   - Don't handle form submissions

### Models SHOULD Contain

1. **Domain Logic**
   - Business rules and calculations
   - State transitions and workflows
   - Data validation and constraints

2. **Data Access Patterns**
   - Query scopes and filters
   - Relationship traversal helpers
   - Aggregation methods

3. **Model Lifecycle**
   - Before/after save hooks
   - Computed fields
   - Default value logic

---

## Migration Strategy

### Existing Models
- Models not using ActiveRecord continue to work
- Gradual migration recommended
- Pattern validation is opt-in initially

### New Models
- All new models SHOULD use ActiveRecord pattern
- Code reviews enforce pattern compliance
- Examples and templates provided

### Tooling Support
- Linters detect anti-patterns
- Auto-formatter can organize sections
- Migration script available for bulk updates

