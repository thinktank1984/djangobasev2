# Agents Tasks Queue

A comprehensive PostgreSQL-based task scheduling system designed for AI agents and automated workflows.

## 🚀 Quick Start

```bash
# Navigate to the tasks queue directory
cd agents_tasks_queue

# Start the task queue worker (first run will auto-install PostgreSQL)
./pgq-cmd run

# Schedule your first task
./pgq-cmd schedule "*/5 * * * *" --name heartbeat -- ./examples/heartbeat.sh

# List scheduled tasks
./pgq-cmd list

# Run immediate task
./pgq-cmd enqueue --name test -- echo "Hello from Agents Tasks Queue!"
```

## 📁 Directory Structure

```
agents_tasks_queue/
├── README.md                    # This file
├── pgq-cmd                     # Main scheduler script (executable)
├── config.json                 # Configuration file
├── pgq-cmd-tasks-queue.md      # Comprehensive documentation
├── examples/                   # Example scripts and data
│   ├── heartbeat.sh           # System monitoring script
│   ├── greet_user.sh          # User greeting script
│   └── users.json             # Sample data for fan-out tasks
├── logs/                      # Task logs directory
├── test_pgq_setup.sh          # Setup validation script
└── README-PGQ.md              # Implementation details
```

## 🔧 Features

- **Self-contained**: No external PostgreSQL needed
- **Auto-setup**: Virtual environment and schema creation
- **JSON configuration**: Customizable logging and settings
- **Task naming**: Optional user-defined names
- **Fan-out scheduling**: JSON array support for multiple tasks
- **Process isolation**: Separate processes per job
- **Pipeline logging**: Configurable log processing
- **One-off tasks**: Immediate task execution
- **Monitoring**: Task listing and dashboard access

## 🎯 Use Cases for AI Agents

### 1. Agent Health Monitoring
```bash
# Schedule agent heartbeat every minute
./pgq-cmd schedule "* * * * *" --name agent-heartbeat -- ./scripts/check_agent_status.sh
```

### 2. Batch Processing
```bash
# Process multiple data files simultaneously
./pgq-cmd schedule "0 */2 * * *" --name batch-process --array-json data/batch_jobs.json -- python scripts/process_data.py --job
```

### 3. Periodic Model Training
```bash
# Schedule daily model retraining
./pgq-cmd schedule "0 3 * * *" --name model-training -- python scripts/train_model.py
```

### 4. API Rate Limiting
```bash
# Schedule API calls within rate limits
./pgq-cmd schedule "*/10 * * * *" --name api-calls -- python scripts/make_api_calls.py
```

## 📖 Documentation

- **[Full Documentation](pgq-cmd-tasks-queue.md)** - Complete feature documentation
- **[Implementation Details](README-PGQ.md)** - Technical implementation notes
- **[Example Scripts](examples/)** - Ready-to-use task examples

## 🧪 Validation

Run the setup validation test:

```bash
cd agents_tasks_queue
./test_pgq_setup.sh
```

## 🔗 Integration

This tasks queue system can be easily integrated with:
- AI agent frameworks
- Django applications
- Python automation scripts
- CI/CD pipelines
- Microservices architectures

## 📊 Monitoring

- **Task listing**: `./pgq-cmd list`
- **Live dashboard**: `./.pgqvenv/bin/pgq dashboard`
- **Log viewing**: `tail -f logs/pgq.log`
- **Individual task logs**: `ls logs/`

## 🔄 Next Steps

1. **Customize configuration**: Edit `config.json` for your environment
2. **Create agent-specific scripts**: Add your automation tasks to `examples/`
3. **Set up monitoring**: Configure dashboards and alerts
4. **Scale horizontally**: Deploy multiple workers for high-throughput scenarios

---

**The Agents Tasks Queue is ready for production use with your AI agent workflows!** 🚀