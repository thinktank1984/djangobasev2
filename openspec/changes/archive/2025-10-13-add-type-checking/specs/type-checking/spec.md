## ADDED Requirements

### Requirement: Static Type Checking

The project SHALL provide static type checking using Pyright to catch type-related bugs during development before runtime.

#### Scenario: Type check passes on valid code

- **WHEN** a developer runs `pyright` on the codebase
- **THEN** the type checker reports no errors for correctly typed code
- **AND** the process completes in less than 5 seconds for the full codebase

#### Scenario: Type check catches type errors

- **WHEN** a developer introduces code with type errors (e.g., passing string to function expecting int)
- **THEN** Pyright reports the error with file location and line number
- **AND** the error message clearly explains the type mismatch
- **AND** the error includes suggestions for fixing the issue

#### Scenario: Type check configuration

- **WHEN** the project is configured with `pyrightconfig.json`
- **THEN** type checking respects the include/exclude paths
- **AND** the strictness level is set appropriately for the project
- **AND** Emmett and pyDAL dynamic features are handled gracefully

### Requirement: Automatic Type Inference

The project SHALL use MonkeyType to automatically infer and generate type annotations from runtime traces.

#### Scenario: Collect type traces from tests

- **WHEN** a developer runs `python -m monkeytype run pytest tests.py`
- **THEN** MonkeyType collects type information from all test executions
- **AND** the traces are stored in the MonkeyType database
- **AND** test execution completes successfully

#### Scenario: Collect type traces from application

- **WHEN** a developer runs the application with MonkeyType tracing enabled
- **THEN** MonkeyType collects type information from all executed code paths
- **AND** the traces are stored in the MonkeyType database
- **AND** application runs normally without crashes

#### Scenario: Generate type annotations

- **WHEN** a developer runs `monkeytype stub module_name`
- **THEN** MonkeyType generates a .pyi stub file with inferred types
- **AND** the stub file contains function signatures with parameter and return types
- **AND** the types are based on observed runtime behavior

#### Scenario: Apply type annotations to source

- **WHEN** a developer runs `monkeytype apply module_name`
- **THEN** MonkeyType applies type annotations directly to the source file
- **AND** the annotations are inserted as proper PEP 484 type hints
- **AND** the code remains functionally identical

### Requirement: Type Annotations Coverage

All Python source files in `runtime/` and `tests/` SHALL have type annotations for functions, methods, and class attributes.

#### Scenario: Function has parameter and return type annotations

- **WHEN** a function is defined in the codebase
- **THEN** all parameters have type annotations
- **AND** the return type is annotated
- **AND** optional parameters use `Optional[Type]` or `Type | None` syntax

#### Scenario: Class attributes are typed

- **WHEN** a class is defined with attributes
- **THEN** class attributes have type annotations
- **AND** instance attributes are annotated in `__init__`
- **AND** property return types are annotated

#### Scenario: Complex types use appropriate annotations

- **WHEN** code uses dictionaries, lists, or other containers
- **THEN** generic types are used (e.g., `dict[str, int]`, `list[Post]`)
- **AND** union types are used for multiple possible types (e.g., `str | int`)
- **AND** Protocol types are used for structural subtyping where appropriate

### Requirement: Type Checking in Development Workflow

Developers SHALL have easy access to type checking tools through scripts and Docker commands.

#### Scenario: Run type check in Docker

- **WHEN** a developer runs `docker compose -f docker/docker-compose.yaml exec runtime pyright`
- **THEN** Pyright runs on the codebase inside the container
- **AND** results are displayed in the terminal
- **AND** the command exits with code 0 if no errors, non-zero if errors found

#### Scenario: Run type check with script

- **WHEN** a developer runs `./run_type_check.sh`
- **THEN** the script executes Pyright in the Docker container
- **AND** results are displayed in the terminal with color output
- **AND** the script provides clear feedback on pass/fail status

#### Scenario: IDE integration

- **WHEN** a developer opens the project in VS Code or PyCharm
- **THEN** the IDE automatically uses Pyright for type checking
- **AND** type errors are highlighted inline in the editor
- **AND** hover tooltips show inferred types for variables and functions

### Requirement: Handling Dynamic Framework Features

The type checking system SHALL gracefully handle dynamic features of Emmett and pyDAL frameworks.

#### Scenario: ORM field access with type ignore

- **WHEN** code accesses ORM model fields (e.g., `post.title`)
- **THEN** appropriate `type: ignore[attr-defined]` comments are used
- **AND** the comment includes an explanation of why it's needed
- **AND** the code still benefits from type checking for other parts

#### Scenario: Dynamic request/response objects

- **WHEN** code uses Emmett's request or response objects
- **THEN** they are typed as `Any` or with Protocol types
- **AND** common attributes are typed in Protocol definitions
- **AND** type checking provides value without being overly strict

#### Scenario: Type stubs for third-party libraries

- **WHEN** Pyright encounters libraries without type stubs (like Emmett internals)
- **THEN** `reportMissingTypeStubs` is set to "none" to avoid noise
- **AND** the project includes custom stub files for critical APIs if needed
- **AND** type checking focuses on application code, not framework internals

### Requirement: Type Checking Documentation

The project SHALL provide comprehensive documentation for type checking practices and workflows.

#### Scenario: Developer guide for type annotations

- **WHEN** a developer needs to add type hints to new code
- **THEN** the documentation provides clear examples of common patterns
- **AND** the guide explains how to handle Emmett-specific typing challenges
- **AND** best practices for type annotations are documented

#### Scenario: Running type checks

- **WHEN** a developer wants to run type checking
- **THEN** the README or AGENTS.md includes clear commands
- **AND** both Docker and local execution methods are documented
- **AND** troubleshooting common type errors is explained

#### Scenario: Type checking in code review

- **WHEN** code is submitted for review
- **THEN** the documentation explains expectations for type annotations
- **AND** reviewers know what to look for regarding type safety
- **AND** the project has clear guidelines on when `type: ignore` is acceptable

### Requirement: CI/CD Integration

Type checking SHALL be integrated into the continuous integration pipeline to catch type errors before merging.

#### Scenario: Type check runs on every commit

- **WHEN** code is pushed to the repository
- **THEN** the CI/CD pipeline runs Pyright on all code
- **AND** the build fails if critical type errors are found
- **AND** warnings are reported but don't fail the build (configurable)

#### Scenario: Type check results in CI report

- **WHEN** CI/CD completes the type checking step
- **THEN** the results are displayed in the build log
- **AND** errors are formatted for easy identification
- **AND** the line numbers and file paths are clickable in the CI interface

#### Scenario: Progressive type checking enforcement

- **WHEN** the project initially adds type checking
- **THEN** CI/CD allows type errors with warnings (continue-on-error: true)
- **AND** the team can progressively fix errors
- **AND** once baseline is clean, enforcement can be made strict

### Requirement: Type Checking Configuration

The project SHALL maintain a `pyrightconfig.json` file that configures Pyright behavior appropriately for the Emmett framework.

#### Scenario: Pyright configuration file exists

- **WHEN** Pyright is run in the project
- **THEN** it reads configuration from `pyrightconfig.json` in the project root
- **AND** the configuration specifies Python version (3.9+)
- **AND** include paths cover runtime/ and tests/
- **AND** exclude paths omit migrations, __pycache__, databases, node_modules

#### Scenario: Type checking mode is appropriate

- **WHEN** Pyright analyzes the code
- **THEN** it uses "basic" mode initially (not "off" or "strict")
- **AND** the configuration can be progressively tightened
- **AND** specific error types can be configured (warning vs error vs none)

#### Scenario: Framework compatibility settings

- **WHEN** Pyright encounters dynamic framework features
- **THEN** `reportMissingTypeStubs` is set to "none" to avoid Emmett/pyDAL noise
- **AND** `reportUnknownMemberType` is set to "none" for ORM fields
- **AND** `reportGeneralTypeIssues` is set to "warning" for gradual improvement

### Requirement: Type Checking Scripts

The project SHALL provide convenient scripts for running type checks both locally and in Docker.

#### Scenario: Docker type check script

- **WHEN** a developer runs `./run_type_check.sh`
- **THEN** the script executes Pyright inside the Docker container
- **AND** output is displayed with proper formatting
- **AND** the script exits with the same code as Pyright (0 for success)

#### Scenario: Local type check fallback

- **WHEN** a developer runs type checking locally (without Docker)
- **THEN** the script detects the local environment
- **AND** runs `pyright` directly using the local Python environment
- **AND** provides the same output as Docker execution

#### Scenario: Targeted type checking

- **WHEN** a developer wants to check only specific files
- **THEN** the script accepts file paths as arguments
- **AND** runs Pyright only on the specified files
- **AND** respects the same configuration as full project checks

