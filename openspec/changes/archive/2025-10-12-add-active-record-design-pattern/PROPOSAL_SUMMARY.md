# Active Record Design Pattern - Proposal Summary

## Overview

This proposal introduces a comprehensive Active Record design pattern for the application, enabling:
- **Clean model architecture** with enforced separation of concerns
- **Automatic REST API generation** from model definitions
- **Automatic Swagger/OpenAPI documentation** generation
- **Automatic CRUD page generation** with Tailwind CSS styling
- **Automatic permission enforcement** based on decorators
- **Zero-boilerplate development** - define model once, get everything automatically

## Problem Statement

Currently, models in the codebase have:
- Mixed concerns (domain logic, UI logic, HTTP handling)
- No standardized structure
- Manual API endpoint creation
- Manual documentation maintenance
- Manual permission management
- Inconsistent patterns across the codebase

## Solution

Implement Active Record pattern with automatic generation:

### 1. Active Record Base Class
```python
class Post(Model, ActiveRecord):
    title = Field.string()
    content = Field.text()
    
    @validates('title')
    def validate_title(self, value):
        return len(value) >= 3
    
    @ui_override(field='content', widget='rich_text_editor')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic']}
    
    def publish(self):
        self.published = True
        return self.save()
    
    @requires_permission('admin')
    def feature(self):
        self.featured = True
        return self.save()
```

### 2. What Gets Auto-Generated

From the model above, **automatically generate**:

#### REST API Endpoints
```
GET    /api/posts          - List with pagination, filtering, sorting
GET    /api/posts/:id      - Retrieve single record
POST   /api/posts          - Create (requires auth)
PUT    /api/posts/:id      - Update (requires ownership or admin)
DELETE /api/posts/:id      - Delete (requires ownership or admin)
```

#### OpenAPI/Swagger Documentation
- Complete API specification at `/swagger.json`
- Interactive Swagger UI at `/api/docs`
- Includes validation rules, authentication requirements
- Always up-to-date with model definitions

#### CRUD Pages
```
/posts              - List view with pagination
/posts/new          - Create form (respects permissions)
/posts/:id          - Detail view
/posts/:id/edit     - Edit form (respects permissions)
```

#### Permission System
- Authentication checks for write operations
- Ownership checks (user can edit own posts)
- Admin bypass for ownership checks
- Method-level permissions from decorators
- Field-level permissions

## Key Benefits

1. **Developer Productivity**: Write model once, get API + UI + docs + permissions
2. **Consistency**: All endpoints follow same patterns and conventions
3. **Maintainability**: Single source of truth for business logic
4. **Documentation**: Swagger always reflects actual implementation
5. **Security**: Permissions automatically enforced, less chance of mistakes
6. **Testing**: Pure domain models are easier to test
7. **Onboarding**: New developers understand structure immediately

## Impact

### New Capabilities
- `rest-api` - Automatic REST API generation
- `permissions` - Automatic permission management

### Modified Capabilities
- `orm` - Enhanced with Active Record pattern
- `auto-ui-generation` - Updated to use Active Record introspection

### New Files
- `runtime/auto_api_generator.py` - REST API generator
- `runtime/auto_page_generator.py` - CRUD page generator
- `runtime/auto_permission_generator.py` - Permission system
- `runtime/test_active_record.py` - Comprehensive tests
- `documentation/active_record_pattern.md` - Pattern guide

### Modified Files
- `runtime/app.py` - Add ActiveRecord base class
- `runtime/openapi_generator.py` - Use ActiveRecord introspection
- `runtime/auto_ui_generator.py` - Use ActiveRecord introspection

## Implementation Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 3 hours | Base class, decorators, introspection API |
| Phase 2 | 2 hours | Pattern validation, anti-pattern detection |
| Phase 3 | 4 hours | Refactor existing models (User, Post, Comment) |
| Phase 4 | 5 hours | API generator, page generator, permission generator |
| Phase 5 | 2 hours | UI generator integration |
| Phase 6 | 1 hour | Configuration, startup wiring |
| Phase 7 | 1 hour | Documentation, comprehensive tests |
| **Total** | **18 hours** | **Complete Active Record system** |

## Configuration Example

```python
class Post(Model, ActiveRecord):
    # Model fields...
    
    class Meta:
        # API Generation
        auto_generate_api = True
        api_prefix = '/api/v1'
        
        # Permissions
        require_auth_for_write = True
        ownership_field = 'user_id'
        admin_roles = ['admin']
        
        # UI Generation
        auto_generate_pages = True
        list_page_size = 25
        
        # Features
        enable_bulk_operations = True
        enable_search = True
        searchable_fields = ['title', 'content']
```

## Before and After

### Before (Manual Approach)

```python
# Model definition
class Post(Model):
    title = Field.string()
    content = Field.text()

# Separate API endpoint
@app.route('/api/posts', methods=['GET'])
def list_posts():
    posts = Post.all()
    return jsonify([p.serialize() for p in posts])

@app.route('/api/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.get(id)
    if not post:
        abort(404)
    return jsonify(post.serialize())

# Separate page route
@app.route('/posts')
def posts_page():
    posts = Post.all()
    return render('posts/list.html', posts=posts)

# Manual OpenAPI spec
openapi_spec['paths']['/api/posts'] = {
    'get': {
        'summary': 'List posts',
        # ... manual schema definition
    }
}

# Manual permission checks
@app.route('/api/posts/<int:id>', methods=['PUT'])
@requires_auth
def update_post(id):
    post = Post.get(id)
    if current_user.id != post.user_id and not current_user.is_admin():
        abort(403)
    # ... update logic
```

**Problems**: Lots of boilerplate, easy to forget permission checks, OpenAPI spec drifts from implementation.

### After (Active Record Approach)

```python
class Post(Model, ActiveRecord):
    title = Field.string()
    content = Field.text()
    user_id = Field.int()
    
    @validates('title')
    def validate_title(self, value):
        return len(value) >= 3
    
    class Meta:
        auto_generate_api = True
        auto_generate_pages = True
        auto_generate_swagger = True
        require_auth_for_write = True
        ownership_field = 'user_id'
```

**That's it!** Everything else is automatically generated:
- ✅ All CRUD API endpoints
- ✅ All CRUD pages
- ✅ OpenAPI documentation
- ✅ Permission checks
- ✅ Validation
- ✅ Error handling

## Risk Mitigation

### Risk: Breaking Existing Code
**Mitigation**: 
- Opt-in initially (inherit from ActiveRecord)
- Gradual migration model by model
- Feature flag for rollback
- Comprehensive test coverage

### Risk: Performance Overhead
**Mitigation**:
- Cache introspection results
- Lazy load generators
- Skip validation in production
- Profile before/after

### Risk: Team Adoption
**Mitigation**:
- Clear documentation with examples
- Training sessions
- Pilot migration (Post model first)
- Gather feedback and iterate

## Success Criteria

- ✅ All models follow Active Record pattern
- ✅ Zero manual API endpoints for CRUD operations
- ✅ OpenAPI docs automatically generated and accurate
- ✅ All permissions enforced automatically
- ✅ Pattern validation passes for all models
- ✅ 100% test coverage for Active Record features
- ✅ Team trained and comfortable with pattern

## Next Steps

1. **Review Proposal**: Team reviews this proposal
2. **Approve**: Get stakeholder approval
3. **Implement Phase 1**: Build foundation (ActiveRecord base class)
4. **Pilot Migration**: Migrate Post model as proof of concept
5. **Iterate**: Gather feedback, adjust as needed
6. **Complete Implementation**: Finish all phases
7. **Deploy**: Roll out to production
8. **Document**: Update team documentation
9. **Archive**: Move to archive after successful deployment

## Questions?

- How should we handle edge cases (models without UI)?
- Should we enforce Active Record for ALL new models?
- What's the rollback plan if issues arise?
- How do we handle custom endpoints that don't fit CRUD?

## References

- OpenSpec Change: `add-active-record-design-pattern`
- Proposal: `openspec/changes/add-active-record-design-pattern/proposal.md`
- Tasks: `openspec/changes/add-active-record-design-pattern/tasks.md`
- Design: `openspec/changes/add-active-record-design-pattern/design.md`
- Specs:
  - `openspec/changes/add-active-record-design-pattern/specs/orm/spec.md`
  - `openspec/changes/add-active-record-design-pattern/specs/auto-ui-generation/spec.md`
  - `openspec/changes/add-active-record-design-pattern/specs/rest-api/spec.md`
  - `openspec/changes/add-active-record-design-pattern/specs/permissions/spec.md`

---

## Implementation Status

**Status**: 🚧 Phase 1 Complete ✅ (20% Done)  
**Created**: 2025-10-12  
**Started**: 2025-10-13  
**Progress**: 47/83 tests passing (57%)  
**Time Spent**: 2 hours  
**Estimated Remaining**: 5-7 hours

### Completed
- ✅ **Phase 1**: Route registration pattern (2 hours)
  - Fixed route registration in consolidated model files
  - Post model routes fully functional
  - 5 tests fixed (+6% improvement)

### In Progress
- 🚧 **Phase 2**: Auth routes (2-3 hours) - Next action
  - Apply same pattern to User model
  - Should fix 8 failed tests + unlock 28 API tests

### Pending
- 🚧 **Phase 3**: API integration (2-3 hours)
- 🚧 **Phase 4**: Minor fixes (1 hour)

### Documentation
- `IMPLEMENTATION_STATUS.md` - Complete implementation tracking
- `ACTIVE_RECORD_PHASE1_COMPLETE.md` - Phase 1 completion guide
- `ACTIVE_RECORD_STATUS.md` - Current status dashboard

**Next Action**: Begin Phase 2 - Fix auth routes in User model

