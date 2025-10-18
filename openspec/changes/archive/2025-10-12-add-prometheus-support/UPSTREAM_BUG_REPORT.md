# Upstream Bug Report Template

## Repository
https://github.com/emmett-framework/prometheus

## Issue Title
`TypeError: '<' not supported between instances of 'str' and 'int'` - Version parsing bug prevents extension loading

## Issue Description

### Problem
The `emmett-prometheus` extension (v0.2.0) fails to load due to a version parsing bug in `_imports.py`. The extension attempts to compare a string version number directly with an integer, causing a TypeError.

### Error
```
TypeError: '<' not supported between instances of 'str' and 'int'
```

**File**: `emmett_prometheus/_imports.py:5`

### Root Cause
```python
# Current code (BUGGY)
_major, _minor, _ = _version.split(".", 2)
if _major < 2:  # BUG: _major is a string, comparing with int 2
    ...
```

### Tested Versions
- ✅ `emmett-prometheus==0.2.0` - Affected
- ✅ `emmett==2.7.1` - Affected
- ✅ `emmett==2.6.0` - Also affected

### Suggested Fix
```python
# Proposed fix
_major, _minor, _ = _version.split(".", 2)
_major = int(_major)  # Convert to int before comparison
if _major < 2:
    ...
```

Or more robustly:
```python
from packaging import version
if version.parse(_version) < version.parse("2.0.0"):
    ...
```

### Reproduction Steps
1. Install emmett-prometheus==0.2.0
2. Import the extension: `from emmett_prometheus import Prometheus`
3. Observe TypeError on import

### Environment
- Python: 3.12
- emmett: 2.7.1 (also tested 2.6.0)
- emmett-prometheus: 0.2.0
- OS: macOS (Docker container with Debian base)

### Workaround
For users affected by this bug, a simple workaround is to use `prometheus-client` directly instead of this extension. Example implementation: ~40 lines of code.

See: https://prometheus.github.io/client_python/

### Impact
- Extension completely unusable with current Emmett versions
- Blocks Prometheus monitoring integration for Emmett users
- Simple one-line fix required

### Labels
- `bug`
- `version-compatibility`
- `high-priority`

---

## Submission Instructions

1. Go to: https://github.com/emmett-framework/prometheus/issues
2. Click "New Issue"
3. Copy the above content
4. Submit the issue
5. Link the issue in this file for tracking

## Issue Status
- [ ] Bug report submitted
- [ ] Issue link: [Add GitHub issue link here]
- [ ] Response received
- [ ] Fix released

## Notes
This bug report can be submitted by any community member. The fix is trivial and should be straightforward for the maintainers to implement.

