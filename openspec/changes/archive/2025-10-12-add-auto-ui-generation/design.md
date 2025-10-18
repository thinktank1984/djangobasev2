# Auto UI Generation Design

## Context

Emmett provides `Form.from_model()` for generating forms from ORM models, but developers still need to:
- Manually create routes for CRUD operations
- Write templates for list, detail, create, edit, and delete views
- Implement pagination, search, and filtering logic
- Handle validation and error display
- Style forms and views consistently

Other frameworks (Django Admin, Rails ActiveAdmin, Flask-Admin) provide automatic admin interfaces that dramatically speed up development. This design brings similar capabilities to Emmett while maintaining its simplicity and async-first approach.

### Stakeholders
- Application developers who want rapid CRUD interface development
- Admin panel builders who need consistent, professional interfaces
- Teams building internal tools and dashboards

### Constraints
- Must be compatible with Emmett's async route handlers
- Must work with pyDAL ORM models
- Must integrate with Emmett's Auth module for permissions
- Must use Tailwind CSS for styling (already integrated in project)
- Must follow Emmett's conventions (decorators, pipelines, templates)

## Goals / Non-Goals

### Goals
- Provide zero-config CRUD interface generation from models
- Support customization through model metadata and configuration
- Generate responsive, accessible UIs following modern UX practices
- Integrate seamlessly with existing Emmett Auth and permission systems
- Support advanced features: pagination, search, filtering, sorting
- Allow template overrides for custom designs
- Maintain Emmett's simplicity and async-first approach

### Non-Goals
- Not a full admin dashboard (no navigation sidebar, dashboards, charts)
- Not a form builder UI (configuration through code only)
- Not a replacement for custom UIs (supplement, not replacement)
- Not supporting non-Emmett ORMs (pyDAL only)
- Not providing REST API generation (that's `emmett-rest`, already implemented)

## Decisions

### Decision 1: Decorator-Based API

**Choice**: Use decorator-based API for enabling auto UI
```python
from auto_ui_generator import auto_ui

@app.auto_ui(Post, url_prefix='/admin/posts')
```

**Alternatives Considered**:
1. Configuration file approach: `auto_ui.yaml` with model mappings
   - Rejected: Less discoverable, adds configuration file complexity
2. Manual registration: `auto_ui.register(app, Post, '/admin/posts')`
   - Rejected: More verbose, less "Emmett-like"
3. Class-based views: `class PostAdmin(AutoUI): model = Post`
   - Rejected: Too Django-like, not idiomatic Emmett

**Rationale**: Emmett uses decorators extensively (`@app.route()`, `@requires()`, `@service.json`). A decorator API feels natural and discoverable.

### Decision 2: Template Hierarchy

**Choice**: Template inheritance with override capability
```
templates/auto_ui/
├── layout.html           # Base layout (extends app layout.html)
├── list.html            # List view template
├── detail.html          # Detail view template
├── form.html            # Create/Edit form template
└── delete.html          # Delete confirmation template
```

**Override mechanism**: Allow custom templates by placing files in `templates/auto_ui_custom/[model_name]/`

**Rationale**: 
- Matches Emmett's template patterns
- Allows global styling while supporting per-model customization
- Easy to understand and extend

### Decision 3: Model Configuration via Class Attribute

**Choice**: Add `auto_ui_config` dictionary to models
```python
class Post(Model):
    title = Field()
    text = Field.text()
    
    auto_ui_config = {
        'display_name': 'Blog Post',
        'display_name_plural': 'Blog Posts',
        'list_columns': ['id', 'title', 'user', 'date'],
        'search_fields': ['title', 'text'],
        'sort_default': '-date',
        'permissions': {
            'list': lambda: True,
            'create': lambda: auth.user and 'admin' in auth.user.groups,
            'update': lambda: auth.user and 'admin' in auth.user.groups,
            'delete': lambda: auth.user and 'admin' in auth.user.groups,
        },
        'field_config': {
            'title': {'display_name': 'Title', 'required': True},
            'text': {'display_name': 'Content', 'widget': 'textarea'},
            'user': {'readonly': True, 'display_name': 'Author'},
        }
    }
```

**Alternatives Considered**:
1. Separate config file per model: `post_ui_config.py`
   - Rejected: Splits model definition across files
2. Decorators on fields: `title = Field(ui_display='Title')`
   - Rejected: Mixes ORM concerns with UI concerns
3. External registry: `auto_ui.configure(Post, {...})`
   - Rejected: Configuration separated from model definition

**Rationale**: Keeping configuration with the model class is discoverable and maintains locality of behavior.

### Decision 4: Route Pattern

**Choice**: Generate 5 standard routes per model
```
GET  /admin/posts          -> list view (with pagination, search)
GET  /admin/posts/new      -> create form
POST /admin/posts          -> create action
GET  /admin/posts/<id>     -> detail view
GET  /admin/posts/<id>/edit -> edit form
POST /admin/posts/<id>     -> update action
GET  /admin/posts/<id>/delete -> delete confirmation
POST /admin/posts/<id>/delete -> delete action
```

**Alternatives Considered**:
1. RESTful pattern (PUT/DELETE verbs): Not well-supported by HTML forms without JavaScript
2. All operations in single route: Too complex, poor separation of concerns
3. Separate actions with explicit names: `/admin/posts/1/update_action` - Too verbose

**Rationale**: This pattern is familiar from Rails, Django, and follows HTML form conventions (GET for views, POST for actions).

### Decision 5: Permission Integration

**Choice**: Integrate with Emmett's `@requires()` decorator and Auth module
```python
# Auto-generated routes will check permissions:
@app.route('/admin/posts')
@requires(lambda: check_permission('list'), url('auth/login'))
async def posts_list():
    ...
```

**Rationale**: 
- Reuses existing Emmett Auth infrastructure
- Consistent with how developers already handle permissions
- No new permission system to learn

### Decision 6: Styling with Tailwind CSS

**Choice**: Use Tailwind CSS utility classes in templates

**Rationale**:
- Already integrated in the project (see `add-tailwind-css-support` in archive)
- Modern, responsive design out of the box
- Easy to customize via Tailwind config
- Small learning curve for developers familiar with CSS

### Decision 7: Field Type to Widget Mapping via ui_mapping.json

**Choice**: Configurable widget selection via `ui_mapping.json` file with automatic loading
```json
{
  "mappings": {
    "string": {
      "component": "input",
      "attributes": {
        "type": "text",
        "class": "form-input rounded-md border-gray-300"
      }
    },
    "text": {
      "component": "textarea",
      "attributes": {
        "rows": 5,
        "class": "form-textarea rounded-md border-gray-300"
      }
    },
    "bool": {
      "component": "input",
      "attributes": {
        "type": "checkbox",
        "class": "form-checkbox rounded"
      }
    },
    "int": {
      "component": "input",
      "attributes": {
        "type": "number",
        "class": "form-input rounded-md border-gray-300"
      }
    },
    "datetime": {
      "component": "input",
      "attributes": {
        "type": "datetime-local",
        "class": "form-input rounded-md border-gray-300"
      }
    },
    "date": {
      "component": "input",
      "attributes": {
        "type": "date",
        "class": "form-input rounded-md border-gray-300"
      }
    },
    "belongs_to": {
      "component": "select",
      "attributes": {
        "class": "form-select rounded-md border-gray-300"
      },
      "populate": "related_records"
    }
  },
  "display_formatters": {
    "datetime": "format_datetime",
    "date": "format_date",
    "bool": "format_boolean",
    "belongs_to": "format_relationship"
  }
}
```

**Location**: `runtime/ui_mapping.json` (default) with override support at `runtime/ui_mapping_custom.json`

**Alternatives Considered**:
1. Hardcoded mapping in Python: `FIELD_TYPE_MAP = {...}`
   - Rejected: Not easily customizable without code changes
2. Database-stored mappings: Store in DB table
   - Rejected: Adds complexity, requires migrations, overkill for configuration
3. Python file configuration: `ui_mapping.py` with dictionaries
   - Rejected: JSON is simpler and can be edited without Python knowledge

**Rationale**: 
- JSON file is easily editable without touching code
- Developers can customize widget types, CSS classes, and HTML attributes
- Custom override file allows project-specific customization without modifying defaults
- Supports display formatters for rendering field values in detail/list views
- Framework maintainers can update default mappings without breaking user customizations

## UI Mapping JSON Schema

### Schema Structure

The `ui_mapping.json` file follows this schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "mappings": {
      "type": "object",
      "description": "Maps field types to UI components",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "component": {
            "type": "string",
            "enum": ["input", "textarea", "select", "checkbox", "radio"],
            "description": "HTML element type"
          },
          "attributes": {
            "type": "object",
            "description": "HTML attributes to apply to the component",
            "additionalProperties": true
          },
          "populate": {
            "type": "string",
            "description": "Data population strategy (e.g., 'related_records')"
          }
        },
        "required": ["component"]
      }
    },
    "display_formatters": {
      "type": "object",
      "description": "Maps field types to formatting functions",
      "additionalProperties": {
        "type": "string",
        "description": "Name of formatter function"
      }
    }
  }
}
```

### Example Usage

**Default mapping** (`ui_mapping.json`):
```json
{
  "mappings": {
    "string": {
      "component": "input",
      "attributes": {
        "type": "text",
        "class": "form-input rounded-md border-gray-300"
      }
    }
  }
}
```

**Custom override** (`ui_mapping_custom.json`):
```json
{
  "mappings": {
    "string": {
      "component": "input",
      "attributes": {
        "type": "text",
        "class": "form-input rounded-lg border-blue-500 shadow-sm"
      }
    },
    "email": {
      "component": "input",
      "attributes": {
        "type": "email",
        "class": "form-input rounded-md border-gray-300",
        "autocomplete": "email"
      }
    }
  }
}
```

**Result**: String fields use custom classes, email fields are added, other types use defaults.

### Formatter Functions

The system provides built-in formatters referenced in `display_formatters`:

- `format_datetime`: Formats datetime objects as "Jan 15, 2025 3:30 PM"
- `format_date`: Formats date objects as "Jan 15, 2025"
- `format_boolean`: Formats booleans as "Yes" / "No" with icons
- `format_relationship`: Displays related object's string representation with link

Custom formatters can be added by extending the `AutoUIGenerator` class.

## Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Application Code                      │
│  @app.auto_ui(Post, url_prefix='/admin/posts')         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               AutoUIGenerator                            │
│  - Load UI mappings from JSON                            │
│  - Introspect model (fields, relations, validation)     │
│  - Resolve field types to UI components                  │
│  - Generate routes (list, create, read, update, delete) │
│  - Register routes with app                              │
│  - Apply permissions                                     │
└─────────────────────────────────────────────────────────┘
         │                │                │
         ▼                ▼                ▼
    ┌─────────┐    ┌──────────┐     ┌─────────┐
    │ui_mapping│   │ui_mapping│     │ Model   │
    │  .json   │   │_custom   │     │ Intrsp. │
    │(default) │   │  .json   │     │         │
    └─────────┘    └──────────┘     └─────────┘
         │                │                │
         └────────┬───────┘                │
                  ▼                        │
         ┌────────────────┐                │
         │ UIMappingLoader│                │
         │ - Merge configs│                │
         │ - Resolve types│                │
         └────────────────┘                │
                  │                        │
         ┌────────┴────────────────────────┘
         ▼
    ┌────────┐      ┌─────────┐      ┌─────────┐
    │ Routes │      │Templates│      │ Forms   │
    │        │      │         │      │         │
    │ List   │─────▶│ list    │      │Form.from│
    │ Create │─────▶│ form    │◀─────│ _model()│
    │ Detail │─────▶│ detail  │      │  +UI    │
    │ Update │─────▶│ form    │      │ mapping │
    │ Delete │─────▶│ delete  │      │         │
    └────────┘      └─────────┘      └─────────┘
```

### Data Flow

**List View Flow**:
```
User → GET /admin/posts
  ↓
Check 'list' permission
  ↓
Query model with pagination
  ↓
Render list.html template
  ↓
Display records in table with actions
```

**Create Flow**:
```
User → GET /admin/posts/new
  ↓
Check 'create' permission
  ↓
Generate form from model
  ↓
Render form.html template
  ↓
User submits → POST /admin/posts
  ↓
Validate form
  ↓
Save to database (on success)
  ↓
Redirect to detail view
```

### Class Structure

```python
class UIMappingLoader:
    def __init__(self, default_path='ui_mapping.json', custom_path='ui_mapping_custom.json'):
        self.default_path = default_path
        self.custom_path = custom_path
        self.mappings = {}
        self.formatters = {}
    
    def load(self):
        """Load and merge UI mappings from JSON files"""
        self._load_defaults()
        self._load_custom()
        return self
    
    def _load_defaults(self):
        """Load default ui_mapping.json"""
        ...
    
    def _load_custom(self):
        """Load and merge ui_mapping_custom.json"""
        ...
    
    def get_component_for_type(self, field_type):
        """Get UI component configuration for field type"""
        return self.mappings.get(field_type, self._default_mapping())
    
    def get_formatter_for_type(self, field_type):
        """Get display formatter function name for field type"""
        return self.formatters.get(field_type)


class AutoUIGenerator:
    def __init__(self, app, model, url_prefix, config=None):
        self.app = app
        self.model = model
        self.url_prefix = url_prefix
        self.config = self._merge_config(model, config)
        self.ui_mapping = UIMappingLoader().load()
    
    def register_routes(self):
        """Register all CRUD routes with the app"""
        self._register_list_route()
        self._register_create_routes()
        self._register_detail_route()
        self._register_update_routes()
        self._register_delete_routes()
    
    def _register_list_route(self):
        """Create and register list view route"""
        ...
    
    def _introspect_model(self):
        """Extract fields, relationships, validation from model"""
        ...
    
    def _resolve_field_component(self, field):
        """Resolve field to UI component using ui_mapping"""
        field_type = self._get_field_type(field)
        return self.ui_mapping.get_component_for_type(field_type)
    
    def _format_field_value(self, field, value):
        """Format field value for display using formatters"""
        field_type = self._get_field_type(field)
        formatter_name = self.ui_mapping.get_formatter_for_type(field_type)
        if formatter_name and hasattr(self, formatter_name):
            return getattr(self, formatter_name)(value)
        return str(value)
    
    def _check_permission(self, operation):
        """Check if current user has permission for operation"""
        ...
    
    def _get_template(self, template_name):
        """Get template with override support"""
        ...
```

## Risks / Trade-offs

### Risk 1: Performance with Large Datasets
**Risk**: List views with thousands of records could be slow

**Mitigation**:
- Implement pagination (default 25 records per page)
- Use efficient queries (select only needed fields)
- Add indexes to commonly searched/sorted fields
- Provide configuration for page size limits

### Risk 2: Security - Mass Assignment
**Risk**: Auto-generated forms might expose fields that shouldn't be user-editable

**Mitigation**:
- Respect model's `fields_rw` configuration (read/write permissions)
- Provide `readonly` option in `field_config`
- Default to hiding sensitive fields (passwords, tokens)
- Require explicit permission checks for all operations

### Risk 3: Customization vs Simplicity
**Risk**: Too much customization makes the API complex; too little makes it inflexible

**Trade-off**: 
- Start with sensible defaults (zero config works)
- Add configuration options progressively
- Support template overrides for complete customization
- Document common customization patterns

### Risk 4: Template Maintenance
**Risk**: Maintaining templates in sync with feature additions

**Mitigation**:
- Keep templates simple and focused
- Use template inheritance to minimize duplication
- Write UI tests to catch template regressions
- Document template structure clearly

## Migration Plan

Not applicable - this is a new feature.

### Rollout Strategy
1. **Phase 1**: Implement core functionality (list, create, detail)
2. **Phase 2**: Add advanced features (search, filtering, sorting)
3. **Phase 3**: Add bulk operations and export
4. **Phase 4**: Gather feedback and iterate

### Backward Compatibility
No breaking changes - new optional feature.

## Open Questions

1. **Q**: Should we auto-generate navigation menus for multiple auto UI models?
   **A**: Not in first version - out of scope. Users can manually create navigation.

2. **Q**: Should we support inline editing in list views (edit without navigation)?
   **A**: Defer to Phase 3 - start with traditional navigation-based editing.

3. **Q**: How should we handle file uploads in auto-generated forms?
   **A**: Use standard HTML file inputs, store path in database. Full asset management out of scope.

4. **Q**: Should we support nested resource routes (e.g., `/posts/1/comments/new`)?
   **A**: Defer to future version - start with flat resource routes.

5. **Q**: Should list views support grouping/aggregation?
   **A**: No - keep list views simple. Complex reporting out of scope.

