# Git Hooks for Emmett Project

This directory contains git hooks that help maintain code quality and prevent anti-patterns from entering the codebase.

## Available Hooks

### pre-commit

Runs **Emmett model validation** and **type checking** before allowing commits.

**What it does:**
1. **Model Validation** (if model files modified):
   - Checks if any model files have been modified (`runtime/app.py`, `runtime/models/*.py`)
   - Runs `validate_models.py` to check for anti-patterns
   - **Blocks commits** if models contain errors (anti-patterns)
   - **Allows commits** if models only have warnings (can be fixed later)

2. **Type Checking** (for all Python files):
   - Runs Pyright on all modified `.py` files
   - **Blocks commits** if type errors are found
   - **Allows commits** if only warnings exist
   - Uses Docker for consistency (falls back gracefully if unavailable)

**Anti-patterns detected:**
- HTTP request/response handling in models
- Template rendering in models
- HTML generation in models
- External API calls in models
- Direct session access in models
- Email sending in models
- Overly complex methods

## Installation

### Automatic Installation (Recommended)

```bash
# From project root
./hooks/install.sh
```

### Manual Installation

```bash
# From project root
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Usage

Once installed, the hooks run automatically:

```bash
# Make changes to any Python files
vim runtime/models/post.py

# Try to commit (hook runs automatically)
git add runtime/models/post.py
git commit -m "Update Post model"

# If validation or type checking fails:
🔍 Model files changed, running validation...

✅ Model validation passed

🔍 Running type checking on changed files...
  Checking: runtime/models/post.py
    ✗ Type errors found
/app/runtime/models/post.py:50:14 - error: Cannot access attribute "id"

❌ Type checking failed with 1 file(s) containing errors

Fix type errors before committing or use type: ignore comments where appropriate.

To fix:
  1. Review the type errors above
  2. Add type hints or type: ignore comments
  3. Re-run: ./run_type_check.sh <file>
```

### Bypassing Hooks (Not Recommended)

If you need to commit despite validation failures:

```bash
git commit --no-verify -m "WIP: fixing models"
```

**⚠️ Warning:** Bypassing hooks should only be done for:
- Work-in-progress commits on feature branches
- Emergency hotfixes (fix the issues ASAP after)

**Never bypass hooks for:**
- Commits to main/master branch
- Pull request commits
- Production deployments

## Testing Hooks Locally

Test the pre-commit hook without committing:

```bash
# From project root
./hooks/pre-commit
```

Or test components individually:

```bash
# Test model validation
cd runtime
python validate_models.py --all

# Test type checking
./run_type_check.sh
./run_type_check.sh runtime/models/post.py  # Check specific file
```

## Uninstalling Hooks

```bash
# Remove pre-commit hook
rm .git/hooks/pre-commit
```

## CI/CD Integration

These hooks should also be enforced in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Validate Models
  run: |
    cd runtime
    python validate_models.py --all --severity error

- name: Type Check
  run: ./run_type_check.sh
  continue-on-error: true  # Initially allow failures for gradual adoption
```

## Troubleshooting

### Hook not running

1. Check hook is installed: `ls -la .git/hooks/pre-commit`
2. Check hook is executable: `chmod +x .git/hooks/pre-commit`
3. Run hook manually to see errors: `./hooks/pre-commit`

### Python not found

The hook tries multiple Python interpreters:
1. `../venv/bin/python` (project virtual environment)
2. `uv run python` (if uv is installed)
3. `python3`
4. `python`

Make sure you have Python installed and the project dependencies set up.

### Hook too slow

The hook is optimized to only check changed files:
- Model validation: Only runs when model files are modified
- Type checking: Only checks the files being committed (not entire project)

If it's still slow:

1. Run checks separately to fix all issues once:
   ```bash
   python runtime/validate_models.py --all
   ./run_type_check.sh
   ```
2. Fix all issues at once
3. Future commits will be fast (no issues to report)

### Docker not available

If Docker is not running, type checking will show a warning but won't block commits:

```
⚠️  Docker not available, skipping type checking
   Run './run_type_check.sh' manually before pushing
```

**Action:** Run `./run_type_check.sh` manually before pushing to remote.

## Why Use Git Hooks?

**Benefits:**
- ✅ Catches anti-patterns before they enter the codebase
- ✅ Catches type errors before they cause runtime bugs
- ✅ Enforces best practices automatically
- ✅ Prevents broken code from reaching code review
- ✅ Saves time in code review (fewer "please fix this" comments)
- ✅ Maintains consistent code quality across the team
- ✅ Incremental type checking (only changed files)

**Repository Policy:**
This project follows strict **NO MOCKING** and **INTEGRATION TESTING ONLY** policies. Git hooks help enforce architectural best practices to maintain code quality.

## See Also

- `/runtime/validate_models.py` - Model validation script
- `/runtime/validate.sh` - Wrapper script for validation
- `/run_type_check.sh` - Type checking script
- `/run_type_check_per_file.sh` - Per-file type checking (generates reports)
- `/run_bloggy.sh` - Application startup (includes validation)
- `/setup/pyrightconfig.json` - Type checking configuration
- `/openspec/changes/add-type-checking/` - Type checking implementation details
- `/documentation/NO_MOCKING_ENFORCEMENT.md` - Testing policies
- `/AGENTS.md` - Complete repository guidelines

