# Design: Prometheus Monitoring Integration

## Context

The Emmett application currently lacks observability and metrics collection capabilities. Adding Prometheus monitoring will enable:
- Real-time performance tracking
- Request rate and latency monitoring
- Error rate tracking
- System resource utilization monitoring
- Historical metrics for trend analysis

The official emmett-framework/prometheus extension provides seamless integration with minimal code changes.

## Goals / Non-Goals

### Goals
- Integrate Prometheus metrics collection into the Emmett application
- Expose metrics endpoint for Prometheus scraping
- Configure Docker-based Prometheus server for metrics storage
- Enable HTTP and WebSocket metrics collection
- Provide foundation for alerting and visualization (Grafana)
- Maintain minimal performance overhead (<1% CPU/memory impact)

### Non-Goals
- Custom metric creation beyond extension defaults (can be added later)
- Full alerting rule configuration (basic setup only)
- Grafana dashboard creation (example only, if time permits)
- Multi-node deployment or federation setup
- Long-term metrics storage beyond Prometheus defaults

## Decisions

### Decision 1: Use Official emmett-prometheus Extension
**Rationale:** 
- Official Emmett framework extension, well-maintained
- Built specifically for Emmett's async architecture
- Minimal configuration required
- Follows Prometheus best practices
- Active development and community support

**Alternatives Considered:**
- Custom Prometheus client integration: More work, less integrated
- StatsD/Graphite: Different ecosystem, less standard than Prometheus
- OpenTelemetry: Overkill for current needs, more complex

### Decision 2: Enable HTTP Metrics by Default, System Metrics Optional
**Rationale:**
- HTTP metrics are core to web application monitoring
- System metrics add overhead and may not be needed initially
- Can be enabled via configuration without code changes

### Decision 3: Default Metrics Path at `/metrics`
**Rationale:**
- Standard Prometheus convention
- Easy to remember and configure
- No conflict with existing application routes

### Decision 4: Docker-based Prometheus Deployment
**Rationale:**
- Consistent with project's Docker-first approach
- Easy to version control configuration
- Isolated from application container
- Simple to add Grafana and Alertmanager later

### Decision 5: Minimal Initial Configuration
**Rationale:**
- Start simple, add complexity as needed
- Default histogram buckets are reasonable for most use cases
- Custom metrics can be added incrementally

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  Runtime Service │        │   Prometheus     │         │
│  │  (Emmett App)   │◄───────│   Server         │         │
│  │  Port: 8081     │ scrape │   Port: 9090     │         │
│  │                 │        │                  │         │
│  │  GET /metrics   │        │  - Scrapes every │         │
│  │  (Prometheus)   │        │    15s           │         │
│  └──────────────────┘        │  - Stores metrics│         │
│                              │  - Query engine  │         │
│                              └──────────────────┘         │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  Alertmanager   │◄───────│   Grafana        │         │
│  │  Port: 9093     │        │   Port: 3000     │         │
│  │  (Optional)     │        │   (Optional)     │         │
│  └──────────────────┘        └──────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Metrics Flow
1. Application handles HTTP/WebSocket requests
2. emmett-prometheus extension intercepts and measures
3. Metrics stored in memory, exposed at `/metrics`
4. Prometheus scrapes metrics every 15s (configurable)
5. Metrics stored in Prometheus time-series database
6. Users query metrics via Prometheus UI or Grafana

### Key Metrics Collected
- **HTTP Request Count:** `emmett_http_requests_total` (by method, path, status)
- **HTTP Request Duration:** `emmett_http_request_duration_seconds` (histogram)
- **HTTP Request Size:** `emmett_http_request_size_bytes` (histogram)
- **HTTP Response Size:** `emmett_http_response_size_bytes` (histogram)
- **WebSocket Connections:** `emmett_ws_connections_total`
- **System Metrics (optional):** CPU, memory, file descriptors

## Configuration

### Extension Configuration
```python
from emmett_prometheus import Prometheus

app.use_extension(Prometheus)

app.config.Prometheus.enable_http_metrics = True
app.config.Prometheus.enable_ws_metrics = True
app.config.Prometheus.enable_sys_metrics = False  # Optional
app.config.Prometheus.metrics_route_path = '/metrics'
```

### Prometheus Scraping Configuration
```yaml
# docker/prometheus.yml
scrape_configs:
  - job_name: 'emmett-app'
    scrape_interval: 15s
    static_configs:
      - targets: ['runtime:8081']
    metrics_path: '/metrics'
```

## Risks / Trade-offs

### Risk 1: Metric Cardinality Explosion
**Risk:** High-cardinality labels (e.g., user IDs in paths) can create millions of metric series.
**Mitigation:** 
- Use path templates, not actual IDs in labels
- Extension handles this by using route patterns, not actual URLs
- Monitor Prometheus memory usage

### Risk 2: Performance Overhead
**Risk:** Metrics collection adds latency to each request.
**Mitigation:**
- Extension designed for minimal overhead (<1ms per request)
- In-memory metrics, no I/O during request
- Can disable specific metric types if needed

### Risk 3: Security - Metrics Endpoint Exposure
**Risk:** `/metrics` endpoint exposes application internals.
**Mitigation:**
- Keep internal to Docker network (don't expose externally)
- Can add authentication if needed (future enhancement)
- No sensitive data in default metrics

### Risk 4: Prometheus Storage Growth
**Risk:** Metrics storage grows over time.
**Mitigation:**
- Configure retention period (default 15 days)
- Use downsampling for older data (future)
- Monitor Prometheus disk usage

## Migration Plan

### Phase 1: Installation and Basic Setup
1. Add dependency to requirements.txt
2. Configure extension in app.py
3. Verify `/metrics` endpoint works

### Phase 2: Docker Infrastructure
1. Configure Prometheus service in docker-compose.yaml
2. Set up scraping configuration
3. Verify end-to-end metrics flow

### Phase 3: Validation and Documentation
1. Test metrics accuracy
2. Document setup and usage
3. Create example queries

### Phase 4: Optional Enhancements (Future)
1. Add custom application metrics
2. Configure Grafana dashboards
3. Set up alerting rules
4. Enable system metrics if needed

### Rollback
- Remove extension from app.py
- Remove dependency from requirements.txt
- Stop Prometheus container
- No data loss (metrics are operational, not stored in app database)

## Performance Impact

### Expected Overhead
- **Memory:** ~50MB for Prometheus client library
- **CPU:** <1% increase per request
- **Latency:** <1ms per request for metric collection
- **Network:** ~1KB per scrape interval to Prometheus

### Monitoring Performance
- Track `emmett_http_request_duration_seconds` before/after
- Monitor application memory usage
- Watch Prometheus scrape duration

## Open Questions

1. **Should we enable system metrics initially?**
   - Recommendation: No, enable later if needed to minimize overhead

2. **What histogram buckets should we use?**
   - Recommendation: Start with defaults (.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10)
   - Adjust based on actual latency patterns

3. **Should we set up Grafana immediately?**
   - Recommendation: No, focus on Prometheus first. Add Grafana in future iteration.

4. **Authentication for /metrics endpoint?**
   - Recommendation: Not initially. Keep internal to Docker network. Add if exposing externally.

5. **Alerting rules configuration?**
   - Recommendation: Minimal/none initially. Add specific alerts based on operational experience.

