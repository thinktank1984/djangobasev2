# Valkey Cache Support

## Why

Valkey is an open-source, Redis-compatible alternative that provides a drop-in replacement for Redis without licensing concerns. As Redis has moved to restrictive licensing (SSPL/RSALv2), Valkey offers a truly open-source alternative maintained by the Linux Foundation. Adding Valkey support provides users with a Redis-compatible caching option that is community-driven and ensures long-term viability for open-source projects.

## What Changes

- Add `ValkeyCache` handler class that mirrors `RedisCache` functionality
- Support standard Valkey connection parameters (host, port, db, prefix)
- Maintain full API compatibility with existing `RedisCache` handler
- Enable multi-cache configurations with Valkey alongside existing cache backends
- Document Valkey configuration and usage patterns
- Add Valkey to requirements and Docker configuration
- Include tests for Valkey cache operations

## Impact

### Affected Specs
- `cache` - New capability specification defining cache backend requirements

### Affected Code
- `runtime/app.py` - Example configuration for Valkey usage
- `setup/requirements.txt` - Add valkey-py package dependency
- `docker/docker-compose.yaml` - Add Valkey service container (optional)
- `docker/Dockerfile` - Include valkey-py in container image
- `emmett_documentation/docs/caching.md` - Add Valkey documentation section
- `runtime/tests.py` - Add Valkey cache tests

### Compatibility
- **Non-breaking change** - Existing Redis cache configurations remain unchanged
- **Fully compatible** - Valkey uses the same protocol as Redis
- **Optional feature** - Users can continue using Redis, RAM, or Disk cache without changes

