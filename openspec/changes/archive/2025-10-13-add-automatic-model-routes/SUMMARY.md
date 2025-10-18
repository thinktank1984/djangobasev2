# Summary: Automatic Route Generation for Models

## The Problem

**Q: Why doesn't the User Role model expose routes?**

**A: Because only models with explicit `setup()` functions and manual registration get routes.**

Currently, route exposure works like this:

```python
# models/__init__.py
def setup_all(app):
    from .post import setup as post_setup
    from .comment import setup as comment_setup
    from .user import setup as user_setup
    
    # Only these three models get routes!
    apis = {
        'posts_api': post_setup(app),
        'comments_api': comment_setup(app),
        'users_api': user_setup(app)
    }
    return apis
```

**Models WITH routes**: Post, Comment, User (manually registered)
**Models WITHOUT routes**: Role, Permission, UserRole, RolePermission, OAuthAccount, OAuthToken

Each model with routes requires:
1. A `setup()` function (~100+ lines of boilerplate)
2. Manual registration in `models/__init__.py`
3. Explicit route definitions for list, detail, create, update, delete
4. Explicit REST API registration

**This is tedious and error-prone.**

## The Solution

Add **automatic route generation** to `BaseModel` class:

```python
# NEW APPROACH: Automatic routes
class Role(BaseModel):
    name = Field.string()
    description = Field.text()
    
    auto_routes = True  # That's it! Routes generated automatically.
```

### What You Get

With `auto_routes = True`, the model automatically gets:

✅ **HTML Routes:**
- `GET /roles/` - List all roles
- `GET /roles/<id>` - View role details
- `GET /roles/new` - Create form
- `POST /roles/` - Submit create
- `GET /roles/<id>/edit` - Edit form
- `POST /roles/<id>` - Submit update
- `GET /roles/<id>/delete` - Delete confirmation
- `POST /roles/<id>/delete` - Confirm delete

✅ **REST API:**
- `GET /api/roles` - List (JSON)
- `GET /api/roles/<id>` - Detail (JSON)
- `POST /api/roles` - Create (JSON)
- `PUT /api/roles/<id>` - Update (JSON)
- `DELETE /api/roles/<id>` - Delete (JSON)

✅ **OpenAPI Documentation** - Automatic Swagger docs at `/api/docs`

### Advanced Configuration

For more control:

```python
class Permission(BaseModel):
    name = Field.string()
    
    auto_routes = {
        'url_prefix': '/admin/permissions',
        'enabled_actions': ['list', 'detail', 'create'],  # No edit/delete
        'permissions': {
            'list': lambda: user_has_role(get_current_user(), 'Admin'),
            'create': lambda: user_has_role(get_current_user(), 'Admin'),
        },
        'rest_api': True,
        'auto_ui_config': {
            'display_name': 'Permission',
            'list_columns': ['name', 'description'],
        }
    }
```

### Backwards Compatible

Existing models with manual `setup()` functions continue to work:

```python
# Still works! Manual setup takes precedence
class Post(BaseModel):
    # ... fields ...

def setup(app):
    # Custom routes
    app.route("/", name='app.index')(index)
    # ...
```

## Benefits

| Before (Manual) | After (Automatic) |
|----------------|-------------------|
| ~100 lines of setup code per model | 1 line: `auto_routes = True` |
| Manual registration in `__init__.py` | Automatic discovery |
| Inconsistent: Some models have routes, some don't | Consistent: All models can have routes |
| Easy to forget | Automatic |
| Hard to maintain | Declarative config |

## Implementation Status

📋 **Proposal Stage** - Awaiting approval

Once approved, implementation includes:
1. Extend BaseModel with auto_routes support
2. Add model discovery system
3. Integrate with existing auto_ui() system
4. Add permission integration
5. Update Role, Permission, and OAuth models
6. Comprehensive testing

## Next Steps

1. **Review this proposal** - Does it solve the right problem?
2. **Approve for implementation** - If design is sound
3. **Implement** - Follow tasks.md checklist
4. **Test** - Verify all CRUD operations work
5. **Migrate models** - Add auto_routes to Role, Permission, etc.

## Questions?

- **Q: Will this break existing code?** No! Manual setup() functions take precedence.
- **Q: Do I have to use it?** No! It's opt-in via `auto_routes = True`.
- **Q: Can I customize the generated routes?** Yes! Use the configuration dictionary.
- **Q: What about permissions?** Fully integrated with RBAC system via `auto_routes['permissions']`.
- **Q: What about complex custom routes?** Use manual setup() or override specific handlers.

---

**To answer your original question**: Role doesn't expose routes because it lacks a `setup()` function and isn't in `setup_all()`. This proposal fixes that by making routes automatic! 🎉

