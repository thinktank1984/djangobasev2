# PGQ-Cmd Tasks Queue

A self-contained PostgreSQL-based task scheduler for the project with embedded PostgreSQL setup, automatic virtual environments, and comprehensive logging.

## Quick Start

```bash
# Start the worker
./pgq-cmd run

# Schedule a simple heartbeat task
./pgq-cmd schedule "*/5 * * * *" --name heartbeat -- ./examples/heartbeat.sh

# List all scheduled tasks
./pgq-cmd list

# Enqueue a one-off task
./pgq-cmd enqueue --name cleanup -- rm -rf /tmp/temp-files
```

## Features

- **Self-contained**: No external PostgreSQL needed (embedded setup)
- **Auto-setup**: Virtual environment and schema creation
- **Advanced logging**: Pipeline logging with JSON configuration
- **Task naming**: Optional user-defined or auto-generated names
- **Fan-out scheduling**: `--array-json` support for scheduling multiple tasks
- **Process isolation**: Separate processes per job
- **Live dashboard**: Built-in monitoring via `./.pgqvenv/bin/pgq dashboard`

## Configuration

The system uses `config.json` for configuration:

```json
{
  "log_dir": "logs",
  "pipeline": ["tee", "-a", "logs/pgq.log"],
  "pg_port": 5544
}
```

## Usage Examples

### Basic Scheduling

```bash
# Schedule heartbeat every 5 minutes
./pgq-cmd schedule "*/5 * * * *" --name heartbeat -- ./examples/heartbeat.sh

# Schedule daily backup
./pgq-cmd schedule "0 2 * * *" --name daily-backup -- ./scripts/backup.sh
```

### Fan-out Scheduling with JSON Arrays

```bash
# Schedule personalized greetings for multiple users
./pgq-cmd schedule "0 9 * * *" --name morning-greet --array-json examples/users.json -- ./examples/greet_user.sh --user
```

### One-off Tasks

```bash
# Run immediate cleanup task
./pgq-cmd enqueue --name cleanup -- ./scripts/cleanup.sh

# Send immediate notification
./pgq-cmd enqueue --name notify -- ./scripts/send-notification.sh "Task completed"
```

## Log Management

Each task creates its own log file:
```
logs/{task_name}-{timestamp}.log
```

All tasks also stream to the pipeline log:
```
logs/pgq.log
```

## Monitoring

- **View scheduled tasks**: `./pgq-cmd list`
- **View live dashboard**: `./.pgqvenv/bin/pgq dashboard`
- **Check logs**: `tail -f logs/pgq.log`

## Integration with Django

You can integrate pgq-cmd with Django tasks:

```python
# In your Django management command
import subprocess
import json

def schedule_task(command, schedule, name=None):
    cmd = ['./pgq-cmd', 'schedule', schedule]
    if name:
        cmd.extend(['--name', name])
    cmd.extend(['--'] + command)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0
```

## Troubleshooting

### PostgreSQL Issues
- Check `.pgdata/server.log` for database errors
- Ensure port 5544 is available
- Database auto-initializes on first run

### Python Environment
- Virtual environment auto-creates in `.pgqvenv`
- Dependencies auto-install on first run
- Use `./.pgqvenv/bin/python` for direct access

### Task Failures
- Check individual task logs in `logs/`
- Verify script permissions and paths
- Use `./pgq-cmd list` to see task status

## Advanced Usage

### Custom Pipeline Processing

Modify `config.json` to add custom log processing:

```json
{
  "log_dir": "logs",
  "pipeline": ["grep", "-i", "error", "|", "tee", "-a", "logs/errors.log"],
  "pg_port": 5544
}
```

### Task Priority

Set task priority when scheduling:

```bash
./pgq-cmd schedule "*/10 * * * *" --name high-priority --priority 10 -- ./scripts/critical-task.sh
```

## File Structure

```
├── pgq-cmd                 # Main scheduler script
├── config.json            # Configuration file
├── logs/                  # Task logs directory
├── examples/              # Example scripts
│   ├── heartbeat.sh      # System monitoring script
│   ├── greet_user.sh     # User greeting script
│   └── users.json        # Sample data for fan-out tasks
├── .pgbin/               # PostgreSQL binaries (auto-created)
├── .pgdata/              # PostgreSQL data (auto-created)
└── .pgqvenv/             # Python virtual environment (auto-created)
```