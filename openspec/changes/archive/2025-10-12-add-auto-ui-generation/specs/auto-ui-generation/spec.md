# Auto UI Generation Specification

## ADDED Requirements

### Requirement: UI Mapping Configuration
The system SHALL provide a JSON-based configuration file that maps model field types to UI components with customizable attributes and display formatters.

#### Scenario: Load default UI mappings
- **WHEN** the auto UI generator is initialized
- **THEN** the system SHALL load `runtime/ui_mapping.json` as the default mapping configuration
- **AND** the JSON SHALL define mappings for standard field types (string, text, int, bool, datetime, date, belongs_to)
- **AND** each mapping SHALL specify the HTML component type (input, textarea, select, checkbox)
- **AND** each mapping SHALL specify HTML attributes (type, class, rows, etc.)

#### Scenario: Support custom UI mapping overrides
- **WHEN** a file exists at `runtime/ui_mapping_custom.json`
- **THEN** the system SHALL load and merge it with the default mappings
- **AND** custom mappings SHALL override default mappings for matching field types
- **AND** new field types defined in custom file SHALL be added to available mappings

#### Scenario: Resolve field type to UI component
- **WHEN** generating a form field for a model attribute
- **THEN** the system SHALL look up the field type in the UI mappings
- **AND** the system SHALL use the mapped component and attributes
- **AND** if no mapping exists for the field type, the system SHALL default to text input

#### Scenario: Apply display formatters
- **WHEN** rendering a field value in detail or list view
- **THEN** the system SHALL check for a display formatter in `display_formatters` section
- **AND** if a formatter is defined, the system SHALL apply it to format the value
- **AND** formatters SHALL handle datetime, date, boolean, and relationship formatting

#### Scenario: Customize CSS classes via mapping
- **WHEN** the UI mapping specifies CSS classes in attributes
- **THEN** the generated HTML SHALL include those classes
- **AND** this SHALL allow consistent Tailwind CSS styling across all fields
- **AND** custom mappings SHALL be able to override default CSS classes

#### Scenario: Handle invalid UI mapping JSON
- **WHEN** the ui_mapping.json file is malformed or missing
- **THEN** the system SHALL fall back to hardcoded default mappings
- **AND** the system SHALL log a warning about the invalid configuration
- **AND** the application SHALL continue to function with default behavior

### Requirement: Model Introspection
The system SHALL introspect Emmett ORM models to extract field definitions, relationships, validation rules, and configuration metadata needed for automatic UI generation.

#### Scenario: Extract basic field information
- **WHEN** a model is registered for auto UI generation
- **THEN** the system SHALL identify all fields defined on the model
- **AND** the system SHALL determine each field's type (string, text, integer, datetime, boolean, etc.)
- **AND** the system SHALL extract field validation rules from the model's `validation` dictionary
- **AND** the system SHALL identify default values from the model's `default_values` dictionary

#### Scenario: Extract relationship information
- **WHEN** a model has relationship fields (belongs_to, has_many, has_one)
- **THEN** the system SHALL identify the related model
- **AND** the system SHALL determine the relationship type
- **AND** the system SHALL prepare appropriate widgets (select dropdowns for belongs_to)

#### Scenario: Extract auto UI configuration
- **WHEN** a model defines an `auto_ui_config` dictionary
- **THEN** the system SHALL merge this configuration with default settings
- **AND** the system SHALL use custom display names, permissions, and field configurations

### Requirement: Route Generation
The system SHALL automatically generate and register CRUD routes for models with appropriate URL patterns, HTTP methods, and route handlers.

#### Scenario: Generate list view route
- **WHEN** auto UI is enabled for a model
- **THEN** the system SHALL register a GET route at `{url_prefix}/` that displays paginated list of records
- **AND** the route SHALL support query parameters for pagination (`page`, `per_page`)
- **AND** the route SHALL support query parameters for search (`q`)
- **AND** the route SHALL support query parameters for filtering (`filter_field`, `filter_value`)
- **AND** the route SHALL support query parameters for sorting (`sort`)

#### Scenario: Generate create routes
- **WHEN** auto UI is enabled for a model
- **THEN** the system SHALL register a GET route at `{url_prefix}/new` that displays the create form
- **AND** the system SHALL register a POST route at `{url_prefix}/` that processes form submission
- **AND** on successful creation, the system SHALL redirect to the detail view of the new record
- **AND** on validation failure, the system SHALL re-render the form with error messages

#### Scenario: Generate detail view route
- **WHEN** auto UI is enabled for a model
- **THEN** the system SHALL register a GET route at `{url_prefix}/<int:id>` that displays a single record's details
- **AND** if the record does not exist, the system SHALL return a 404 error

#### Scenario: Generate update routes
- **WHEN** auto UI is enabled for a model
- **THEN** the system SHALL register a GET route at `{url_prefix}/<int:id>/edit` that displays the edit form
- **AND** the system SHALL register a POST route at `{url_prefix}/<int:id>` that processes form submission
- **AND** on successful update, the system SHALL redirect to the detail view
- **AND** on validation failure, the system SHALL re-render the form with error messages

#### Scenario: Generate delete routes
- **WHEN** auto UI is enabled for a model
- **THEN** the system SHALL register a GET route at `{url_prefix}/<int:id>/delete` that displays delete confirmation
- **AND** the system SHALL register a POST route at `{url_prefix}/<int:id>/delete` that performs deletion
- **AND** on successful deletion, the system SHALL redirect to the list view
- **AND** the system SHALL display a success message after deletion

### Requirement: Form Generation
The system SHALL automatically generate forms from models with appropriate widgets, labels, validation, and styling.

#### Scenario: Generate form with appropriate widgets
- **WHEN** a form is generated for a model
- **THEN** `Field()` SHALL render as `<input type="text">`
- **AND** `Field.text()` SHALL render as `<textarea>`
- **AND** `Field.bool()` SHALL render as `<input type="checkbox">`
- **AND** `Field.int()` SHALL render as `<input type="number">`
- **AND** `Field.datetime()` SHALL render as `<input type="datetime-local">`
- **AND** `Field.date()` SHALL render as `<input type="date">`
- **AND** `Field.belongs_to()` SHALL render as `<select>` with options from related model

#### Scenario: Apply custom field configuration
- **WHEN** a field has custom configuration in `auto_ui_config.field_config`
- **THEN** the system SHALL use the custom display name
- **AND** the system SHALL use the custom widget type if specified
- **AND** the system SHALL apply readonly attribute if configured
- **AND** the system SHALL hide the field if configured as hidden

#### Scenario: Display validation errors
- **WHEN** form validation fails
- **THEN** the system SHALL display error messages next to the relevant fields
- **AND** the system SHALL preserve user input in the form fields
- **AND** the system SHALL highlight fields with errors using CSS classes

#### Scenario: Handle form submission
- **WHEN** a form is submitted successfully
- **THEN** the system SHALL save the record to the database
- **AND** the system SHALL apply default values from `default_values`
- **AND** the system SHALL set relationships appropriately
- **AND** the system SHALL run all model validation rules

### Requirement: Template Generation
The system SHALL provide default templates for CRUD views that are responsive, accessible, and styled with Tailwind CSS.

#### Scenario: Render list view template
- **WHEN** the list view is displayed
- **THEN** the template SHALL show a table with configured columns
- **AND** the template SHALL show pagination controls if records exceed page size
- **AND** the template SHALL show a search box if search fields are configured
- **AND** the template SHALL show filter controls if filters are configured
- **AND** the template SHALL include action links (view, edit, delete) for each record
- **AND** the template SHALL include a "Create New" button linking to the create form

#### Scenario: Render detail view template
- **WHEN** the detail view is displayed
- **THEN** the template SHALL show all readable fields with their labels and values
- **AND** the template SHALL format values appropriately (dates, booleans, relationships)
- **AND** the template SHALL include action buttons (Edit, Delete, Back to List)
- **AND** the template SHALL show related records if relationships exist

#### Scenario: Render form template
- **WHEN** a create or edit form is displayed
- **THEN** the template SHALL show form fields with appropriate labels
- **AND** the template SHALL include validation error messages
- **AND** the template SHALL include a submit button
- **AND** the template SHALL include a cancel button linking back to the list
- **AND** the template SHALL apply Tailwind CSS styling for professional appearance

#### Scenario: Render delete confirmation template
- **WHEN** the delete confirmation is displayed
- **THEN** the template SHALL show the record's identifying information
- **AND** the template SHALL include a warning message
- **AND** the template SHALL include a "Confirm Delete" button
- **AND** the template SHALL include a "Cancel" button linking back to the detail view

#### Scenario: Support custom template overrides
- **WHEN** a custom template exists at `templates/auto_ui_custom/{model_name}/{template}.html`
- **THEN** the system SHALL use the custom template instead of the default
- **AND** the system SHALL provide the same context variables to the custom template

### Requirement: Permission Integration
The system SHALL integrate with Emmett's Auth module to enforce permissions for all CRUD operations.

#### Scenario: Check list permission
- **WHEN** a user attempts to access the list view
- **THEN** the system SHALL check the `list` permission from `auto_ui_config.permissions`
- **AND** if permission is denied, the system SHALL redirect to login or show 403 error
- **AND** if no permission is configured, the system SHALL allow access by default

#### Scenario: Check create permission
- **WHEN** a user attempts to access the create form or submit create action
- **THEN** the system SHALL check the `create` permission
- **AND** if permission is denied, the system SHALL redirect to login or show 403 error

#### Scenario: Check update permission
- **WHEN** a user attempts to access the edit form or submit update action
- **THEN** the system SHALL check the `update` permission
- **AND** if permission is denied, the system SHALL redirect to login or show 403 error

#### Scenario: Check delete permission
- **WHEN** a user attempts to access the delete confirmation or submit delete action
- **THEN** the system SHALL check the `delete` permission
- **AND** if permission is denied, the system SHALL redirect to login or show 403 error

#### Scenario: Check detail permission
- **WHEN** a user attempts to access the detail view
- **THEN** the system SHALL check the `read` permission from `auto_ui_config.permissions`
- **AND** if permission is denied, the system SHALL redirect to login or show 403 error

### Requirement: Pagination
The system SHALL provide pagination for list views to handle large datasets efficiently.

#### Scenario: Paginate list results
- **WHEN** the list view is accessed
- **THEN** the system SHALL limit results to the configured page size (default 25)
- **AND** the system SHALL display page navigation controls
- **AND** the system SHALL support `?page=N` query parameter for navigation

#### Scenario: Display pagination metadata
- **WHEN** pagination is active
- **THEN** the template SHALL show current page number
- **AND** the template SHALL show total number of pages
- **AND** the template SHALL show total number of records
- **AND** the template SHALL show record range for current page (e.g., "Showing 1-25 of 100")

#### Scenario: Navigate between pages
- **WHEN** a user clicks a page navigation link
- **THEN** the system SHALL preserve search and filter parameters
- **AND** the system SHALL load the requested page
- **AND** the system SHALL highlight the current page in navigation

### Requirement: Search Functionality
The system SHALL provide search functionality for list views based on configured search fields.

#### Scenario: Perform text search
- **WHEN** a user submits a search query
- **THEN** the system SHALL search configured `search_fields` for matches
- **AND** the system SHALL use case-insensitive matching
- **AND** the system SHALL use OR logic across multiple search fields
- **AND** the system SHALL display only matching records

#### Scenario: Preserve search in pagination
- **WHEN** search results are paginated
- **THEN** the system SHALL preserve the search query across page navigation
- **AND** the system SHALL show search query in the search box

#### Scenario: Clear search
- **WHEN** a user clears the search box and submits
- **THEN** the system SHALL display all records (subject to pagination)

### Requirement: Filtering
The system SHALL provide filtering capabilities for list views based on field values.

#### Scenario: Filter by field value
- **WHEN** filtering is configured for a field
- **THEN** the list view SHALL show a filter control for that field
- **AND** the system SHALL display only records matching the filter value

#### Scenario: Combine multiple filters
- **WHEN** multiple filters are applied
- **THEN** the system SHALL use AND logic to combine filters
- **AND** the system SHALL display only records matching all filters

#### Scenario: Preserve filters in pagination
- **WHEN** filtered results are paginated
- **THEN** the system SHALL preserve filter values across page navigation

### Requirement: Sorting
The system SHALL provide sorting capabilities for list views based on column headers.

#### Scenario: Sort by column
- **WHEN** a user clicks a sortable column header
- **THEN** the system SHALL sort records by that column in ascending order
- **AND** clicking again SHALL sort in descending order
- **AND** the template SHALL indicate sort direction with visual indicator

#### Scenario: Default sorting
- **WHEN** no sort parameter is provided
- **THEN** the system SHALL use `sort_default` from `auto_ui_config` if configured
- **AND** otherwise SHALL use the model's primary key

#### Scenario: Preserve sorting in pagination
- **WHEN** sorted results are paginated
- **THEN** the system SHALL preserve the sort parameter across page navigation

### Requirement: Responsive Design
The system SHALL generate UIs that are responsive and work on mobile, tablet, and desktop devices.

#### Scenario: Adapt list view for mobile
- **WHEN** the list view is displayed on a mobile device
- **THEN** the table SHALL transform to a card-based layout
- **OR** the table SHALL allow horizontal scrolling
- **AND** action buttons SHALL remain accessible

#### Scenario: Adapt forms for mobile
- **WHEN** forms are displayed on a mobile device
- **THEN** form fields SHALL stack vertically
- **AND** inputs SHALL be appropriately sized for touch interaction
- **AND** the submit button SHALL be easily tappable

### Requirement: Accessibility
The system SHALL generate UIs that are accessible to users with disabilities.

#### Scenario: Provide semantic HTML
- **WHEN** templates are rendered
- **THEN** the system SHALL use semantic HTML elements (table, form, button, nav)
- **AND** the system SHALL use appropriate heading hierarchy

#### Scenario: Provide ARIA labels
- **WHEN** interactive elements are rendered
- **THEN** the system SHALL include ARIA labels where appropriate
- **AND** the system SHALL mark required fields with `aria-required="true"`
- **AND** the system SHALL associate error messages with fields using `aria-describedby`

#### Scenario: Support keyboard navigation
- **WHEN** a user navigates with keyboard
- **THEN** all interactive elements SHALL be reachable with Tab key
- **AND** forms SHALL be submittable with Enter key
- **AND** focus indicators SHALL be clearly visible

### Requirement: Relationship Handling
The system SHALL properly handle and display model relationships in forms and views.

#### Scenario: Display belongs_to relationship in form
- **WHEN** a field is a belongs_to relationship
- **THEN** the form SHALL show a select dropdown
- **AND** the dropdown SHALL include all records from the related model
- **AND** the dropdown SHALL display the related model's primary display field

#### Scenario: Display belongs_to relationship in detail view
- **WHEN** viewing a record with a belongs_to relationship
- **THEN** the detail view SHALL show the related record's display name
- **AND** the display name SHALL be a link to the related record's detail view (if accessible)

#### Scenario: Display has_many relationships in detail view
- **WHEN** viewing a record with has_many relationships
- **THEN** the detail view SHALL show a list of related records
- **AND** each related record SHALL link to its detail view (if accessible)
- **AND** the list SHALL show a limited number of related records with "View All" link

### Requirement: Customization API
The system SHALL provide a configuration API for customizing the auto-generated UI without writing custom templates.

#### Scenario: Configure display names
- **WHEN** `auto_ui_config.display_name` is set
- **THEN** the system SHALL use this name in page titles and breadcrumbs
- **AND** when `auto_ui_config.display_name_plural` is set, the system SHALL use this for list views

#### Scenario: Configure list columns
- **WHEN** `auto_ui_config.list_columns` is set
- **THEN** the list view SHALL show only the specified columns in the specified order

#### Scenario: Configure search fields
- **WHEN** `auto_ui_config.search_fields` is set
- **THEN** the search functionality SHALL search only those fields

#### Scenario: Configure default sort
- **WHEN** `auto_ui_config.sort_default` is set
- **THEN** the list view SHALL sort by that field by default
- **AND** a minus prefix (e.g., `-date`) SHALL indicate descending order

#### Scenario: Configure per-field options
- **WHEN** `auto_ui_config.field_config[field_name]` is set
- **THEN** the system SHALL apply those options to the field
- **AND** supported options SHALL include `display_name`, `widget`, `readonly`, `hidden`, `help_text`

#### Scenario: Configure permissions
- **WHEN** `auto_ui_config.permissions` is set
- **THEN** the system SHALL use those permission functions for operation access control
- **AND** permissions SHALL support `list`, `create`, `read`, `update`, `delete` operations

### Requirement: Error Handling
The system SHALL handle errors gracefully and provide helpful error messages to users.

#### Scenario: Handle record not found
- **WHEN** a user attempts to view, edit, or delete a non-existent record
- **THEN** the system SHALL return a 404 error
- **AND** the error page SHALL provide a link back to the list view

#### Scenario: Handle validation errors
- **WHEN** form validation fails
- **THEN** the system SHALL display validation errors clearly
- **AND** the system SHALL indicate which fields have errors
- **AND** the system SHALL preserve user input

#### Scenario: Handle database errors
- **WHEN** a database operation fails
- **THEN** the system SHALL display a user-friendly error message
- **AND** the system SHALL log the detailed error for debugging

#### Scenario: Handle permission errors
- **WHEN** a user lacks permission for an operation
- **THEN** the system SHALL redirect to login if not authenticated
- **OR** the system SHALL show a 403 forbidden error if authenticated but lacking permission
- **AND** the error SHALL indicate what permission is required

### Requirement: Integration with Existing App
The system SHALL integrate seamlessly with existing Emmett applications without requiring major refactoring.

#### Scenario: Co-exist with manual routes
- **WHEN** auto UI is enabled for a model
- **THEN** existing manual routes SHALL continue to work
- **AND** the auto UI routes SHALL not conflict with existing routes

#### Scenario: Share authentication
- **WHEN** the app uses Emmett's Auth module
- **THEN** auto UI SHALL use the same authentication system
- **AND** auto UI SHALL respect the same session management

#### Scenario: Use existing templates
- **WHEN** the app has a base layout template
- **THEN** auto UI templates SHALL extend the app's layout
- **AND** auto UI SHALL inherit the app's styling and navigation

