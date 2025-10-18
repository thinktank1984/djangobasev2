# Type Checking Design Document

## Context

The project currently has no static type checking or type annotations, which makes it harder to catch bugs early, limits IDE support, and reduces code maintainability. This design document outlines the approach for adding comprehensive type checking using MonkeyType for automatic type inference and Pyright for static type checking.

### Background

- The codebase is Python 3.9+ (3.13+ recommended)
- Uses Emmett framework (2.5.0+) which may have limited type stub support
- pyDAL ORM may not have comprehensive type stubs
- Need to maintain backward compatibility (type hints are backward compatible)
- Must work in Docker environment

### Constraints

- Type hints must not break existing functionality
- Must be easy to run for developers (both in Docker and locally)
- Should not significantly slow down development
- Must handle dynamic nature of Emmett and pyDAL

## Goals / Non-Goals

### Goals

- Add comprehensive type annotations to all Python code
- Enable static type checking in development workflow
- Improve IDE support and auto-completion
- Catch type-related bugs before runtime
- Make codebase more maintainable and self-documenting
- Integrate type checking into development scripts and Docker

### Non-Goals

- Achieving 100% type coverage immediately (progressive enhancement is fine)
- Rewriting code to be more type-friendly if it breaks Emmett patterns
- Adding type stubs for third-party libraries without stubs
- Making type checking mandatory for all new code (can be gradual)
- Supporting Python versions below 3.9

## Decisions

### Decision 1: Use MonkeyType for Initial Type Inference

**What**: Use MonkeyType to automatically generate type annotations from runtime traces.

**Why**: 
- Saves significant manual effort in adding initial type hints
- Provides data-driven type annotations based on actual usage
- Particularly useful for dynamically-typed frameworks like Emmett
- Can capture complex types that would be tedious to write manually

**Alternatives Considered**:
- **Manual annotation**: Too time-consuming and error-prone for large codebase
- **PyAnnotate**: Less actively maintained than MonkeyType
- **Pyre**: Requires Facebook's type system, overkill for this project

**Implementation**:
1. Install MonkeyType: `uv pip install monkeytype`
2. Run tests and application with MonkeyType tracing: `python -m monkeytype run pytest tests.py`
3. Generate stubs: `monkeytype stub module_name`
4. Apply annotations: `monkeytype apply module_name`

### Decision 2: Use Pyright as Type Checker

**What**: Use Pyright (Microsoft's fast Python type checker) instead of mypy.

**Why**:
- Significantly faster than mypy (written in TypeScript/Node.js)
- Better error messages
- Excellent IDE integration (VS Code uses Pyright internally)
- Active development and good community support
- Better handling of complex generic types

**Alternatives Considered**:
- **mypy**: Slower, more established but less developer-friendly errors
- **Pyre**: Requires Facebook's infrastructure, less portable
- **pytype**: Google's type checker, slower and less IDE integration

**Configuration** (`setup/pyrightconfig.json`):
```json
{
  "include": ["runtime", "tests"],
  "exclude": [
    "runtime/migrations",
    "**/__pycache__",
    "**/node_modules",
    "runtime/databases"
  ],
  "pythonVersion": "3.9",
  "pythonPlatform": "All",
  "typeCheckingMode": "basic",
  "reportMissingImports": "warning",
  "reportMissingTypeStubs": "none",
  "reportUnknownMemberType": "none",
  "reportUnknownArgumentType": "none",
  "reportUnknownVariableType": "none",
  "reportGeneralTypeIssues": "warning"
}
```

**Rationale for settings**:
- Start with "basic" mode to avoid overwhelming errors
- Set dynamic framework issues to "none" initially
- Can progressively increase strictness over time
- Focus on catching actual bugs, not pedantic type issues

### Decision 3: Progressive Type Coverage Strategy

**What**: Implement type checking progressively, not all at once.

**Why**:
- Reduces risk of breaking changes
- Allows team to learn type annotation best practices
- Easier to review and validate changes
- Can identify and fix issues incrementally

**Implementation Order**:
1. **Phase 1**: Core application files (app.py, base_model.py)
2. **Phase 2**: Models (models/*.py)
3. **Phase 3**: Authentication modules (auth/*.py)
4. **Phase 4**: Utility modules (auto_ui_generator.py, openapi_generator.py, etc.)
5. **Phase 5**: Test files
6. **Phase 6**: Increase Pyright strictness gradually

### Decision 4: Handling Emmett and pyDAL Dynamic Types

**What**: Use strategic type: ignore comments and Protocol types for dynamic framework features.

**Why**:
- Emmett and pyDAL are dynamically typed frameworks
- Some features (like ORM magic methods) are hard to type correctly
- Better to have some types with selective ignores than no types at all

**Strategy**:
- Use `type: ignore[attr-defined]` for ORM field access (e.g., `post.title`)
- Use `Any` type for highly dynamic objects (like request, response)
- Create Protocol classes for common interfaces where beneficial
- Add comments explaining why type: ignore is used

**Example**:
```python
from typing import Protocol, Any

class EmmetRequest(Protocol):
    method: str
    vars: dict[str, Any]
    # ... other common attributes

# In route handler
async def show_post(post_id: int) -> dict[str, Any]:
    post = Post.get(post_id)  # type: ignore[attr-defined]
    return {"post": post}
```

### Decision 5: Integration with Development Workflow

**What**: Add type checking to Docker development environment and provide easy-to-use scripts.

**Why**:
- Docker is the primary development environment
- Must be easy to run to ensure adoption
- Should integrate with existing workflows

**Implementation**:
- Add to Dockerfile: `RUN pip install monkeytype pyright`
- Create `run_type_check.sh` script:
  ```bash
  #!/bin/bash
  docker compose -f docker/docker-compose.yaml exec runtime pyright
  ```
- Add to justfile (if used): `type-check: pyright`
- Document in AGENTS.md and README

### Decision 6: CI/CD Integration Strategy

**What**: Add type checking to CI/CD as a warning, not a blocker (initially).

**Why**:
- Prevents breaking existing development workflow
- Allows team to fix type errors progressively
- Can be upgraded to blocker once coverage is high

**Implementation**:
```yaml
# Example GitHub Actions step
- name: Type Check
  run: |
    docker compose -f docker/docker-compose.yaml exec runtime pyright
  continue-on-error: true  # Allow failures initially
```

## Risks / Trade-offs

### Risk 1: Type Annotations May Be Incorrect

**Risk**: MonkeyType-generated annotations may not cover all code paths or may infer overly specific types.

**Mitigation**:
- Manually review all generated annotations
- Run comprehensive tests with MonkeyType to maximize coverage
- Add manual annotations for edge cases
- Use union types for parameters that accept multiple types

### Risk 2: Performance Impact of Type Checking

**Risk**: Running Pyright on every file save could slow development.

**Mitigation**:
- Pyright is fast, typically <1 second for full project
- Can configure IDE to run on save or on demand
- Can run in background without blocking development

### Risk 3: Team Learning Curve

**Risk**: Developers unfamiliar with type hints may struggle initially.

**Mitigation**:
- Provide comprehensive documentation and examples
- Start with basic type checking mode
- Include common patterns in documentation
- Make type checking warnings, not errors initially

### Risk 4: Maintenance Burden

**Risk**: Type annotations require maintenance as code evolves.

**Mitigation**:
- Pyright catches outdated annotations automatically
- Type annotations often reveal design issues early
- Benefits outweigh maintenance cost for projects of this size

### Risk 5: Emmett/pyDAL Compatibility

**Risk**: Dynamic features of Emmett and pyDAL may be hard to type.

**Mitigation**:
- Use `type: ignore` strategically with comments
- Use `Any` type for highly dynamic objects
- Create Protocol types for common interfaces
- Contribute type stubs to upstream projects if needed

## Migration Plan

### Phase 1: Setup (Week 1)
1. Add tools to requirements and Docker
2. Configure Pyright
3. Test on sample file
4. Create documentation

### Phase 2: Core Files (Week 1-2)
1. Run MonkeyType on core files
2. Apply and refine annotations
3. Fix type errors
4. Review and test

### Phase 3: Models (Week 2-3)
1. Run MonkeyType on all models
2. Apply and refine annotations
3. Fix type errors
4. Review and test

### Phase 4: Remaining Code (Week 3-4)
1. Run MonkeyType on auth, utilities, tests
2. Apply and refine annotations
3. Fix type errors
4. Review and test

### Phase 5: Integration (Week 4)
1. Add to CI/CD
2. Update all documentation
3. Train team
4. Collect feedback

### Rollback Plan
If type checking causes significant issues:
1. Revert type annotations (Git revert)
2. Keep tools installed for future use
3. Review what went wrong
4. Plan better migration strategy
5. Type annotations are backward compatible, so removing them is safe

## Open Questions

1. **Q**: Should we use strict mode eventually or stay with basic mode?
   **A**: TBD - Start with basic, evaluate after 3 months of usage

2. **Q**: Should we enforce type checking in CI/CD from day one?
   **A**: TBD - Start as warning, make it blocking once we fix initial errors

3. **Q**: Do we need custom type stubs for Emmett/pyDAL?
   **A**: TBD - Evaluate after seeing what Pyright reports

4. **Q**: Should new code be required to have type hints?
   **A**: TBD - Add to code review checklist after initial migration

5. **Q**: How do we handle auto-generated code (migrations, etc.)?
   **A**: Exclude from type checking in pyrightconfig.json

