# Active Record Design Pattern - Technical Design

## Context

The current codebase has models with mixed concerns: domain logic, UI logic, HTTP handling, and data access are often intertwined. This makes models difficult to test, maintain, and reason about. The Active Record pattern provides a well-known solution that separates concerns while maintaining the convenience of models that "know how to save themselves."

### Current State
- Models inherit from Emmett's `Model` class
- Business logic mixed with presentation concerns
- No standardized structure for model organization
- Auto-UI generation uses ad-hoc introspection
- No validation of architectural patterns

### Desired State
- Models follow clean Active Record pattern
- Clear separation of concerns enforced by design
- Standardized introspection API for tooling
- Auto-UI generation uses reliable metadata
- Automated validation of pattern compliance

### Stakeholders
- **Developers**: Need clear patterns to follow
- **QA**: Need testable, predictable behavior
- **Auto-UI Generator**: Needs reliable model metadata
- **Future Maintainers**: Need clear architectural boundaries

---

## Goals / Non-Goals

### Goals
1. **Enforce separation of concerns** at the model layer
2. **Provide introspection API** for tooling and auto-generation
3. **Enable decorator-based extensions** without cluttering model code
4. **Validate pattern compliance** automatically
5. **Maintain backward compatibility** with existing models

### Non-Goals
1. **Not creating a new ORM** - still using Emmett's ORM
2. **Not changing database schema** - only model organization
3. **Not rewriting all code at once** - gradual migration
4. **Not enforcing pattern for all models** - opt-in initially

---

## Technical Decisions

### Decision 1: Mixin vs Base Class
**Chosen**: Mixin approach (`class Post(Model, ActiveRecord)`)

**Rationale**:
- Preserves Emmett's `Model` as primary base class
- Allows optional adoption (can use `Model` alone)
- Python MRO handles method resolution cleanly
- No breaking changes to existing code

**Alternatives Considered**:
- **Full base class replacement**: Too breaking, hard to migrate
- **Decorator-based**: Less explicit, harder to discover
- **Configuration file**: Disconnected from code, prone to drift

**Trade-offs**:
- ✅ Non-breaking, gradual adoption
- ✅ Clear opt-in via inheritance
- ⚠️ Multiple inheritance (but Python handles well)
- ⚠️ Need to document MRO implications

---

### Decision 2: Decorator Implementation
**Chosen**: Function decorators with registry pattern

**Rationale**:
- Pythonic and familiar to developers
- Allows composition of multiple decorators
- Clear visual separation in code
- Easy to introspect at runtime

**Example**:
```python
class Post(Model, ActiveRecord):
    @validates('title')
    def validate_title(self, value):
        return len(value) >= 3
    
    @ui_override(field='content', widget='rich_text')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic']}
```

**Alternatives Considered**:
- **Class-level attributes**: Less flexible, harder to compose
- **External configuration**: Disconnected from model definition
- **Metaclass magic**: Too implicit, harder to understand

**Trade-offs**:
- ✅ Familiar Python pattern
- ✅ Easy to read and write
- ✅ Good IDE support
- ⚠️ Runtime overhead (mitigated by caching)

---

### Decision 3: Introspection API
**Chosen**: Class methods on ActiveRecord mixin

**API**:
```python
Model.get_attributes() -> Dict[str, FieldInfo]
Model.get_methods() -> List[MethodInfo]
Model.get_ui_overrides() -> Dict[str, UIOverride]
Model.get_validators() -> Dict[str, List[Validator]]
```

**Rationale**:
- Class methods don't require instances
- Consistent API across all Active Record models
- Easy to mock for testing
- Can be cached at class level

**Alternatives Considered**:
- **Instance methods**: Require object creation
- **Module-level functions**: Harder to discover
- **Separate introspection class**: Extra indirection

**Trade-offs**:
- ✅ Clean API, easy to use
- ✅ Efficient (no instances needed)
- ✅ Cacheable results
- ⚠️ Need to handle inheritance correctly

---

### Decision 4: Anti-Pattern Detection
**Chosen**: Static analysis + runtime checks

**Implementation**:
- AST parsing for static checks (HTTP, templates, etc.)
- Runtime introspection for dynamic checks
- CLI tool for validation (`validate_models.py`)
- Optional pre-commit hook

**Rationale**:
- Catches issues early in development
- Provides actionable error messages
- Can be integrated into CI/CD
- Doesn't slow down runtime

**Detection Rules**:
1. **HTTP Handling**: Detect `request` parameters, HTTP library imports
2. **Template Rendering**: Detect template engine calls, HTML string building
3. **External Services**: Detect API client usage, email sending
4. **UI Logic**: Detect JavaScript/CSS strings, form building

**Alternatives Considered**:
- **Runtime-only**: Catches issues too late
- **Linting-only**: May miss dynamic patterns
- **No validation**: Relies on code review

**Trade-offs**:
- ✅ Catches issues early
- ✅ Educational for developers
- ✅ Enforces consistency
- ⚠️ May have false positives (allow-list needed)

---

### Decision 5: Migration Strategy
**Chosen**: Opt-in with gradual migration

**Phases**:
1. **Phase 1**: Introduce ActiveRecord mixin, document pattern
2. **Phase 2**: Migrate one model (Post) as pilot
3. **Phase 3**: Migrate remaining models incrementally
4. **Phase 4**: Make pattern required for new models
5. **Phase 5**: Eventually require for all models

**Rationale**:
- Minimizes risk of breaking changes
- Allows learning from pilot migration
- Gives team time to adapt
- Can be rolled back if issues arise

**Alternatives Considered**:
- **Big bang migration**: Too risky, hard to debug
- **Feature flag**: Adds complexity, hard to maintain
- **New project only**: Leaves old code unmaintained

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────┐
│              Application Models                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Post   │  │   User   │  │ Comment  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │              │             │
└───────┼─────────────┼──────────────┼─────────────┘
        │             │              │
        ├─────────────┴──────────────┘
        │
        ↓
┌──────────────────────────────────────────────────┐
│           ActiveRecord Mixin                      │
│  ┌────────────────────────────────────────────┐  │
│  │  Introspection API                         │  │
│  │  - get_attributes()                        │  │
│  │  - get_methods()                           │  │
│  │  - get_ui_overrides()                      │  │
│  │  - get_validators()                        │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Decorator Registry                        │  │
│  │  - @validates                              │  │
│  │  - @ui_override                            │  │
│  │  - @computed_field                         │  │
│  │  - @requires_permission                    │  │
│  └────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────┐  │
│  │  Pattern Validation                        │  │
│  │  - validate_pattern()                      │  │
│  │  - check_anti_patterns()                   │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
        │
        ├──────────────┬─────────────────┐
        ↓              ↓                 ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Auto-UI    │  │  Validation │  │    CLI      │
│  Generator  │  │   Engine    │  │  Tool       │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Class Diagram

```python
class ActiveRecord:
    """Mixin for Active Record pattern."""
    
    # Introspection API
    @classmethod
    def get_attributes(cls) -> Dict[str, FieldInfo]:
        """Return all database field definitions."""
        pass
    
    @classmethod
    def get_methods(cls) -> List[MethodInfo]:
        """Return all business logic methods."""
        pass
    
    @classmethod
    def get_ui_overrides(cls) -> Dict[str, UIOverride]:
        """Return all UI widget overrides."""
        pass
    
    @classmethod
    def get_validators(cls) -> Dict[str, List[Validator]]:
        """Return all field validators."""
        pass
    
    # Pattern validation
    @classmethod
    def validate_pattern(cls) -> List[PatternViolation]:
        """Check for anti-patterns."""
        pass
    
    # Decorator support
    @classmethod
    def _register_decorator(cls, type: str, name: str, func: Callable):
        """Register a decorator in the registry."""
        pass


# Example usage
class Post(Model, ActiveRecord):
    # Attributes
    title = Field.string()
    content = Field.text()
    
    # Attribute decorators
    @validates('title')
    def validate_title(self, value):
        return len(value) >= 3
    
    # UI overrides
    @ui_override(field='content', widget='rich_text')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic']}
    
    # Methods
    def publish(self):
        self.published = True
        return self.save()
    
    # Method decorators
    @requires_permission('admin')
    def delete_permanently(self):
        return self.destroy()
```

---

## Data Structures

### FieldInfo
```python
@dataclass
class FieldInfo:
    name: str
    field_type: Type
    required: bool
    default: Any
    constraints: Dict[str, Any]
```

### MethodInfo
```python
@dataclass
class MethodInfo:
    name: str
    signature: inspect.Signature
    decorators: List[str]
    docstring: str
```

### UIOverride
```python
@dataclass
class UIOverride:
    field: str
    widget: str
    config: Dict[str, Any]
    conditional: bool  # Whether config depends on instance
```

### Validator
```python
@dataclass
class Validator:
    field: str
    func: Callable
    error_message: str
    client_side: bool  # Can be expressed in HTML5 validation
```

---

## Implementation Details

### Decorator Registry

```python
class ActiveRecord:
    _decorators = {
        'validators': {},
        'ui_overrides': {},
        'computed_fields': {},
        'permissions': {},
    }
    
    @classmethod
    def _register_decorator(cls, category, name, func):
        if cls.__name__ not in cls._decorators[category]:
            cls._decorators[category][cls.__name__] = {}
        cls._decorators[category][cls.__name__][name] = func
```

### Introspection Caching

```python
class ActiveRecord:
    _introspection_cache = {}
    
    @classmethod
    def get_attributes(cls):
        cache_key = (cls.__name__, 'attributes')
        if cache_key not in cls._introspection_cache:
            cls._introspection_cache[cache_key] = cls._introspect_attributes()
        return cls._introspection_cache[cache_key]
```

### Anti-Pattern Detection

```python
def check_anti_patterns(model_class):
    violations = []
    
    # Check for HTTP handling
    for name, method in inspect.getmembers(model_class, inspect.isfunction):
        sig = inspect.signature(method)
        if 'request' in sig.parameters:
            violations.append(PatternViolation(
                type='http_handling',
                location=f'{model_class.__name__}.{name}',
                message='Models should not handle HTTP requests',
                suggestion='Move to controller or service layer'
            ))
    
    # Check for template rendering
    source = inspect.getsource(model_class)
    if 'render_template' in source or '<html' in source:
        violations.append(PatternViolation(
            type='template_rendering',
            location=model_class.__name__,
            message='Models should not render templates',
            suggestion='Use views or serializers'
        ))
    
    return violations
```

---

## Performance Considerations

### Caching Strategy
- **Class-level introspection**: Cached indefinitely (class definition doesn't change at runtime)
- **Instance-level UI config**: Not cached (depends on instance state)
- **Validation results**: Not cached (depends on data)

### Overhead Analysis
- **Introspection**: O(1) after first call (cached)
- **Decorator registration**: O(1) per decorator (done at class definition time)
- **Pattern validation**: O(n) where n = number of methods (only run in dev/CI)

### Optimization Opportunities
- Pre-compute introspection at startup
- Lazy load decorators only when needed
- Skip validation in production builds

---

## Security Considerations

### Permission Decorators
- Must check current user context
- Should fail closed (deny by default)
- Log unauthorized access attempts

### Validation Decorators
- Never trust client-side validation alone
- Always run server-side validators
- Sanitize error messages (no stack traces to users)

### UI Overrides
- Validate widget names against allow-list
- Sanitize widget configuration (no arbitrary code execution)
- Escape user data in widget config

---

## Testing Strategy

### Unit Tests
- Test each decorator independently
- Test introspection API methods
- Test anti-pattern detection
- Test caching behavior

### Integration Tests
- Test complete model lifecycle
- Test auto-UI generation with Active Record
- Test validation integration
- Test permission enforcement

### Example Test

```python
def test_active_record_introspection():
    """Test that ActiveRecord provides correct introspection."""
    
    class TestModel(Model, ActiveRecord):
        name = Field.string()
        
        @validates('name')
        def validate_name(self, value):
            return len(value) > 0
    
    # Test attributes
    attrs = TestModel.get_attributes()
    assert 'name' in attrs
    assert attrs['name'].field_type == str
    
    # Test validators
    validators = TestModel.get_validators()
    assert 'name' in validators
    assert len(validators['name']) == 1
    
    # Test pattern validation
    violations = TestModel.validate_pattern()
    assert len(violations) == 0  # No anti-patterns
```

---

## Migration Plan

### Phase 1: Foundation (Week 1)
**Deliverables**:
- ActiveRecord mixin implemented
- Decorator infrastructure complete
- Basic introspection API working
- Documentation written

**Success Criteria**:
- All tests pass
- Pilot model (Post) migrated successfully
- Team trained on pattern

**Rollback**: Remove ActiveRecord, revert pilot model

---

### Phase 2: Integration (Week 2)
**Deliverables**:
- Auto-UI generator updated
- Pattern validation CLI tool
- All models migrated
- Integration tests passing

**Success Criteria**:
- Auto-UI generation works with ActiveRecord
- No anti-patterns detected
- All existing tests pass

**Rollback**: Use feature flag to disable ActiveRecord

---

### Phase 3: Enforcement (Week 3)
**Deliverables**:
- Pre-commit hook for pattern validation
- CI/CD integration
- Code review checklist
- Pattern required for new code

**Success Criteria**:
- Pattern violations caught in CI
- No new anti-patterns introduced
- Team comfortable with pattern

**Rollback**: Disable pre-commit hook, make pattern optional

---

## Risks / Trade-offs

### Risk: Breaking Existing Code
**Mitigation**:
- Opt-in initially (non-breaking)
- Comprehensive test suite
- Gradual migration
- Feature flag for rollback

**Impact**: Medium  
**Likelihood**: Low

---

### Risk: Developer Resistance
**Mitigation**:
- Clear documentation with examples
- Training sessions
- Migrate one model as pilot
- Gather feedback and iterate

**Impact**: High (adoption failure)  
**Likelihood**: Medium

---

### Risk: Performance Overhead
**Mitigation**:
- Cache introspection results
- Lazy load decorators
- Skip validation in production
- Profile before/after

**Impact**: Low  
**Likelihood**: Low

---

### Trade-off: Flexibility vs Consistency
**Decision**: Favor consistency

**Rationale**:
- Codebase maintainability more important than individual flexibility
- Clear patterns reduce cognitive load
- Easier onboarding for new developers
- Can add exceptions if needed

---

## Open Questions

1. **Should we enforce Active Record for ALL models eventually?**
   - Recommendation: Yes, but allow 6-month migration period
   
2. **How strict should anti-pattern detection be?**
   - Recommendation: Warnings initially, errors after 1 month
   
3. **Should UI overrides be in models or separate files?**
   - Recommendation: In models (metadata, not logic)
   
4. **How to handle edge cases (e.g., models with no UI)?**
   - Recommendation: ActiveRecord optional for non-UI models

---

## References

- Martin Fowler's Active Record pattern: https://martinfowler.com/eaaCatalog/activeRecord.html
- Django Model design patterns
- Rails ActiveRecord documentation
- Emmett ORM documentation

---

## Appendix: Example Models

### Before Active Record

```python
class Post(Model):
    title = Field.string()
    content = Field.text()
    
    def render_preview(self):  # Anti-pattern: presentation logic
        return f"<div class='post'><h2>{self.title}</h2></div>"
    
    def create_from_request(request):  # Anti-pattern: HTTP handling
        title = request.vars.title
        return Post.create(title=title)
```

### After Active Record

```python
class Post(Model, ActiveRecord):
    # Attributes
    title = Field.string()
    content = Field.text()
    published = Field.bool(default=False)
    
    # Attribute decorators
    @validates('title')
    def validate_title(self, value):
        if len(value) < 3:
            return "Title must be at least 3 characters"
    
    @computed_field
    def excerpt(self):
        return self.content[:100] + "..."
    
    # UI overrides
    @ui_override(field='content', widget='rich_text_editor')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic', 'link']}
    
    # Methods (domain logic only)
    def publish(self):
        """Publish the post."""
        self.published = True
        self.published_at = datetime.now()
        return self.save()
    
    def can_edit(self, user):
        """Check if user can edit."""
        return user.is_admin() or self.user_id == user.id
    
    # Method decorators
    @requires_permission('admin')
    def delete_permanently(self):
        """Permanently delete (admin only)."""
        return self.destroy()
```

---

**Design Status**: Ready for implementation  
**Last Updated**: 2025-10-12  
**Author**: OpenSpec AI Agent

