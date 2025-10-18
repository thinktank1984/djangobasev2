# Design: Bugsink Error Tracking Integration

## Context

The Emmett application needs error tracking to improve debugging and monitoring in development and production environments. Bugsink is a self-hosted, open-source alternative to Sentry that provides error tracking without external dependencies or data sharing concerns.

**Background:**
- Emmett framework has official Sentry extension support via emmett-framework/sentry
- Bugsink is Sentry-compatible, meaning it accepts the same SDK and protocol
- Self-hosted solution aligns with project's emphasis on Docker-based development

**Stakeholders:**
- Development team (improved error visibility)
- Operations (easier debugging in production)

## Goals / Non-Goals

**Goals:**
- Enable automatic capture of unhandled exceptions
- Provide centralized error dashboard at http://localhost:8000
- Capture stack traces, request context, and user information
- Support error grouping and filtering
- Enable performance monitoring (optional)
- Maintain simplicity - minimal configuration overhead

**Non-Goals:**
- Not replacing application logging (complementary)
- Not implementing custom error handlers (use Emmett's built-in)
- Not adding user-facing error pages (keep Emmett defaults)
- Not implementing alerting/notifications (future consideration)

## Decisions

### Decision 1: Use Bugsink instead of hosted Sentry

**What:** Deploy Bugsink as a Docker service instead of using Sentry's hosted service.

**Why:**
- Self-hosted keeps all error data within project infrastructure
- No external account or API keys required for development
- Sentry-compatible protocol means we can switch later if needed
- Aligns with Docker-first development approach
- Free and open source

**Alternatives considered:**
- Hosted Sentry: Requires external account, costs money at scale, data leaves infrastructure
- Custom logging: Lacks structured error tracking, search, and grouping capabilities
- Other error tracking (Rollbar, etc.): Not Sentry-compatible, would need different SDK

### Decision 2: Use emmett-framework/sentry extension

**What:** Use the official Emmett Sentry extension rather than integrating Sentry SDK directly.

**Why:**
- Official Emmett integration designed for framework
- Handles ASGI middleware integration automatically
- Maintains consistency with Emmett patterns
- Properly captures request context and user information
- Actively maintained by Emmett team

**Alternatives considered:**
- Direct Sentry SDK integration: More manual setup, might miss Emmett-specific context
- Custom error tracking: Reinventing the wheel, maintenance burden

### Decision 3: Default configuration with opt-out capability

**What:** Enable error tracking by default in development, allow disabling via environment variable.

**Why:**
- Errors in development are valuable to catch early
- Easy to disable if it causes issues
- Encourages consistent error tracking practices
- Makes transition to production easier

**Configuration:**
```python
# In app.py
SENTRY_DSN = os.environ.get('SENTRY_DSN', 'http://public@localhost:8000/1')
SENTRY_ENABLED = os.environ.get('SENTRY_ENABLED', 'true').lower() == 'true'
```

### Decision 4: Capture rate and performance monitoring

**What:** 
- Capture 100% of errors in development
- Enable performance monitoring at 10% sampling rate
- Make these configurable via environment variables

**Why:**
- Development: Want to see all errors for thorough debugging
- Performance monitoring helps identify slow endpoints
- Low sampling rate keeps overhead minimal
- Configurable for different environments

## Risks / Trade-offs

### Risk: Additional service overhead
- **Impact:** Adds another Docker container, increases resource usage
- **Mitigation:** Bugsink is lightweight; can be disabled in environments where it's not needed
- **Trade-off:** Worth it for the debugging value

### Risk: Error capture overhead
- **Impact:** Each error requires network call to Bugsink
- **Mitigation:** Sentry SDK handles async reporting, won't block requests
- **Trade-off:** Minimal performance impact for significant debugging value

### Risk: Sensitive data in error reports
- **Impact:** Stack traces might contain passwords, tokens, or PII
- **Mitigation:** 
  - Configure scrubbing for sensitive fields
  - Review Sentry extension's default scrubbing
  - Document what data gets captured
- **Trade-off:** Need to balance debugging info with data sensitivity

### Risk: Bugsink learning curve
- **Impact:** Team needs to learn new tool
- **Mitigation:** 
  - Bugsink UI is similar to Sentry (familiar to many)
  - Provide documentation and examples
  - Simple enough to start without extensive training
- **Trade-off:** One-time learning investment for ongoing value

## Migration Plan

### Phase 1: Development setup (This proposal)
1. Add Bugsink to docker-compose.yaml
2. Add emmett-sentry to requirements.txt
3. Configure Sentry extension in app.py
4. Test with sample errors
5. Document setup and usage

### Phase 2: Production considerations (Future)
- Determine production hosting approach for Bugsink
- Configure error rate limits and sampling
- Set up persistent storage for error data
- Consider alerting integrations

### Rollback Plan
If issues arise:
1. Set `SENTRY_ENABLED=false` environment variable
2. Remove or comment out Sentry extension initialization
3. Remove Bugsink from docker-compose.yaml if needed
4. Application continues working without error tracking

## Open Questions

1. **Q:** Should we capture user information in error reports?
   **A:** Yes, include user ID if authenticated. Don't include passwords or sensitive fields.

2. **Q:** What's the data retention policy for errors?
   **A:** Start with 30 days default. Can be configured in Bugsink settings.

3. **Q:** Should we add custom tags or context?
   **A:** Start simple. Add custom context later if specific debugging needs arise.

4. **Q:** How do we handle errors in background tasks or CLI commands?
   **A:** Sentry extension should capture those automatically. Verify during testing.

