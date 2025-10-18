# Implementation Blocker

## Issue

`emmett-prometheus 0.2.0` has a compatibility issue with Emmett 2.7.1.

### Error Details

```python
File "/usr/local/lib/python3.12/site-packages/emmett_prometheus/_imports.py", line 5, in <module>
  if _major < 2 or (_major == 2 and _minor < 6):
     ^^^^^^^^^^
TypeError: '<' not supported between instances of 'str' and 'int'
```

The version detection code in `emmett_prometheus/_imports.py` is incorrectly comparing version strings as strings instead of integers.

### Versions Tested

- Emmett: 2.7.1
- emmett-prometheus: 0.2.0 (latest available on PyPI as of 2025-10-12)
- Python: 3.12

### Workaround Options

1. **Wait for upstream fix**: Report the bug to emmett-framework/prometheus and wait for a new release
2. **Manual implementation**: Implement custom Prometheus metrics without the extension
3. **Downgrade Emmett**: Downgrade to Emmett 2.5.x (not recommended)

### Proposed Action

**Option 2 recommended**: Implement custom Prometheus integration using `prometheus_client` directly.

## Implementation Status

- ✅ Dependency added to requirements.txt
- ✅ Configuration code added to app.py
- ✅ Docker configuration updated  
- ✅ Prometheus scraping configured
- ❌ **BLOCKED**: Extension fails to load due to version detection bug
- ⏸️ Testing pending resolution of blocker

## Next Steps

1. Report issue to emmett-framework/prometheus GitHub repository
2. Implement custom Prometheus metrics as temporary solution
3. Replace custom implementation with extension once bug is fixed

## Alternative Implementation

If needed urgently, we can use `prometheus_client` directly:

```python
from prometheus_client import Counter, Histogram, generate_latest
from emmett import response

# Define custom metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

@app.route('/metrics')
async def metrics():
    """Expose Prometheus metrics"""
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return generate_latest()
```

This would provide basic metrics without the extension.

