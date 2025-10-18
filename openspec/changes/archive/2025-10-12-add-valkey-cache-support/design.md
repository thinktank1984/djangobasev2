# Valkey Cache Support - Technical Design

## Context

Valkey is a Linux Foundation open-source project that emerged as a Redis fork after Redis adopted dual SSPL/RSALv2 licensing in March 2024. Major cloud providers (AWS, Google Cloud, Oracle) and the open-source community backed Valkey to ensure a truly open-source, Redis-compatible caching solution.

### Current State
- Emmett framework currently supports Redis caching via `RedisCache` handler
- Redis client library: `redis-py`
- Configuration follows standard Emmett cache handler pattern
- Multi-cache backend support already in place

### Stakeholders
- **Developers**: Need open-source caching without licensing concerns
- **Enterprises**: Require license-compliant infrastructure components
- **Cloud Deployments**: Benefit from managed Valkey services (AWS MemoryDB, etc.)

### Constraints
- Must maintain backward compatibility with existing Redis configurations
- Should not require Emmett framework core changes (use existing extension points)
- Must work seamlessly in Docker development environment
- Cannot break existing cache API contracts

## Goals / Non-Goals

### Goals
- ✅ Provide drop-in Valkey cache backend for Emmett applications
- ✅ Maintain full Redis protocol compatibility
- ✅ Enable seamless migration from Redis to Valkey
- ✅ Support all existing cache operations (get, set, clear, patterns, async)
- ✅ Include Docker Compose configuration for local development
- ✅ Document configuration and usage patterns
- ✅ Add comprehensive tests for Valkey operations

### Non-Goals
- ❌ Modify Emmett framework core caching implementation
- ❌ Create Valkey-specific features beyond Redis compatibility
- ❌ Support non-Redis-compatible Valkey extensions
- ❌ Provide automatic migration tools from Redis to Valkey
- ❌ Implement connection pooling beyond what valkey-py provides
- ❌ Build custom Valkey client (use valkey-py library)

## Decisions

### Decision 1: Use valkey-py Library

**What**: Use the official `valkey-py` Python client library maintained by the Valkey project.

**Why**:
- Official library with active maintenance
- Drop-in replacement for redis-py with identical API
- Protocol-level compatibility guaranteed
- Community support and security updates
- Minimal migration effort from redis-py

**Alternatives Considered**:
1. **Continue using redis-py**: 
   - ❌ Doesn't signal explicit Valkey support
   - ❌ May have licensing concerns in the future
   - ❌ Doesn't benefit from Valkey-specific optimizations

2. **Create custom Valkey client**: 
   - ❌ Significant development overhead
   - ❌ Maintenance burden
   - ❌ Reinventing the wheel
   - ❌ Potential compatibility issues

3. **Use redis-py with Valkey server**: 
   - ✓ Works due to protocol compatibility
   - ❌ Unclear licensing implications
   - ❌ Not officially supported configuration
   - ❌ Confusing for developers

### Decision 2: ValkeyCache Handler Implementation

**What**: Create a standalone `ValkeyCache` handler class that mirrors `RedisCache` structure.

**Why**:
- Clear separation of concerns
- Explicit Valkey support in codebase
- Easier to document and test
- Future-proof for potential Valkey-specific features
- Follows Emmett's existing cache handler pattern

**Implementation Approach**:
```python
# Option A: Custom handler in application code (chosen)
from emmett.cache import Cache
from valkey import Valkey

class ValkeyCache:
    def __init__(self, host='localhost', port=6379, db=0, 
                 prefix='cache:', default_expire=300):
        self.client = Valkey(host=host, port=port, db=db)
        self.prefix = prefix
        self.default_expire = default_expire
    
    def get(self, key):
        return self.client.get(f"{self.prefix}{key}")
    
    def set(self, key, value, duration=None):
        ttl = duration or self.default_expire
        return self.client.setex(f"{self.prefix}{key}", ttl, value)
    
    def clear(self, key=None):
        if key is None:
            return self.client.flushdb()
        if '*' in key:
            keys = self.client.keys(f"{self.prefix}{key}")
            return self.client.delete(*keys) if keys else 0
        return self.client.delete(f"{self.prefix}{key}")

# Usage
cache = Cache(valkey=ValkeyCache(host='valkey', port=6379))
```

**Alternatives Considered**:
1. **Extend Emmett's cache module**: 
   - ❌ Requires framework changes
   - ❌ Coupling to Emmett release cycle
   - ❌ May not be accepted upstream

2. **Create Emmett extension package**: 
   - ❌ Additional package to maintain
   - ❌ Extra dependency management
   - ✓ Could benefit wider community

3. **Alias RedisCache to ValkeyCache**: 
   - ❌ Confusing naming
   - ❌ Hides actual implementation
   - ❌ Future compatibility concerns

### Decision 3: Docker Service Configuration

**What**: Add optional Valkey service to docker-compose.yaml using official Valkey Docker image.

**Why**:
- Consistent development environment
- Easy local testing
- No additional installation required
- Matches existing Docker-first workflow
- Demonstrates production-like setup

**Configuration**:
```yaml
valkey:
  image: valkey/valkey:7.2-alpine
  container_name: valkey
  ports:
    - "6379:6379"
  volumes:
    - valkey_data:/data
  command: valkey-server --appendonly yes
  networks:
    - app_network
  healthcheck:
    test: ["CMD", "valkey-cli", "ping"]
    interval: 5s
    timeout: 3s
    retries: 5
```

**Alternatives Considered**:
1. **Use Redis image**: 
   - ❌ Defeats purpose of Valkey support
   - ❌ Licensing confusion

2. **No Docker service**: 
   - ❌ Inconsistent with project patterns
   - ❌ Harder to test locally
   - ❌ Requires manual setup

3. **Make Valkey the default**: 
   - ❌ Breaking change for existing users
   - ❌ Forces migration

### Decision 4: Environment-Based Configuration

**What**: Support environment variables for Valkey connection configuration.

**Why**:
- 12-factor app compliance
- Production deployment flexibility
- Secure credential management
- Kubernetes/container-friendly
- Follows existing project patterns

**Environment Variables**:
- `VALKEY_HOST` (default: localhost)
- `VALKEY_PORT` (default: 6379)
- `VALKEY_DB` (default: 0)
- `VALKEY_PREFIX` (default: cache:)
- `VALKEY_EXPIRE` (default: 300)

## Risks / Trade-offs

### Risk 1: valkey-py Library Maturity
**Risk**: valkey-py is newer than redis-py, may have undiscovered bugs.

**Mitigation**:
- Comprehensive test suite covering all operations
- Pin specific version in requirements.txt
- Monitor Valkey issue tracker and release notes
- Fallback to Redis if issues discovered

**Impact**: Low - Valkey protocol compatibility with Redis is strong

---

### Risk 2: Valkey vs Redis Feature Drift
**Risk**: Future Valkey releases may diverge from Redis protocol.

**Mitigation**:
- Document tested Valkey version
- Test against both Redis and Valkey in CI (future)
- Keep implementation simple (avoid advanced features)
- Monitor Valkey compatibility commitments

**Impact**: Medium - Could require future handler updates

---

### Risk 3: Emmett Framework Changes
**Risk**: Future Emmett versions may change cache handler interface.

**Mitigation**:
- Follow Emmett's stable cache API patterns
- Document Emmett version compatibility
- Maintain tests that validate API compatibility
- Keep handler implementation simple and focused

**Impact**: Low - Emmett has stable cache interface

---

### Risk 4: Connection Pool Exhaustion
**Risk**: Multiple workers could exhaust Valkey connection pool.

**Mitigation**:
- Use valkey-py connection pooling defaults
- Document recommended pool size settings
- Add connection pool configuration options
- Monitor connection metrics in production

**Impact**: Low - valkey-py handles pooling well

---

### Trade-off 1: Custom Handler vs Framework Integration
**Chosen**: Custom handler in application code

**Benefits**:
- ✅ No framework dependency
- ✅ Faster implementation
- ✅ Project-specific control

**Costs**:
- ❌ Not available to other Emmett users automatically
- ❌ Duplicated effort if others need same feature

**Justification**: Project-specific need, can be extracted to extension later if needed.

---

### Trade-off 2: Valkey-Only vs Hybrid Redis/Valkey
**Chosen**: Both Redis and Valkey supported simultaneously

**Benefits**:
- ✅ Zero breaking changes
- ✅ Gradual migration path
- ✅ Users choose based on needs

**Costs**:
- ❌ Two cache backends to document
- ❌ Potential confusion about which to use

**Justification**: Non-breaking changes are critical; users may have existing Redis infrastructure.

## Migration Plan

### Phase 1: Development (Current)
1. Install valkey-py package
2. Create ValkeyCache handler class
3. Add Valkey service to docker-compose
4. Write tests for Valkey operations
5. Document configuration and usage

### Phase 2: Testing
1. Run full test suite with Valkey backend
2. Performance comparison with Redis (optional)
3. Connection pool stress testing
4. Multi-worker cache sharing verification

### Phase 3: Documentation
1. Add Valkey section to caching.md
2. Update AGENTS.md with Valkey option
3. Create migration guide (Redis → Valkey)
4. Add troubleshooting section

### Phase 4: Deployment
1. Deploy Valkey service to staging
2. Test application with Valkey backend
3. Monitor performance and errors
4. Rollback plan: Switch back to Redis config

### Rollback Strategy
If issues are discovered with Valkey:
1. Change handler from `ValkeyCache()` to `RedisCache()`
2. Point connection to Redis server instead
3. No code changes required (API compatible)
4. Data in Valkey can be migrated using Redis protocol tools

### Data Migration (Redis → Valkey)
For existing Redis caches:
1. **Option A - Cold Migration**: 
   - Stop application
   - Export Redis data using DUMP/RESTORE
   - Import to Valkey
   - Switch configuration
   - Restart application

2. **Option B - Warm Start** (Recommended):
   - Deploy Valkey alongside Redis
   - Switch application to Valkey
   - Let cache warm up naturally
   - No downtime required (cache misses acceptable)

3. **Option C - Gradual Migration**:
   - Run both Redis and Valkey
   - Route specific keys/services to Valkey
   - Monitor performance
   - Complete migration when confident

## Open Questions

### Q1: Should we contribute ValkeyCache back to Emmett framework?
**Status**: Deferred - Implement in project first, evaluate later

**Considerations**:
- Would benefit broader Emmett community
- Requires coordination with Emmett maintainers
- May slow initial implementation

**Decision Point**: After 3 months of production use

---

### Q2: Do we need Valkey Cluster support?
**Status**: Not in scope for initial implementation

**Considerations**:
- Cluster adds complexity
- Single-node sufficient for current scale
- Can add later if needed

**Decision Point**: When cache becomes bottleneck (>1M req/day)

---

### Q3: Should we support both Redis and Valkey simultaneously in production?
**Status**: Supported but not recommended

**Considerations**:
- Adds operational complexity
- Doubles cache infrastructure
- Could be useful for gradual migration

**Recommendation**: Use one or the other, not both

---

### Q4: What about Valkey JSON or Valkey Search modules?
**Status**: Out of scope

**Considerations**:
- Requires additional dependencies
- Not Redis-compatible (Valkey extensions)
- Complicates handler implementation

**Recommendation**: Stick to core Redis-compatible operations

## Implementation Notes

### File Changes
- `runtime/app.py` - Add example ValkeyCache configuration
- `setup/requirements.txt` - Add valkey-py>=5.0.0
- `docker/Dockerfile` - Install valkey-py in container
- `docker/docker-compose.yaml` - Add valkey service
- `runtime/tests.py` - Add Valkey cache tests
- `emmett_documentation/docs/caching.md` - Add Valkey documentation section
- `openspec/project.md` - Update cache capabilities list

### Testing Strategy
- Unit tests for ValkeyCache handler methods
- Integration tests with actual Valkey server
- Multi-process cache sharing tests
- Async operation tests
- Pattern-based clearing tests
- Expiration behavior tests

### Performance Expectations
Valkey should have similar performance to Redis:
- GET operations: <1ms p99
- SET operations: <1ms p99
- Pattern clears: <10ms p99 (depends on key count)
- Memory usage: Similar to Redis

### Monitoring Recommendations
- Cache hit/miss ratio
- Connection pool utilization
- Valkey memory usage
- Operation latencies
- Error rates

## References

- [Valkey Project](https://valkey.io/)
- [valkey-py Documentation](https://github.com/valkey-io/valkey-py)
- [Emmett Caching Documentation](emmett_documentation/docs/caching.md)
- [Redis Protocol Specification](https://redis.io/topics/protocol)
- [Valkey Compatibility Guarantees](https://valkey.io/blog/2024-03-27-valkey-compatibility/)

