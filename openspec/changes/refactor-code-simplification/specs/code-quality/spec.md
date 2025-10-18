## ADDED Requirements

### Requirement: Model Consolidation Pattern
All models SHALL follow the Active Record pattern with a single `model.py` file containing model definition, routes, REST API setup, and a `setup(app)` function.

#### Scenario: Model structure consistency
- **WHEN** reviewing any model directory in `models/`
- **THEN** it SHALL contain only `__init__.py` and `model.py` files
- **AND** `model.py` SHALL contain the model class, routes, REST API, and `setup()` function
- **AND** there SHALL NOT be separate `api.py` or `views.py` files

#### Scenario: Permission model consolidation
- **WHEN** reviewing the Permission model at `models/permission/`
- **THEN** it SHALL follow the Active Record pattern
- **AND** previous `api.py` and `views.py` SHALL be merged into `model.py`

#### Scenario: Role model consolidation  
- **WHEN** reviewing the Role model at `models/role/`
- **THEN** it SHALL follow the Active Record pattern
- **AND** previous `api.py` and `views.py` SHALL be merged into `model.py`

### Requirement: Test Utility Organization
Test-only utilities SHALL be located in the `tests/` directory, not in production code directories.

#### Scenario: Test helpers location
- **WHEN** a utility file is used exclusively in test code
- **THEN** it SHALL be located in `tests/helpers/` directory
- **AND** it SHALL NOT be located in `runtime/` directory

#### Scenario: Chrome test helpers relocation
- **WHEN** reviewing `playwright_helpers.py`
- **THEN** it SHALL be located at `tests/helpers/chrome_helpers.py`
- **AND** it SHALL NOT exist in `runtime/` directory

#### Scenario: Model factory relocation
- **WHEN** reviewing `model_factory.py`
- **THEN** it SHALL be located at `tests/helpers/factories.py` (if test-only)
- **OR** remain in `runtime/` if used in production code

### Requirement: Code Complexity Limits
Code SHALL be maintainable with enforced complexity limits to ensure readability and maintainability.

#### Scenario: File size limit
- **WHEN** reviewing any Python file
- **THEN** it SHOULD NOT exceed 500 lines of code
- **AND** if it does, it SHOULD be split into logical modules

#### Scenario: Function size limit
- **WHEN** reviewing any function or method
- **THEN** it SHOULD NOT exceed 50 lines of code
- **AND** complex functions SHOULD be refactored into smaller helpers

#### Scenario: Import complexity
- **WHEN** reviewing any module's imports
- **THEN** unused imports SHALL be removed
- **AND** imports SHALL be grouped (stdlib, third-party, local)
- **AND** imports SHALL be sorted alphabetically within groups

### Requirement: Dead Code Elimination
Code that is not used SHALL be removed to reduce maintenance burden and cognitive load.

#### Scenario: Unused function removal
- **WHEN** a function has zero call sites in the codebase
- **AND** it is not part of a public API
- **AND** it is not referenced in documentation
- **THEN** it SHALL be removed

#### Scenario: Unused class removal
- **WHEN** a class has zero instantiations in the codebase
- **AND** it is not part of a public API  
- **AND** it is not referenced in documentation
- **THEN** it SHALL be removed

#### Scenario: Dead code verification
- **WHEN** removing potentially unused code
- **THEN** a thorough search for usages MUST be performed
- **AND** test suite MUST pass after removal
- **AND** rationale for removal MUST be documented

### Requirement: Module Consolidation
Related utilities SHALL be consolidated into cohesive modules to reduce file proliferation.

#### Scenario: Token utility consolidation
- **WHEN** `auth/tokens.py` and `auth/token_refresh.py` have overlapping concerns
- **THEN** they SHOULD be consolidated into a single `auth/tokens.py` module
- **AND** all token-related functionality SHALL be in one place

#### Scenario: OAuth provider simplification
- **WHEN** OAuth providers have duplicate code patterns
- **THEN** common patterns SHALL be extracted to `auth/providers/base.py`
- **AND** individual providers SHALL contain only provider-specific configuration and overrides

#### Scenario: Utility evaluation criteria
- **WHEN** evaluating whether to keep a utility file
- **THEN** it MUST be used in production code, OR
- **THEN** it MUST be a documented development tool, OR
- **THEN** it SHOULD be moved to `tests/` if test-only, OR
- **THEN** it SHOULD be removed if unused

### Requirement: Documentation Currency
Documentation SHALL accurately reflect the current codebase structure and organization.

#### Scenario: Model documentation updates
- **WHEN** model structure changes
- **THEN** `models/README.md` SHALL be updated to reflect the changes
- **AND** examples SHALL match the actual code structure

#### Scenario: Project structure documentation
- **WHEN** files are moved, renamed, or removed
- **THEN** `openspec/project.md` SHALL be updated
- **AND** `AGENTS.md` SHALL be updated if it references changed files
- **AND** a summary document SHALL document all changes

#### Scenario: Code organization guide
- **WHEN** simplification refactoring is complete
- **THEN** a `documentation/code_organization.md` file SHALL exist
- **AND** it SHALL document the rationale for the structure
- **AND** it SHALL provide guidance for future additions

### Requirement: Refactoring Safety
All refactoring MUST preserve existing functionality and test coverage.

#### Scenario: Test preservation
- **WHEN** any refactoring change is made
- **THEN** all existing tests MUST still pass
- **AND** test coverage MUST NOT decrease
- **AND** tests MUST be run after each significant change

#### Scenario: Functionality preservation  
- **WHEN** code is moved, merged, or removed
- **THEN** all external APIs MUST remain functional
- **AND** all routes MUST remain accessible
- **AND** all REST API endpoints MUST work identically

#### Scenario: Incremental changes with rollback
- **WHEN** implementing simplification changes
- **THEN** changes SHALL be made in small increments
- **AND** each increment SHALL be committed separately
- **AND** each commit SHALL be revertible independently

### Requirement: Metrics Tracking
Simplification improvements SHALL be measurable with quantifiable metrics.

#### Scenario: File count reduction
- **WHEN** simplification is complete
- **THEN** total file count in `runtime/` SHALL be reduced by at least 20%
- **AND** reduction SHALL be documented with before/after counts

#### Scenario: Code count reduction
- **WHEN** simplification is complete  
- **THEN** total function and class count SHALL be reduced by at least 10%
- **AND** this SHALL be achieved through consolidation and dead code removal
- **AND** NOT by removing required functionality

#### Scenario: Complexity metrics
- **WHEN** measuring refactoring success
- **THEN** metrics SHALL include: file count, function count, lines of code, test coverage
- **AND** all metrics SHALL be documented in `SIMPLIFICATION_SUMMARY.md`
- **AND** summary SHALL explain rationale for all changes

