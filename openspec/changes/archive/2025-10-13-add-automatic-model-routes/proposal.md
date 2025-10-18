# Proposal: Automatic Route Generation for Models

## Why

Currently, models must explicitly define a `setup()` function and be manually registered in `models/__init__.py` to expose routes. This creates several problems:

1. **Inconsistent API**: Role, Permission, UserRole, RolePermission, OAuthAccount, and OAuthToken models don't expose routes, while Post, Comment, and User do
2. **Boilerplate code**: Each model requires ~100+ lines of route setup code that is largely repetitive
3. **Easy to forget**: Developers can create models but forget to add routes, leading to incomplete APIs
4. **Maintenance burden**: Changes to route patterns require updating multiple setup functions

The `auto_ui()` helper exists but still requires explicit registration for each model. We need a more automatic approach that works at the BaseModel level.

## What Changes

- Extend `BaseModel` class to automatically generate and register routes when models are defined
- Add `auto_routes` class attribute to enable/configure automatic route generation
- Auto-register models with routes during database initialization
- Provide sensible defaults while allowing per-model customization
- **NON-BREAKING**: Existing manual `setup()` functions continue to work and take precedence

## Impact

- **Affected specs**: `auto-ui-generation` (extends route generation requirements)
- **Affected code**: 
  - `runtime/base_model.py` - Add automatic route registration
  - `runtime/app.py` - Add automatic model discovery and registration
  - `runtime/models/__init__.py` - Add automatic setup for models
  - All model classes gain automatic routes by default

## Benefits

1. **Zero boilerplate**: Models get routes automatically without setup functions
2. **Consistent API**: All models expose the same route patterns
3. **Developer experience**: New models work immediately without manual wiring
4. **Backwards compatible**: Existing code continues to work
5. **Declarative**: Configure routes via class attributes, not procedural code

## Example Usage

```python
# Before: Manual setup required
class Role(BaseModel):
    name = Field.string()
    
def setup(app):
    # 100+ lines of route definitions
    pass

# After: Automatic routes
class Role(BaseModel):
    name = Field.string()
    
    auto_routes = True  # Routes generated automatically!
    
# Or with customization:
class Role(BaseModel):
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/roles',
        'enabled_actions': ['list', 'detail', 'create', 'update'],  # No delete
        'permissions': {
            'list': lambda: user_has_role(get_current_user(), 'Admin'),
            'create': lambda: user_has_role(get_current_user(), 'Admin'),
        }
    }
```

