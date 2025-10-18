# Add Auto UI Generation from Models

## Why

Developers spend significant time writing boilerplate code for CRUD operations: defining routes, creating form templates, handling validation, and rendering data. Emmett already provides `Form.from_model()` for basic form generation, but developers still need to manually create routes, templates, and views for each model.

Auto UI generation from models will dramatically reduce development time by automatically creating complete CRUD interfaces with proper styling, validation, and routing based on model definitions. This allows developers to focus on business logic while getting professional-looking admin interfaces automatically.

## What Changes

- Add `AutoUIGenerator` class that introspects Emmett ORM models and generates complete CRUD interfaces
- Provide decorator-based API: `@app.auto_ui(Post, url_prefix='/admin/posts')` to enable auto UI for a model
- **Create one UI component mapping for each ORM field type** (string, text, int, float, bool, datetime, date, time, password, email, url, belongs_to, etc.) with appropriate HTML input types and Tailwind CSS styling
- Generate routes automatically: list, create, read, update, delete operations
- Generate templates automatically using Tailwind CSS styling
- Add `ui_mapping.json` configuration file that maps model field types to UI components with attributes
- Support customization through model metadata: field display names, widget types, permissions, list columns
- Allow custom UI mappings via `ui_mapping_custom.json` override file
- Provide hooks for custom validation, permissions, and business logic
- Include pagination, search, and filtering in list views
- Support field-level customization via model decorators
- Generate responsive, accessible UI following modern UX practices

## Impact

### Affected Specs
- **New Capability**: `auto-ui-generation` - Complete specification for auto UI generation system

### Affected Code
- **New File**: `runtime/auto_ui_generator.py` - Core auto UI generation logic
- **New File**: `runtime/ui_mapping.json` - Default field type to UI component mappings
- **New Directory**: `runtime/templates/auto_ui/` - Default templates for generated UIs
  - `layout.html`, `list.html`, `detail.html`, `form.html`, `delete.html`
- **New Directory**: `runtime/templates/auto_ui/components/` - Separate UI components by usage
  - `form/` - 12 form input components (string, text, bool, int, float, datetime, date, time, password, email, url, select)
  - `display/` - 5 display components for detail views
  - `table/` - 6 table cell components for list views
- **Modified**: `runtime/app.py` - Add example usage of auto UI generation
- **Modified**: `runtime/tests.py` - Add tests for auto UI generation
- **New File**: `runtime/test_auto_ui.py` - Comprehensive unit tests
- **New File**: `documentation/AUTO_UI_GENERATION.md` - Complete documentation

### UI Mapping Configuration (`ui_mapping.json`)

The `runtime/ui_mapping.json` file defines how ORM field types map to HTML form components and their styling. This configuration drives the auto UI generation system.

**Structure:**
```json
{
  "mappings": {
    "field_type": {
      "component": "html_element",
      "attributes": { /* HTML attributes */ },
      "populate": "optional_data_source"
    }
  },
  "display_formatters": {
    "field_type": "formatter_function_name"
  }
}
```

**Implemented Field Type Mappings:**

| Field Type | HTML Component | Tailwind Classes | Special Attributes |
|------------|----------------|------------------|-------------------|
| `string` | `<input type="text">` | Rounded border, focus ring | - |
| `text` | `<textarea>` | Rounded border, 5 rows | - |
| `bool` | `<input type="checkbox">` | Indigo colors | - |
| `int` | `<input type="number">` | Rounded border | - |
| `float` | `<input type="number">` | Rounded border | `step="0.01"` |
| `datetime` | `<input type="datetime-local">` | Rounded border | - |
| `date` | `<input type="date">` | Rounded border | - |
| `time` | `<input type="time">` | Rounded border | - |
| `password` | `<input type="password">` | Rounded border | - |
| `email` | `<input type="email">` | Rounded border | `autocomplete="email"` |
| `url` | `<input type="url">` | Rounded border | - |
| `belongs_to` | `<select>` | Rounded border | `populate="related_records"` |

**Tailwind CSS Classes (All Fields):**
- Base: `mt-1 block w-full rounded-md border-gray-300 shadow-sm`
- Focus: `focus:border-indigo-500 focus:ring-indigo-500`
- Text size: `sm:text-sm`

**Display Formatters:**
- `datetime` → `format_datetime()` - Human-readable datetime
- `date` → `format_date()` - Localized date format
- `time` → `format_time()` - Localized time format
- `bool` → `format_boolean()` - "Yes"/"No" display
- `belongs_to` → `format_relationship()` - Related record name

**Customization:**
Developers can override mappings by creating `runtime/ui_mapping_custom.json` with the same structure. Custom mappings are merged with defaults, with custom values taking precedence.

### Breaking Changes
None - this is a new optional feature that doesn't affect existing code.

### Migration Path
Not applicable - new feature only.

