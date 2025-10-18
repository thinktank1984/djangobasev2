# Implementation Tasks: Code Simplification Refactoring

## Overview
Systematic review and simplification of codebase to eliminate redundancy and unnecessary complexity while maintaining all functionality.

---

## Phase 1: Analysis and Discovery (2 hours)

### Task 1.1: Generate Dependency Map
- [ ] 1.1.1 Create script to analyze all imports across codebase
- [ ] 1.1.2 Generate dependency graph visualization
- [ ] 1.1.3 Identify circular dependencies (if any)
- [ ] 1.1.4 Document findings in `SIMPLIFICATION_ANALYSIS.md`

**Command:**
```bash
cd runtime
grep -r "^import \|^from " *.py models/**/*.py auth/**/*.py > imports.txt
python -c "import ast; # analyze imports"
```

### Task 1.2: Find Unused Code
- [ ] 1.2.1 Search for unused function definitions
- [ ] 1.2.2 Search for unused class definitions
- [ ] 1.2.3 Identify functions/classes with zero call sites
- [ ] 1.2.4 Document candidates for removal

**Tools:** `vulture`, `grep`, manual review

### Task 1.3: Identify Duplicate Code
- [ ] 1.3.1 Find similar functions across files
- [ ] 1.3.2 Identify duplicate validation logic
- [ ] 1.3.3 Find similar route patterns
- [ ] 1.3.4 Document consolidation opportunities

**Tools:** `pylint`, manual diff review

### Task 1.4: Review Test Coverage
- [ ] 1.4.1 Run coverage report for all files
- [ ] 1.4.2 Identify utility files with no test coverage
- [ ] 1.4.3 Identify test-only utilities in wrong location
- [ ] 1.4.4 Document test coverage gaps

**Command:**
```bash
pytest --cov=runtime --cov-report=html
open htmlcov/index.html
```

---

## Phase 2: Complete Model Consolidation (3 hours)

### Task 2.1: Consolidate Permission Model
- [ ] 2.1.1 Read current `models/permission/model.py`
- [ ] 2.1.2 Read current `models/permission/api.py`
- [ ] 2.1.3 Read current `models/permission/views.py`
- [ ] 2.1.4 Merge api.py content into model.py
- [ ] 2.1.5 Merge views.py content into model.py
- [ ] 2.1.6 Create `setup(app)` function in model.py
- [ ] 2.1.7 Update `models/permission/__init__.py` exports
- [ ] 2.1.8 Delete `api.py` and `views.py`
- [ ] 2.1.9 Test: Run all permission-related tests

**Files:**
- `runtime/models/permission/model.py` (modify)
- `runtime/models/permission/api.py` (delete)
- `runtime/models/permission/views.py` (delete)
- `runtime/models/permission/__init__.py` (update)

**Test Command:**
```bash
pytest tests.py -k permission -v
```

### Task 2.2: Consolidate Role Model
- [ ] 2.2.1 Read current `models/role/model.py`
- [ ] 2.2.2 Read current `models/role/api.py`
- [ ] 2.2.3 Read current `models/role/views.py`
- [ ] 2.2.4 Merge api.py content into model.py
- [ ] 2.2.5 Merge views.py content into model.py
- [ ] 2.2.6 Create `setup(app)` function in model.py
- [ ] 2.2.7 Update `models/role/__init__.py` exports
- [ ] 2.2.8 Delete `api.py` and `views.py`
- [ ] 2.2.9 Test: Run all role-related tests

**Files:**
- `runtime/models/role/model.py` (modify)
- `runtime/models/role/api.py` (delete)
- `runtime/models/role/views.py` (delete)
- `runtime/models/role/__init__.py` (update)

**Test Command:**
```bash
pytest tests.py -k role -v
```

### Task 2.3: Update Model Package Initialization
- [ ] 2.3.1 Update `models/__init__.py` to include Permission and Role in `setup_all()`
- [ ] 2.3.2 Verify all model imports still work
- [ ] 2.3.3 Test: Import all models from top level

**Test Command:**
```bash
cd runtime
python -c "from models import Permission, Role, setup_all; print('✓ OK')"
```

---

## Phase 3: Test Utility Relocation (2 hours)

### Task 3.1: Move Test-Only Utilities
- [ ] 3.1.1 Create `tests/helpers/` directory
- [ ] 3.1.2 Move `runtime/playwright_helpers.py` → `tests/helpers/playwright_helpers.py`
- [ ] 3.1.3 Move `runtime/model_factory.py` → `tests/helpers/factories.py`
- [ ] 3.1.4 Update all test imports
- [ ] 3.1.5 Test: Run full test suite

**Files to Move:**
- `runtime/playwright_helpers.py` → `tests/helpers/playwright_helpers.py`
- `runtime/model_factory.py` → `tests/helpers/factories.py`

**Files to Update:**
- All test files with imports from these modules

**Test Command:**
```bash
pytest tests/ -v
```

### Task 3.2: Review Remaining Utilities
- [ ] 3.2.1 Audit `base_model.py` - Is it used? By what?
- [ ] 3.2.2 Audit `validate_models.py` - Dev tool only? Keep as is?
- [ ] 3.2.3 Audit `model_permissions.py` - Can it merge into base_model?
- [ ] 3.2.4 Document decisions in `SIMPLIFICATION_ANALYSIS.md`

**Decision Criteria:**
- Used in production code? → Keep in runtime/
- Used only in tests? → Move to tests/
- Dev tool only? → Keep but mark as dev-only
- Unused? → Remove after verification

---

## Phase 4: Auth Module Simplification (3 hours)

### Task 4.1: Consolidate Token Utilities
- [ ] 4.1.1 Read `auth/tokens.py` 
- [ ] 4.1.2 Read `auth/token_refresh.py`
- [ ] 4.1.3 Identify overlapping functionality
- [ ] 4.1.4 Merge `token_refresh.py` into `tokens.py` (if beneficial)
- [ ] 4.1.5 Update imports in `app.py` and other files
- [ ] 4.1.6 Delete redundant file (if merged)
- [ ] 4.1.7 Test: Run OAuth tests

**Files:**
- `runtime/auth/tokens.py` (potentially expand)
- `runtime/auth/token_refresh.py` (potentially delete)

**Test Command:**
```bash
pytest tests/test_oauth_real.py -v
```

### Task 4.2: Simplify OAuth Providers
- [ ] 4.2.1 Review all provider files for duplicate patterns
- [ ] 4.2.2 Extract common code to `base.py`
- [ ] 4.2.3 Simplify each provider to config + overrides only
- [ ] 4.2.4 Update provider implementations
- [ ] 4.2.5 Test: Verify all OAuth flows still work

**Files:**
- `runtime/auth/providers/base.py` (enhance with common patterns)
- `runtime/auth/providers/google.py` (simplify)
- `runtime/auth/providers/github.py` (simplify)
- `runtime/auth/providers/facebook.py` (simplify)
- `runtime/auth/providers/microsoft.py` (simplify)

**Test Command:**
```bash
pytest tests/test_oauth_real.py -v
```

### Task 4.3: Document Auth Module Structure
- [ ] 4.3.1 Update `runtime/documentation/OAUTH_SETUP.md` if changed
- [ ] 4.3.2 Add comments to simplified code
- [ ] 4.3.3 Document provider extension pattern

---

## Phase 5: Import Cleanup (1 hour)

### Task 5.1: Remove Unused Imports
- [ ] 5.1.1 Run linter to find unused imports in `app.py`
- [ ] 5.1.2 Remove unused imports from `app.py`
- [ ] 5.1.3 Run linter on all model files
- [ ] 5.1.4 Remove unused imports from models
- [ ] 5.1.5 Test: Full test suite

**Tool:**
```bash
autoflake --remove-all-unused-imports --in-place runtime/**/*.py
```

### Task 5.2: Simplify Import Statements
- [ ] 5.2.1 Group related imports in `app.py`
- [ ] 5.2.2 Sort imports alphabetically
- [ ] 5.2.3 Use `isort` for consistency
- [ ] 5.2.4 Verify code still works

**Tool:**
```bash
isort runtime/*.py runtime/**/*.py
```

---

## Phase 6: Dead Code Removal (2 hours)

### Task 6.1: Remove Unused Functions
- [ ] 6.1.1 Review `SIMPLIFICATION_ANALYSIS.md` for unused functions
- [ ] 6.1.2 Verify each function has zero call sites
- [ ] 6.1.3 Remove unused functions one at a time
- [ ] 6.1.4 Test after each removal
- [ ] 6.1.5 Document what was removed and why

**Safety:** Only remove if:
- Zero usages found in codebase
- Not part of public API
- Not used in templates
- Not referenced in documentation as example

### Task 6.2: Remove Unused Classes
- [ ] 6.2.1 Review `SIMPLIFICATION_ANALYSIS.md` for unused classes
- [ ] 6.2.2 Verify each class has zero instantiations
- [ ] 6.2.3 Remove unused classes one at a time
- [ ] 6.2.4 Test after each removal
- [ ] 6.2.5 Document what was removed and why

### Task 6.3: Simplify Complex Methods
- [ ] 6.3.1 Find methods over 50 lines
- [ ] 6.3.2 Refactor to extract helper methods
- [ ] 6.3.3 Improve readability
- [ ] 6.3.4 Test after each simplification

**Target:** All functions under 50 lines

---

## Phase 7: Documentation and Validation (1 hour)

### Task 7.1: Update Documentation
- [ ] 7.1.1 Update `models/README.md` with final structure
- [ ] 7.1.2 Update `AGENTS.md` file structure references
- [ ] 7.1.3 Create `documentation/code_organization.md`
- [ ] 7.1.4 Update `openspec/project.md` structure section
- [ ] 7.1.5 Document all changes in `SIMPLIFICATION_SUMMARY.md`

### Task 7.2: Final Validation
- [ ] 7.2.1 Run complete test suite
- [ ] 7.2.2 Verify all 83+ tests pass
- [ ] 7.2.3 Run linter on all files
- [ ] 7.2.4 Generate coverage report
- [ ] 7.2.5 Compare before/after metrics

**Test Command:**
```bash
pytest tests/ tests.py -v --cov=runtime --cov-report=html
```

### Task 7.3: Metrics Collection
- [ ] 7.3.1 Count files before and after
- [ ] 7.3.2 Count functions/classes before and after
- [ ] 7.3.3 Measure test coverage before and after
- [ ] 7.3.4 Document improvements in proposal

**Metrics to Track:**
- Total files in runtime/
- Total functions/classes
- Lines of code
- Test coverage percentage
- Import complexity (number of imports)

---

## Testing Checkpoints

### After Each Phase
```bash
# Quick validation
pytest tests/ -x  # Stop on first failure

# Full test suite
pytest tests/ tests.py -v

# Coverage check
pytest --cov=runtime --cov-report=term-missing
```

### Before Committing
```bash
# All tests pass
pytest tests/ tests.py -v

# No linter errors
ruff check runtime/

# Imports clean
isort --check runtime/

# Documentation updated
ls documentation/code_organization.md
```

---

## Success Metrics

| Metric | Before | Target | After |
|--------|--------|--------|-------|
| Files in runtime/ | ~38 | ~30 | TBD |
| Functions/Classes | ~127 | ~115 | TBD |
| Tests Passing | 83 | 83 | TBD |
| Test Coverage | Current% | ≥Current% | TBD |
| Models Consolidated | 3/5 | 5/5 | TBD |

---

## Rollback Plan

### Per-Phase Rollback
```bash
# After each phase, commit with descriptive message
git add -A
git commit -m "Phase N: [description]"

# If issues found, rollback that phase
git revert HEAD
```

### Full Rollback
```bash
# Revert all changes
git log --oneline | grep "refactor-code-simplification"
git revert <commit-hash>..HEAD
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Break existing functionality | Test after every change; commit frequently |
| Remove needed code | Thorough analysis before removal; keep analysis doc |
| Import errors | Update all imports immediately after moves |
| Test failures | Fix immediately or rollback change |

---

## Deliverables

- [ ] All models follow consistent Active Record pattern (5/5 models)
- [ ] Test utilities moved to tests/ directory
- [ ] Auth module simplified (2-3 fewer files)
- [ ] Dead code removed (functions/classes with zero usage)
- [ ] Imports cleaned up across codebase
- [ ] Documentation updated to reflect new structure
- [ ] `SIMPLIFICATION_SUMMARY.md` with before/after metrics
- [ ] All 83+ tests still passing
- [ ] No reduction in test coverage

---

**Estimated Total Time:** 14 hours over 3-4 days  
**Status:** Ready for implementation  
**Priority:** Medium (improves maintainability, not urgent)

