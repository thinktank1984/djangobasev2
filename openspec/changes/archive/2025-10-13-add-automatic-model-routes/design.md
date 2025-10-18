# Design: Automatic Route Generation for Models

## Context

The Emmett application currently requires models to define explicit `setup()` functions to expose routes. This works but creates inconsistency: Post, Comment, and User have routes while Role, Permission, and OAuth models do not.

The existing `auto_ui()` helper provides automatic CRUD UI generation but still requires manual registration. We want to take this further by making route generation automatic at the BaseModel level.

## Goals / Non-Goals

**Goals:**
- Automatic route generation for any BaseModel subclass
- Zero configuration needed for basic CRUD routes
- Declarative configuration via class attributes
- Full backwards compatibility with existing setup() functions
- Integration with existing RBAC permission system
- Automatic REST API endpoint generation

**Non-Goals:**
- Replacing auto_ui() system (we extend it, not replace it)
- Changing existing route behavior for Post/Comment/User
- Requiring database schema changes
- Supporting non-Emmett frameworks

## Decisions

### Decision 1: Class Attribute Configuration

**Decision**: Use `auto_routes` class attribute on models to enable and configure automatic routes.

**Why**: 
- Declarative and visible in model definition
- Easy to enable: `auto_routes = True`
- Easy to configure: `auto_routes = {...}`
- No impact on models that don't use it

**Alternatives considered**:
- Decorator-based: `@auto_routes` - Less flexible, harder to configure
- Config file: External YAML/JSON - Separates config from model definition
- Convention-based: Always generate routes - No opt-out mechanism

**Example**:
```python
class Role(BaseModel):
    name = Field.string()
    description = Field.text()
    
    auto_routes = True  # Enable with defaults
    
class Permission(BaseModel):
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/permissions',
        'enabled_actions': ['list', 'detail', 'create'],  # No edit/delete
        'permissions': {
            'list': lambda: user_has_role(get_current_user(), 'Admin')
        }
    }
```

### Decision 2: Model Discovery via Database Initialization

**Decision**: Discover and register models automatically during `db.define_models()` call.

**Why**:
- Natural integration point - all models are registered with database
- Happens once at startup
- Access to database connection for relationship resolution
- Can leverage Emmett's model registry

**Alternatives considered**:
- Manual registration: `register_model_routes(Role)` - Still requires boilerplate
- Metaclass magic: Automatic at class definition - Can cause import-order issues
- Startup hook: Separate initialization step - Extra complexity

**Implementation**:
```python
# In app.py, after db.define_models()
from models import discover_and_register_auto_routes
discover_and_register_auto_routes(app, db)
```

### Decision 3: Precedence: Manual Setup > Auto Routes

**Decision**: Manual `setup()` functions always take precedence over `auto_routes`.

**Why**:
- Full backwards compatibility
- Allows gradual migration
- Provides escape hatch for complex custom routes
- Clear precedence hierarchy

**Implementation**:
- Check if model has `setup` function in package `__init__.py`
- If yes, call `setup()` and skip auto_routes
- If no, generate routes from auto_routes configuration

### Decision 4: Integration with auto_ui()

**Decision**: Automatic routes will call `auto_ui()` internally, not replace it.

**Why**:
- Reuse existing, tested UI generation code
- Maintain consistency with manually registered auto_ui models
- Leverage existing template system
- No duplication of form/view generation logic

**Implementation**:
```python
def _generate_routes(model_class, config, app):
    """Generate automatic routes for a model."""
    url_prefix = config.get('url_prefix', f'/{model_class.tablename}')
    
    # Call existing auto_ui system
    auto_ui(app, model_class, url_prefix)
    
    # Generate REST API if configured
    if config.get('rest_api', True):
        rest_module = app.rest_module(
            __name__, 
            f'{model_class.tablename}_api',
            model_class,
            url_prefix=f'api/{model_class.tablename}'
        )
```

### Decision 5: Configuration Schema

**Decision**: Use dictionary-based configuration with clear defaults.

**Configuration options**:
```python
auto_routes = {
    # Required
    'enabled': True,  # Or just auto_routes = True
    
    # Optional - URL patterns
    'url_prefix': '/admin/roles',  # Default: f'/{tablename}'
    'rest_api': True,  # Default: True
    'rest_prefix': 'api/roles',  # Default: f'api/{tablename}'
    
    # Optional - Enabled actions
    'enabled_actions': ['list', 'detail', 'create', 'update', 'delete'],  # Default: all
    
    # Optional - Permissions (callable functions)
    'permissions': {
        'list': callable,    # Default: None (public)
        'detail': callable,  # Default: None (public)
        'create': callable,  # Default: None (public)
        'update': callable,  # Default: None (public)
        'delete': callable,  # Default: None (public)
    },
    
    # Optional - Auto UI config pass-through
    'auto_ui_config': {
        'display_name': 'Role',
        'display_name_plural': 'Roles',
        'list_columns': ['name', 'description'],
        # ... other auto_ui options
    },
    
    # Optional - Custom handlers (override auto-generated)
    'custom_handlers': {
        'list': async_function,
        'detail': async_function,
        # ...
    }
}
```

## Risks / Trade-offs

### Risk 1: Route Conflicts
**Risk**: Automatically generated routes might conflict with manually defined routes.

**Mitigation**: 
- Detect conflicts during registration
- Raise clear error with conflicting route path
- Manual routes always win (skip auto-generation if conflict)
- Provide `ignore_conflicts=True` option for debugging

### Risk 2: Import Order Issues
**Risk**: Model discovery might happen before all models are imported.

**Mitigation**:
- Run discovery after explicit `db.define_models()` call
- Document required initialization order in AGENTS.md
- Provide clear error message if models not yet defined

### Risk 3: Performance Impact
**Risk**: Automatic discovery and registration adds startup time.

**Mitigation**:
- Discovery is O(n) where n = number of models (typically < 20)
- Route registration happens once at startup
- Measure and document actual impact
- Cache discovered models if needed

### Risk 4: Breaking Changes to auto_ui
**Risk**: Changes to auto_ui might break automatic route generation.

**Mitigation**:
- Keep integration surface small
- Test with all auto_ui features
- Document dependency on auto_ui version
- Version lock auto_ui compatibility

## Migration Plan

### Phase 1: Add Feature (Non-Breaking)
1. Implement automatic route generation in BaseModel
2. Implement model discovery system
3. Add integration point in app.py
4. All existing models continue using manual setup()
5. Test with new test models

### Phase 2: Migrate Simple Models
1. Add `auto_routes = True` to Role model
2. Add `auto_routes = True` to Permission model
3. Verify routes work identically
4. Keep setup() functions commented for rollback

### Phase 3: Migrate Complex Models (Optional)
1. Evaluate Post, Comment, User for migration
2. If desired, add auto_routes with custom handlers
3. Remove setup() functions
4. Update documentation

### Phase 4: Cleanup
1. Mark manual setup() pattern as legacy
2. Update documentation to prefer auto_routes
3. Create migration guide for existing projects
4. Consider deprecation warnings for setup() (future)

### Rollback Plan
- If issues arise, set `auto_routes = False` on affected models
- Keep old setup() functions in git history
- Revert app.py integration commit
- No database changes needed

## Open Questions

1. **Q**: Should auto_routes be enabled by default for all new models?
   **A**: No. Require explicit `auto_routes = True` to avoid surprising behavior.

2. **Q**: How to handle models that should never have routes (join tables)?
   **A**: Don't set `auto_routes` on them. Convention: models with routes are typically user-facing entities.

3. **Q**: Should we auto-generate admin-only routes separately from public routes?
   **A**: No. Use permissions configuration to control access. Keep route generation logic unified.

4. **Q**: What about WebSocket routes or custom HTTP methods?
   **A**: Out of scope. Use manual setup() for advanced routing. Auto routes handle standard REST patterns.

5. **Q**: Should we validate auto_routes configuration at class definition or at registration?
   **A**: At registration (during discover_and_register). Allows for dynamic configuration and clearer error messages.

