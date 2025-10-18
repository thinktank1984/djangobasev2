# Add Type Checking with MonkeyType and Pyright

## Why

The codebase currently lacks type annotations, making it difficult to catch type-related bugs during development and reducing IDE support for auto-completion and refactoring. Adding comprehensive type hints will improve code quality, developer experience, and maintainability by enabling static type checking and better tooling support.

## What Changes

- **Add Pyright** as the static type checker for the project
- **Add MonkeyType** to automatically infer and generate type hints from runtime traces
- **Generate type annotations** for all Python files in the codebase using MonkeyType
- **Configure Pyright** with appropriate settings for the Emmett framework
- **Update CI/CD** to run type checking on all commits
- **Add type checking scripts** to development workflow
- **Document type checking practices** in project documentation

## Impact

- **Affected specs**: 
  - NEW: `type-checking` - Type checking and static analysis capability
  - MODIFIED: `testing` - Add type checking to test workflow
- **Affected code**: 
  - All Python files in `runtime/` will receive type annotations
  - All Python files in `tests/` will receive type annotations
  - New configuration files: `setup/pyrightconfig.json`, type checking scripts
  - Updated `requirements.txt` with MonkeyType and Pyright dependencies
  - Updated `docker/Dockerfile` to include type checking tools
  - Updated CI/CD workflows (if any) to run type checks
- **Breaking changes**: None (type hints are backward compatible)
- **Benefits**:
  - Catch type errors before runtime
  - Better IDE support (auto-completion, refactoring, documentation)
  - Self-documenting code through type annotations
  - Easier onboarding for new developers
  - Reduced debugging time

## Implementation Approach

### Progressive Type Error Fixing

After setting up the type checking infrastructure, type errors should be fixed incrementally:

1. **Run type check on individual files**:
   ```bash
   ./run_type_check.sh runtime/app.py
   ./run_type_check.sh runtime/models/user/model.py
   # etc.
   ```

2. **Fix errors in order of priority**:
   - **Critical errors** (actual bugs) - Fix immediately
   - **ORM attribute access** - Add `# type: ignore[attr-defined]` with comment
   - **Unused imports** - Remove or comment why needed
   - **Type mismatches** - Add proper type annotations

3. **Document expected errors**:
   - pyDAL ORM fields (`.id`, `.update_record()`, etc.) are dynamically generated
   - Use `# type: ignore[attr-defined]` for ORM operations
   - Add comments explaining why type ignore is needed

4. **Iterative approach**:
   - Fix one file or module at a time
   - Run type check after each fix
   - Commit working changes incrementally
   - Track progress in baseline (start: ~89 errors, goal: <20)

