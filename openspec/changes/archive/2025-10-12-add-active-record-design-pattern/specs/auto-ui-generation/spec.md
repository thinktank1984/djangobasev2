# Auto-UI Generation Specification - Active Record Integration

## MODIFIED Requirements

### Requirement: Form Generation from Models
The system SHALL generate HTML forms automatically from model definitions using Active Record introspection.

**Previous requirement used ad-hoc model inspection. Now using standardized Active Record API for reliability and consistency.**

#### Scenario: Generate form from Active Record model
- **WHEN** calling `generate_form(Post)` on an Active Record model
- **THEN** use `Post.get_attributes()` to extract field definitions
- **AND** use `Post.get_ui_overrides()` to apply custom widgets
- **AND** use `Post.get_validators()` to add client-side validation

#### Scenario: Apply UI overrides to form fields
- **WHEN** a model specifies `@ui_override(field='content', widget='rich_text_editor')`
- **THEN** the generated form uses a rich text editor for the content field
- **AND** widget configuration from the decorator is passed to the UI component

#### Scenario: Apply validators to form fields
- **WHEN** a model specifies `@validates('title')` with minimum length check
- **THEN** the generated form includes HTML5 validation attributes
- **AND** displays custom validation messages defined in the decorator

---

### Requirement: Widget Selection
The system SHALL select appropriate UI widgets based on field types and explicit overrides from Active Record decorators.

**Previous requirement only used field types. Now also respecting explicit UI override decorators.**

#### Scenario: Default widget by field type
- **WHEN** a model has a `Field.text()` attribute without UI override
- **THEN** generate a `<textarea>` element with appropriate default size
- **AND** use standard text input for `Field.string()` attributes

#### Scenario: Override widget with decorator
- **WHEN** a model specifies `@ui_override(field='published_at', widget='date_picker')`
- **THEN** use the date picker widget instead of a plain text input
- **AND** pass any widget configuration options from the decorator

#### Scenario: Computed fields excluded from forms
- **WHEN** a model has a `@computed_field` decorator on a property
- **THEN** exclude that field from edit forms
- **AND** optionally display it as read-only in view templates

---

### Requirement: Form Validation Integration
The system SHALL integrate model validators into generated forms for both client-side and server-side validation.

**Previous requirement only handled server-side validation. Now supporting both client and server validation from the same decorator.**

#### Scenario: Client-side validation from decorator
- **WHEN** a model uses `@validates('email')` with email format check
- **THEN** add `type="email"` attribute to the form field
- **AND** add HTML5 pattern attribute if custom regex is provided

#### Scenario: Server-side validation on submit
- **WHEN** a generated form is submitted
- **THEN** model validators are executed via Active Record validation API
- **AND** validation errors are displayed next to the corresponding form fields

#### Scenario: Custom validation messages
- **WHEN** a validator decorator returns a custom error message
- **THEN** display that message in the form instead of a generic error
- **AND** maintain consistent error message formatting across all fields

---

## ADDED Requirements

### Requirement: Active Record Introspection API
The auto-UI generator MUST use standardized Active Record introspection methods instead of direct attribute inspection.

#### Scenario: Use introspection API
- **WHEN** generating UI for a model
- **THEN** call `Model.get_attributes()` instead of inspecting `__dict__`
- **AND** call `Model.get_ui_overrides()` instead of searching for decorated methods
- **AND** call `Model.get_validators()` instead of looking for validation logic

#### Scenario: Graceful fallback for non-Active Record models
- **WHEN** a model does not inherit from ActiveRecord
- **THEN** fall back to legacy introspection methods
- **AND** log a warning suggesting migration to Active Record pattern

#### Scenario: Cache introspection results
- **WHEN** introspecting a model for UI generation
- **THEN** cache the results for the model class
- **AND** invalidate cache only when the class definition changes

---

### Requirement: UI Override Configuration
The auto-UI generator MUST support rich widget configuration from UI override decorators.

#### Scenario: Widget with configuration options
- **WHEN** a `@ui_override` decorator returns a dictionary of options
- **THEN** pass those options to the widget renderer
- **AND** merge with default widget options (decorator options take precedence)

#### Scenario: Dynamic widget configuration
- **WHEN** a `@ui_override` decorator is a method that accepts the model instance
- **THEN** call the method with the instance during form generation
- **AND** use the returned configuration for that specific form instance

#### Scenario: Conditional field visibility
- **WHEN** a model defines field visibility rules via decorators
- **THEN** respect those rules when generating forms
- **AND** exclude invisible fields from the generated HTML

---

### Requirement: Documentation of UI Overrides
The auto-UI generator MUST provide documentation of available widgets and how to override them.

#### Scenario: List available widgets
- **WHEN** running `python auto_ui_generator.py --list-widgets`
- **THEN** display all available widget types with descriptions
- **AND** show example code for common override scenarios

#### Scenario: Generate widget reference
- **WHEN** running `python auto_ui_generator.py --widget-docs`
- **THEN** generate HTML documentation of all widgets
- **AND** include configuration options and examples for each widget

#### Scenario: Validate UI overrides
- **WHEN** a model specifies an unknown widget type
- **THEN** raise a clear error during UI generation
- **AND** suggest valid widget types as alternatives

---

## Integration Examples

### Example 1: Rich Text Editor Override

```python
class Post(Model, ActiveRecord):
    title = Field.string()
    content = Field.text()
    
    @ui_override(field='content', widget='rich_text_editor')
    def content_widget(self):
        return {
            'toolbar': ['bold', 'italic', 'link', 'image'],
            'height': '400px'
        }
```

Generated form includes:
- TinyMCE or similar rich text editor for `content` field
- Standard text input for `title` field
- Configured toolbar with specified options

### Example 2: Date Picker with Validation

```python
class Event(Model, ActiveRecord):
    start_date = Field.datetime()
    end_date = Field.datetime()
    
    @ui_override(field='start_date', widget='date_picker')
    def start_date_widget(self):
        return {'format': 'YYYY-MM-DD', 'min_date': 'today'}
    
    @validates('end_date')
    def validate_end_date(self, value):
        if value < self.start_date:
            return "End date must be after start date"
```

Generated form includes:
- Date picker widget for both date fields
- Client-side validation preventing past dates for start_date
- Server-side validation ensuring end_date > start_date
- Clear error messages for validation failures

### Example 3: Conditional Widget Configuration

```python
class Product(Model, ActiveRecord):
    name = Field.string()
    price = Field.decimal()
    is_featured = Field.bool()
    
    @ui_override(field='price', widget='currency_input')
    def price_widget(self):
        if self.is_featured:
            return {'warning': 'Featured product - price changes are public'}
        return {}
```

Generated form includes:
- Currency input with proper formatting for price field
- Conditional warning message if product is featured
- Dynamic widget configuration based on model state

