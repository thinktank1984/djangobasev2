# Docker Setup Changes for Runtime Application

## Summary

Added Docker support for the Runtime Emmett application with full repository mounting for live development.

## Files Created/Modified

### Created Files

1. **`runtime/Dockerfile`** (NEW)
   - Python 3.12-slim base image
   - Installs Emmett, Granian, pytest
   - Exposes port 8081
   - Configured for ASGI application

2. **`runtime/.dockerignore`** (NEW)
   - Excludes Python cache, virtual environments, logs
   - Prevents unnecessary files in Docker context

3. **`run_runtime.sh`** (NEW)
   - Convenience script to start the runtime service
   - Displays connection info and credentials
   - Note: May need `chmod +x run_runtime.sh`

4. **`docker/RUNTIME_SETUP.md`** (NEW)
   - Comprehensive Docker setup documentation
   - Usage examples and troubleshooting guide
   - Development workflow instructions

5. **`docker/CHANGES.md`** (NEW - this file)
   - Summary of all changes made

### Modified Files

1. **`docker/docker-compose.yaml`** (UPDATED)
   - Added `runtime` service definition
   - Configured with build context pointing to parent directory
   - Full repository mounted to `/app`
   - Port 8081 exposed
   - Granian ASGI server command

2. **`runtime/README.md`** (UPDATED)
   - Added Docker quick start section (Option 1)
   - Added Docker commands section
   - Updated development workflow with Docker instructions

## Configuration Details

### Docker Compose Service

```yaml
runtime:
  build:
    context: ..
    dockerfile: runtime/Dockerfile
  container_name: runtime
  restart: unless-stopped
  ports:
    - "8081:8081"
  environment:
    - PYTHONUNBUFFERED=1
    - EMMETT_ENV=development
  volumes:
    - ..:/app  # Full repository mounted
  working_dir: /app
  command: ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8081", "runtime.app:app"]
```

### Key Features

1. **Full Repository Mount**: The entire `/Users/ed.sharood2/code/pybase/` repository is mounted to `/app` in the container
2. **Live Reload**: Code changes are reflected immediately without rebuilding
3. **Isolated Environment**: Clean Python 3.12 environment with only required dependencies
4. **Easy Management**: Simple commands to start/stop/rebuild

## How to Use

### Quick Start

```bash
# From project root
./run_runtime.sh

# Or manually
cd docker
docker compose up runtime --build
```

### Access the Application

- **URL**: http://localhost:8081
- **Admin Email**: doc@emmettbrown.com
- **Admin Password**: fluxcapacitor

### Common Commands

```bash
# Start service
docker compose -f docker/docker-compose.yaml up runtime

# Start in background
docker compose -f docker/docker-compose.yaml up runtime -d

# View logs
docker compose -f docker/docker-compose.yaml logs -f runtime

# Run tests
docker compose -f docker/docker-compose.yaml exec runtime pytest runtime/tests.py

# Access shell
docker compose -f docker/docker-compose.yaml exec runtime bash

# Stop service
docker compose -f docker/docker-compose.yaml down
```

## Benefits

1. **No Local Python Required**: Everything runs in Docker
2. **Consistent Environment**: Same Python version and dependencies for all developers
3. **Easy Onboarding**: New developers just need Docker
4. **Full Repository Access**: All files available in container for debugging
5. **Integrates with Monitoring**: Works alongside Prometheus, Grafana, etc.

## Testing

To verify the setup works:

```bash
# 1. Start the service
cd docker
docker compose up runtime --build

# 2. Wait for "Application startup complete" message

# 3. In another terminal, test the application
curl http://localhost:8081

# 4. Or open in browser
open http://localhost:8081
```

## Next Steps

1. **Make script executable**: `chmod +x run_runtime.sh`
2. **Setup admin user**: `docker compose -f docker/docker-compose.yaml exec runtime emmett setup`
3. **Run migrations**: `docker compose -f docker/docker-compose.yaml exec runtime emmett migrations up`
4. **Create test user** and verify login/post creation works
5. **Configure production settings** when ready to deploy

## Troubleshooting

### Issue: Port 8081 already in use

**Solution**: Change the port mapping in `docker/docker-compose.yaml`:
```yaml
ports:
  - "8082:8081"  # Use 8082 or any available port
```

### Issue: Permission denied on run_runtime.sh

**Solution**: Make it executable:
```bash
chmod +x run_runtime.sh
```

### Issue: Container keeps restarting

**Solution**: Check logs for errors:
```bash
docker compose -f docker/docker-compose.yaml logs runtime
```

### Issue: Changes not reflected

**Solution**: 
- Verify volume is mounted: `docker compose exec runtime ls -la /app`
- For dependency changes, rebuild: `docker compose up runtime --build`

## Documentation References

- **Runtime Setup Guide**: `docker/RUNTIME_SETUP.md`
- **Application README**: `runtime/README.md`
- **Emmett Documentation**: `/emmett_documentation/`

## Date Created

October 11, 2025

