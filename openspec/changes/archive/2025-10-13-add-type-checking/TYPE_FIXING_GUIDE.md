# Type Error Fixing Guide

This guide provides step-by-step instructions for fixing type errors in the pybase project after type checking has been set up.

## Overview

**Current Baseline**: 85 errors, 176 warnings  
**Goal**: <20 errors, <50 warnings  
**Strategy**: Fix incrementally, one file at a time

## Quick Start

```bash
# Check a specific file
./run_type_check.sh runtime/app.py

# Fix errors, then verify
./run_type_check.sh runtime/app.py

# Check entire project
./run_type_check.sh
```

## Common Error Patterns & Fixes

### 1. ORM Attribute Access

**Error**: `Cannot access attribute "id" for class "User*"`

**Fix**: Add `type: ignore[attr-defined]` comment

```python
# ❌ BEFORE - Type error
user = User.get(user_id)
email = user.email
user_id = user.id

# ✅ AFTER - Fixed
user = User.get(user_id)  # type: ignore[attr-defined]
email = user.email  # type: ignore[attr-defined]
user_id = user.id  # type: ignore[attr-defined]
```

### 2. ORM Methods

**Error**: `Cannot access attribute "update_record" for class "Post*"`

**Fix**: Add `type: ignore[attr-defined]` comment

```python
# ❌ BEFORE - Type error
post = Post.get(post_id)
post.update_record(title=new_title)

# ✅ AFTER - Fixed
post = Post.get(post_id)  # type: ignore[attr-defined]
post.update_record(title=new_title)  # type: ignore[attr-defined]
```

### 3. Missing Route Handler Type Hints

**Error**: No error, but best practice

**Fix**: Add type annotations to route handlers

```python
# ❌ BEFORE - No type hints
async def show_post(id):
    post = Post.get(id)
    return {'post': post}

# ✅ AFTER - With type hints
from typing import Any

async def show_post(id: int) -> dict[str, Any]:
    post = Post.get(id)  # type: ignore[attr-defined]
    return {'post': post}
```

### 4. Unused Imports

**Warning**: `Import "X" is not accessed`

**Fix**: Remove unused imports or keep with justification

```python
# ❌ BEFORE - Unused import
from typing import Optional, Dict, List
from emmett import request

# ✅ AFTER - Only used imports
from typing import Any

# OR keep with comment if needed for type checking
from emmett import request  # type: ignore[reportUnusedImport]
```

### 5. Field Type vs String Type

**Error**: `Argument of type "Field" cannot be assigned to parameter of type "str"`

**Fix**: Access the field value properly or use type ignore

```python
# ❌ BEFORE - Type error
encrypted_token = token.access_token
result = decrypt_token(encrypted_token)

# ✅ AFTER - Fixed
encrypted_token = token.access_token  # type: ignore[arg-type]
result = decrypt_token(str(encrypted_token))
```

### 6. Optional Member Access

**Error**: `"attribute" is not a known attribute of "None"`

**Fix**: Add null checks or use type ignore

```python
# ❌ BEFORE - Type error
config = get_config()
value = config.setting

# ✅ AFTER - With null check
config = get_config()
if config:
    value = config.setting

# OR with type ignore
config = get_config()
value = config.setting  # type: ignore[attr-defined]
```

### 7. Dynamic Form Attribute

**Error**: `Cannot access attribute "form" for class "type[Comment]"`

**Fix**: Use type ignore (Emmett generates this dynamically)

```python
# ❌ BEFORE - Type error
form = await Comment.form()

# ✅ AFTER - Fixed
form = await Comment.form()  # type: ignore[attr-defined]
```

## Priority Order

Fix errors in this order for maximum impact:

1. **Critical Errors** (0 currently)
   - Actual bugs that could cause runtime failures
   - These should be fixed immediately

2. **High-Priority Files** (Core application)
   - `runtime/app.py` - Main application entry point
   - `runtime/base_model.py` - Base model functionality
   - `runtime/models/user/model.py` - User authentication

3. **Medium-Priority Files** (Business logic)
   - Other model files (`post`, `comment`, `role`, etc.)
   - Auth module files
   - API generators

4. **Low-Priority Files** (Utilities and tests)
   - Helper functions
   - Test files
   - Utilities

5. **Warnings** (Last)
   - Unused imports
   - Unused variables
   - Unnecessary comparisons

## Workflow

### Step 1: Check a File

```bash
./run_type_check.sh runtime/models/user/model.py
```

### Step 2: Analyze Errors

Review the output:
- How many errors?
- What type of errors?
- Are they expected (ORM) or unexpected (bugs)?

### Step 3: Fix Errors

Edit the file following the patterns above:
- Add `type: ignore[attr-defined]` for ORM access
- Add type hints to functions
- Remove unused imports

### Step 4: Verify Fix

```bash
./run_type_check.sh runtime/models/user/model.py
```

### Step 5: Commit

```bash
git add runtime/models/user/model.py
git commit -m "fix(types): Add type annotations to User model"
```

### Step 6: Repeat

Move to the next file in priority order.

## Bulk Operations

### Check All Model Files

```bash
for model in runtime/models/*/model.py; do
    echo "Checking $model..."
    ./run_type_check.sh "$model"
done
```

### Remove Unused Imports (Automated)

```bash
# Use autoflake to remove unused imports
docker compose -f docker/docker-compose.yaml exec runtime \
    autoflake --in-place --remove-unused-variables runtime/app.py
```

## Type Annotation Best Practices

### Function Signatures

```python
# ✅ GOOD - Clear type hints
def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    word_count = len(text.split())
    return max(1, word_count // words_per_minute)

# ✅ GOOD - Route handler
from typing import Any

async def api_endpoint(user_id: int) -> dict[str, Any]:
    user = User.get(user_id)  # type: ignore[attr-defined]
    return {'user': user, 'status': 'success'}
```

### Complex Types

```python
from typing import Any, Optional

# ✅ GOOD - Optional return
def find_user_by_email(email: str) -> Optional[Any]:
    return User.where(lambda u: u.email == email).first()  # type: ignore[attr-defined]

# ✅ GOOD - List return
def get_user_posts(user_id: int) -> list[Any]:
    return Post.where(lambda p: p.user == user_id).select()  # type: ignore[attr-defined]
```

### Class Methods

```python
class PostService:
    """Service for post operations"""
    
    def create_post(self, title: str, text: str, user_id: int) -> Any:
        """Create a new post"""
        return Post.create(  # type: ignore[attr-defined]
            title=title,
            text=text,
            user=user_id
        )
    
    def get_recent_posts(self, limit: int = 10) -> list[Any]:
        """Get recent posts"""
        return Post.all().select(limitby=(0, limit))  # type: ignore[attr-defined]
```

## Tracking Progress

Keep track of your progress:

```bash
# Run full check and save results
./run_type_check.sh > type_check_results.txt 2>&1

# Count errors
grep "errors," type_check_results.txt
```

**Example Progress**:
- Day 1: 85 errors, 176 warnings (baseline)
- Day 2: 65 errors, 150 warnings (fixed core files)
- Day 3: 45 errors, 120 warnings (fixed models)
- Day 4: 25 errors, 80 warnings (fixed auth)
- Day 5: 15 errors, 50 warnings (fixed utilities)
- Goal: <20 errors, <50 warnings ✅

## When to Use Type Ignore

**✅ ALWAYS use `type: ignore` for:**
- ORM field access (`.id`, `.email`, `.title`, etc.)
- ORM methods (`.update_record()`, `.delete_record()`)
- Dynamic Emmett features (`.form`, `.validation`)

**⚠️ CAREFULLY use `type: ignore` for:**
- Complex type situations that are correct but Pyright doesn't understand
- Third-party library issues
- Always add a comment explaining WHY

**❌ NEVER use `type: ignore` for:**
- Actual bugs or type errors in your code
- Lazy workaround instead of proper fix
- Without understanding the error

## Getting Help

If you're stuck on a type error:

1. **Check this guide** for common patterns
2. **Check AGENTS.md** for type checking section
3. **Run with verbose**: Pyright usually has good error messages
4. **Ask for help**: Include the specific error and file

## References

- Main documentation: `AGENTS.md` → "## Type Checking"
- Pyright config: `setup/pyrightconfig.json`
- Type checking design: `openspec/changes/add-type-checking/design.md`
- Implementation summary: `openspec/changes/add-type-checking/IMPLEMENTATION_SUMMARY.md`

