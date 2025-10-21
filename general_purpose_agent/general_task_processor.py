#!/usr/bin/env python3
"""
General-Purpose Task Processor
A universal task processing system that executes migration and generation tasks
from JSON configuration files with embedded instructions and rules.
"""

import argparse
import sys
import json
import os
import time
import redis
import threading
import subprocess
import logging
import uuid
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from config.config_utils import ConfigManager

# Import Celery components (celery_app imports execute_general_purpose_task lazily to avoid circular import)
from agents.celery_app import celery_app, general_purpose_task, initialize_services

# Redis connection for real-time log streaming
try:
    redis_client = redis.Redis(host='127.0.0.1', port=6379, db=1, decode_responses=True)
    redis_client.ping()  # Test connection
except redis.ConnectionError:
    redis_client = None

# Colored Logging Formatter
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and better formatting"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{self.BOLD}{levelname}{self.RESET}"

        message = super().format(record)

        if levelname in ['ERROR', 'WARNING']:
            message = f"\n{'='*80}\n{message}\n{'='*80}"

        return message

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.handlers = [handler]


# ============================================================================
# TASK EXECUTION LOGIC (Consolidated from task_executor.py)
# ============================================================================

def execute_general_purpose_task(task_config: dict, database_name: str, shared_rules_path: str = None):
    """
    Execute a general-purpose task with embedded or external instructions and rules.

    Args:
        task_config: Dictionary containing:
            - task_type: Type of task (e.g., 'crud_service', 'vba_migration', etc.)
            - task_data: Data specific to the task
            - instructions: Instructions for Claude to follow
            - rules: Optional rules content (can be string or path to .md file)
            - rules_file: Optional path to external rules file
            - output_folder: Optional output folder override
            - log_folder_key: Optional config key for log folder (defaults to 'logs_folder')
        database_name: Database name for configuration resolution
        shared_rules_path: Optional path to shared rules file for all tasks
    """
    logging.info("--- execute_general_purpose_task entered ---")

    task_type = task_config.get('task_type', 'unknown')
    task_data = task_config.get('task_data', {})
    instructions = task_config.get('instructions', '')
    rules_content = task_config.get('rules', '')
    rules_file = task_config.get('rules_file', None)
    log_folder_key = task_config.get('log_folder_key', 'logs_folder')

    if not instructions:
        raise Exception("No instructions provided in task configuration")

    # Load rules from file if specified (priority: shared_rules_path > rules_file > embedded rules)
    if shared_rules_path and os.path.exists(shared_rules_path):
        logging.info(f"Loading shared rules from: {shared_rules_path}")
        with open(shared_rules_path, 'r', encoding='utf-8') as f:
            rules_content = f.read()
    elif rules_file and os.path.exists(rules_file):
        logging.info(f"Loading task-specific rules from: {rules_file}")
        with open(rules_file, 'r', encoding='utf-8') as f:
            rules_content = f.read()
    elif rules_content and os.path.exists(rules_content):
        # If rules looks like a file path, try to load it
        logging.info(f"Loading rules from path in 'rules' field: {rules_content}")
        with open(rules_content, 'r', encoding='utf-8') as f:
            rules_content = f.read()

    logging.info(f"--- execute_general_purpose_task started for type: {task_type} ---")

    task_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    task_identifier = task_config.get('task_identifier', task_data.get('identifier', task_type))
    log_filename = f"{task_identifier}_{task_type}_logs_{timestamp}_{task_id}.log"

    config_path = Path(__file__).resolve().parents[2] / 'config' / 'config.json'
    config_manager = ConfigManager(config_path=config_path, database_name=database_name)
    logging.info("--- ConfigManager instantiated ---")

    logs_folder = config_manager.get_processed_value(log_folder_key)
    log_file_path = (Path(logs_folder) / log_filename).resolve()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = None
    for attempt in range(3):
        try:
            file_handler = logging.FileHandler(log_file_path)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            break
        except (FileNotFoundError, OSError, PermissionError) as e:
            if attempt < 2:
                logging.warning(f"Attempt {attempt + 1} failed to create log file handler for {log_file_path}: {e}. Retrying...")
                time.sleep(0.1)
            else:
                logging.error(f"Failed to create log file handler for {log_file_path} after 3 attempts: {e}")
                raise

    task_logger = logging.getLogger()
    task_logger.addHandler(file_handler)

    logging.info(f"\n🔧 Starting task execution\n   Type: {task_type}\n   Data: {json.dumps(task_data, indent=2)}\n   Log file: {log_file_path}")

    try:
        target_folder = config_manager.get_target_blazor_app_server_folder()

        if not target_folder or not os.path.exists(target_folder):
            logging.error(f"Target Blazor app server folder not found or does not exist: {target_folder}")
            raise Exception(f"Target Blazor app server folder not found or does not exist: {target_folder}")

        # Serialize task_data as JSON for the prompt (single line)
        task_data_json = json.dumps(task_data)

        # Format instructions - use task_data_json as 'name' placeholder
        prompt = instructions.format(name=task_data_json)

        if rules_content:
            # Don't format rules - let Claude interpret the placeholders
            # Rules are documentation/examples, not templates to be filled
            prompt = f"{prompt}\n\n## Rules\n{rules_content}"

        # Use the current environment for the subprocess
        env = os.environ.copy()

        # Write prompt to a temporary file to avoid shell escaping issues
        temp_prompt_file = log_file_path.parent / f"temp_prompt_{task_id}.txt"
        with open(temp_prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt)

        # Build command string using cat to pipe the prompt file to claude
        command = f'cat "{temp_prompt_file}" | claude --model claude-sonnet-4-5@20250929 --verbose --output-format stream-json --dangerously-skip-permissions > "{log_file_path}"'

        logging.info(f"\n📂 Working Directory: {target_folder}\n🚀 Executing command:\n{'-'*60}\n{command}\n{'-'*60}")
        logging.info(f"📝 Prompt written to: {temp_prompt_file}")
        logging.info("--- about to run claude command ---")
        # Execute command with shell=True to handle redirection properly
        result = subprocess.run(command, shell=True, cwd=target_folder, env=env, capture_output=True, text=True)
        logging.info("--- claude command finished ---")

        # Read the output from the log file
        with open(log_file_path, 'r') as f:
            claude_output = f.read()

        # Detailed logging of stdout and stderr
        logging.info(f"--- Claude CLI output (from log file) ---\n{claude_output}")
        logging.info(f"--- Claude CLI stderr ---\n{result.stderr}")

        # Try to parse the output as JSON
        try:
            output_data = json.loads(claude_output)

            # Ensure target_folder is set
            if not target_folder:
                logging.error("Target folder is not configured. Cannot write files.")
                raise Exception("Target folder is not configured. Cannot write files.")

            # Write each file from the JSON output
            for file_path, file_content in output_data.items():
                # Construct the full path relative to the target folder
                full_path = os.path.join(target_folder, file_path)


                # Write the content to the file
                with open(full_path, 'w') as f:
                    f.write(file_content)
                logging.info(f"   📄 Saved generated code to: {full_path}")

        except json.JSONDecodeError:
            logging.warning("   ⚠️  Claude CLI output was not valid JSON. Saving raw output to log file.")
            with open(log_file_path, 'w') as f:
                f.write(result.stdout)
        except Exception as e:
            logging.error(f"   ❌ An error occurred while processing the output: {e}")
            with open(log_file_path, 'w') as f:
                f.write(result.stdout)


        if result.stderr:
            logging.warning(f"Claude CLI stderr:\n{result.stderr}")

        logging.info(f"\n✅ Successfully completed task: {task_type}\n")

        return {
            'status': 'success',
            'task_type': task_type,
            'task_data': task_data,
            'log_file': str(log_file_path)
        }

    except Exception as e:
        logging.error(f"--- execute_general_purpose_task error: {e} ---")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred in execute_general_purpose_task for task '{task_type}': {e}")
        logging.error(f"--- execute_general_purpose_task error: {e} ---")
        raise
    finally:
        try:
            if 'temp_prompt_file' in locals() and temp_prompt_file.exists():
                temp_prompt_file.unlink()
                logging.info(f"🧹 Cleaned up temporary prompt file: {temp_prompt_file}")
        except Exception as cleanup_error:
            logging.warning(f"Failed to clean up temporary file: {cleanup_error}")

        if 'file_handler' in locals() and file_handler:
            try:
                task_logger.removeHandler(file_handler)
                file_handler.close()
                if 'log_file_path' in locals():
                    logging.info(f"📄 Log saved to: {log_file_path}")
            except Exception as handler_cleanup_error:
                logging.warning(f"Failed to clean up file handler: {handler_cleanup_error}")

        logging.info("--- execute_general_purpose_task finished ---")


# ============================================================================
# CLI FUNCTIONS
# ============================================================================

def ensure_events_and_monitoring():
    """Ensure Celery events are enabled and monitoring is active."""
    try:
        # Enable events
        celery_app.control.enable_events()
        print("✅ Celery events enabled")

        # Check if workers are running
        active_workers = celery_app.control.inspect().active()
        if active_workers:
            print(f"✅ Active workers: {list(active_workers.keys())}")
        else:
            print("⚠️  No active workers found")

        return True
    except Exception as e:
        print(f"⚠️  Could not enable events: {e}")
        return False

def get_task_logs(task_id: str, from_redis: bool = True) -> list:
    """Fetch full task logs from Redis or Celery result."""
    logs = []

    # Try Redis first for complete real-time logs
    if from_redis and redis_client:
        try:
            redis_key = f"task_logs:{task_id}"
            redis_logs = redis_client.lrange(redis_key, 0, -1)
            logs = [json.loads(log) for log in reversed(redis_logs)]  # Reverse to get chronological order
        except (redis.RedisError, json.JSONDecodeError):
            pass  # Fall back to Celery result

    # Fall back to Celery result if Redis fails or no Redis logs
    if not logs:
        result = celery_app.AsyncResult(task_id)
        if result.state == 'SUCCESS' and result.result:
            logs = result.result.get('logs', [])
        elif result.state == 'PROGRESS' and result.info:
            logs = result.info.get('full_logs', result.info.get('recent_logs', []))

    return logs

def display_logs(logs: list, show_all: bool = False):
    """Display task logs in a formatted way."""
    if not logs:
        print("   No logs available")
        return

    display_logs_list = logs if show_all else logs[-10:]  # Show last 10 by default

    for log_entry in display_logs_list:
        timestamp = log_entry.get('timestamp', 'N/A')
        level = log_entry.get('level', 'INFO')
        message = log_entry.get('message', '')

        # Color code by level
        if level == 'ERROR':
            print(f"   🔴 [{timestamp}] {level}: {message}")
        elif level == 'WARNING':
            print(f"   🟡 [{timestamp}] {level}: {message}")
        else:
            print(f"   🔵 [{timestamp}] {level}: {message}")

def stream_logs_from_redis(task_id: str, stop_event: threading.Event):
    """Stream logs from Redis in real-time."""
    if not redis_client:
        print("   ⚠️  Redis not available for real-time log streaming")
        return

    redis_key = f"task_logs:{task_id}"
    last_count = 0

    print(f"   📺 Streaming logs from Redis (key: {redis_key})")

    while not stop_event.is_set():
        try:
            current_count = redis_client.llen(redis_key)
            if current_count > last_count:
                # Get new logs
                new_logs = redis_client.lrange(redis_key, 0, current_count - last_count - 1)
                for log_data in reversed(new_logs):  # Reverse to show in chronological order
                    try:
                        log_entry = json.loads(log_data)
                        timestamp = log_entry.get('timestamp', 'N/A')
                        level = log_entry.get('level', 'INFO')
                        message = log_entry.get('message', '')

                        # Color code by level
                        if level == 'ERROR':
                            print(f"   🔴 [{timestamp}] {level}: {message}")
                        elif level == 'WARNING':
                            print(f"   🟡 [{timestamp}] {level}: {message}")
                        else:
                            print(f"   🔵 [{timestamp}] {level}: {message}")
                    except json.JSONDecodeError:
                        continue
                last_count = current_count

            time.sleep(1)  # Check for new logs every second

        except redis.RedisError:
            break

def check_task_status(task_id: str) -> dict:
    """Check the status of a specific task."""
    result = celery_app.AsyncResult(task_id)

    status_info = {
        'task_id': task_id,
        'state': result.state,
        'ready': result.ready()
    }

    if result.state == 'PENDING':
        status_info['status'] = 'Task is waiting to be processed'
    elif result.state == 'PROGRESS':
        status_info['status'] = 'Task is being processed'
        status_info['progress'] = result.info
    elif result.state == 'SUCCESS':
        status_info['status'] = 'Task completed successfully'
        status_info['result'] = result.result
    else:  # FAILURE
        status_info['status'] = 'Task failed'
        status_info['error'] = str(result.info)

    return status_info

def load_task_from_convention(task_name: str, base_path: Path = None) -> dict:
    """
    Load task configuration using naming convention.

    Convention:
        {task_name}_array.json      - Array of objects to process
        {task_name}_instructions.json - Instructions template
        {task_name}_rules.md        - Rules file

    Args:
        task_name: Name of the task (e.g., 'model', 'page', 'vba')
        base_path: Base directory (defaults to current script directory)

    Returns:
        dict: Task configuration with tasks array
    """
    if base_path is None:
        base_path = Path(__file__).parent

    array_file = base_path / f"{task_name}_array.json"
    instructions_file = base_path / f"{task_name}_instructions.json"
    rules_file = base_path / f"{task_name}_rules.md"

    # Validate files exist
    if not array_file.exists():
        print(f"❌ Error: Array file not found: {array_file}")
        sys.exit(1)

    if not instructions_file.exists():
        print(f"❌ Error: Instructions file not found: {instructions_file}")
        sys.exit(1)

    # Rules file is optional
    has_rules = rules_file.exists()

    # Load array
    try:
        with open(array_file, 'r') as f:
            objects_array = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {array_file}: {e}")
        sys.exit(1)

    if not isinstance(objects_array, list):
        print(f"❌ Error: {array_file} must contain a JSON array")
        sys.exit(1)

    # Load instructions
    try:
        with open(instructions_file, 'r') as f:
            instructions_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {instructions_file}: {e}")
        sys.exit(1)

    # Get instructions from the file (look for key matching task_name or use default)
    instructions_key = f"{task_name}_instructions"
    if instructions_key in instructions_data:
        instructions_list = instructions_data[instructions_key]
    elif "default_instructions" in instructions_data:
        instructions_list = instructions_data["default_instructions"]
    else:
        print(f"❌ Error: No '{instructions_key}' or 'default_instructions' found in {instructions_file}")
        sys.exit(1)

    # Join instructions if it's a list
    if isinstance(instructions_list, list):
        instructions = "\n".join(instructions_list)
    else:
        instructions = instructions_list

    # Create tasks array from objects
    tasks = []
    for obj in objects_array:
        # Handle both simple strings and objects
        if isinstance(obj, str):
            # Simple string - use as both identifier and single data field
            task_data = {
                "identifier": obj,
                "name": obj  # Generic 'name' field that can be used in templates
            }
            identifier = obj
        elif isinstance(obj, dict):
            # Object - use as-is, don't modify
            task_data = obj.copy()
            # Determine identifier for logging/filename purposes only
            if "identifier" in obj:
                identifier = obj["identifier"]
            else:
                first_value = str(list(obj.values())[0]) if obj else task_name
                identifier = first_value.replace('/', '_').replace('\\', '_')
        else:
            print(f"⚠️  Warning: Skipping invalid item in array (must be string or object): {obj}")
            continue

        task_config = {
            "task_type": task_name,
            "task_data": task_data,
            "task_identifier": identifier,
            "instructions": instructions
        }

        # Add rules file path if it exists
        if has_rules:
            task_config["rules_file"] = str(rules_file)

        tasks.append(task_config)

    print(f"✅ Loaded {len(tasks)} tasks from convention-based files")
    print(f"   📋 Array: {array_file}")
    print(f"   📝 Instructions: {instructions_file}")
    if has_rules:
        print(f"   📜 Rules: {rules_file}")

    return {
        "database_name": "targetdbname",
        "tasks": tasks
    }


def load_json_config(json_path: str) -> dict:
    """Load and validate JSON configuration file."""
    if not os.path.exists(json_path):
        print(f"❌ Error: Configuration file not found: {json_path}")
        sys.exit(1)

    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format in {json_path}: {e}")
        sys.exit(1)

    if 'tasks' not in config:
        print(f"❌ Error: Missing 'tasks' array in {json_path}")
        print("Expected format:")
        print("""
{
  "tasks": [
    {
      "task_type": "crud_service",
      "task_data": {...},
      "instructions": "...",
      "rules": "..."
    }
  ]
}""")
        sys.exit(1)

    if not isinstance(config['tasks'], list) or len(config['tasks']) == 0:
        print(f"❌ Error: 'tasks' must be a non-empty list")
        sys.exit(1)

    return config

def wait_for_task_completion(task_id: str, task_description: str = "Task", show_logs: bool = True, stream_redis: bool = True) -> dict:
    """Wait for a Celery task to complete and return the result."""
    print(f"⏳ Waiting for {task_description.lower()} to complete...")
    print(f"   Task ID: {task_id}")
    print(f"   Monitor at: http://localhost:5555/task/{task_id}")

    result = celery_app.AsyncResult(task_id)
    last_log_count = 0
    last_status = None
    stop_event = threading.Event()
    redis_thread = None

    # Start Redis log streaming if enabled and available
    if show_logs and stream_redis and redis_client:
        print(f"   🔄 Starting real-time log streaming from Redis...")
        redis_thread = threading.Thread(target=stream_logs_from_redis, args=(task_id, stop_event))
        redis_thread.daemon = True
        redis_thread.start()

    # Wait for completion with progress updates
    while not result.ready():
        if result.state == 'PROGRESS':
            meta = result.info or {}
            status = meta.get('status', 'Processing...')
            log_count = meta.get('log_count', 0)

            # Only print status if it has changed
            current_status = f"{status} ({log_count} log entries)"
            if current_status != last_status:
                print(f"   Status: {current_status}")
                last_status = current_status

            # Show new logs if Redis streaming is not available
            if show_logs and not (stream_redis and redis_client):
                full_logs = meta.get('full_logs', meta.get('recent_logs', []))
                if len(full_logs) > last_log_count:
                    print(f"   📄 New logs:")
                    display_logs(full_logs[last_log_count:], show_all=True)
                    last_log_count = len(full_logs)
        time.sleep(2)

    # Stop Redis streaming
    if redis_thread:
        stop_event.set()
        redis_thread.join(timeout=2)

    # Task completed - show final result
    if result.successful():
        final_result = result.result
        print(f"✅ {task_description} completed successfully!")

        # Show final logs if not already streaming
        if show_logs and not (stream_redis and redis_client):
            logs = get_task_logs(task_id, from_redis=False)  # Get from Celery result
            if logs:
                print(f"📄 Complete execution logs:")
                display_logs(logs, show_all=True)

        return final_result
    else:
        error = str(result.info) if result.info else "Unknown error"
        print(f"❌ {task_description} failed: {error}")

        # Show any available logs from failed task
        if show_logs:
            logs = get_task_logs(task_id)
            if logs:
                print(f"📄 Error logs:")
                display_logs(logs, show_all=True)

        return {'status': 'failed', 'error': error}

def wait_for_batch_completion(task_ids: list) -> dict:
    """Wait for multiple tasks to complete."""
    print(f"⏳ Waiting for {len(task_ids)} tasks to complete...")

    results = {'successful': [], 'failed': []}
    completed_tasks = set()

    tasks = {tid: celery_app.AsyncResult(tid) for tid in task_ids}

    while len(completed_tasks) < len(task_ids):
        for task_id, task in tasks.items():
            if task_id in completed_tasks:
                continue

            if task.ready():
                completed_tasks.add(task_id)
                try:
                    # Use get with a timeout to ensure result is fetched
                    result_data = task.get(timeout=30)

                    if result_data and result_data.get('status') == 'success':
                        results['successful'].append({
                            'task_id': task_id,
                            'task_type': result_data.get('task_type', 'unknown'),
                            'result': result_data
                        })
                        print(f"✅ [{len(completed_tasks)}/{len(task_ids)}] Completed: {result_data.get('task_type', task_id)}")
                    else:
                        error_message = result_data.get('error', 'Unknown error') if result_data else 'Task returned no result'
                        results['failed'].append({
                            'task_id': task_id,
                            'error': error_message,
                            'result': result_data
                        })
                        print(f"❌ [{len(completed_tasks)}/{len(task_ids)}] Failed: {task_id} - {error_message}")
                except Exception as e:
                    results['failed'].append({
                        'task_id': task_id,
                        'error': str(e)
                    })
                    print(f"❌ [{len(completed_tasks)}/{len(task_ids)}] Error retrieving result for {task_id}: {e}")

        if len(completed_tasks) < len(task_ids):
            time.sleep(2)

    return results

def execute_task_with_celery(task_config: dict, database_name: str, shared_rules_path: str = None, show_logs: bool = True, stream_redis: bool = True) -> dict:
    """Execute a task using Celery for parallel processing."""
    task_type = task_config.get('task_type', 'unknown')
    print(f"🚀 Submitting {task_type} task to Celery...")

    # Submit task to Celery
    task = general_purpose_task.delay(task_config, database_name, shared_rules_path)
    print(f"   Task ID: {task.id}")

    # Wait for completion
    return wait_for_task_completion(task.id, task_type, show_logs, stream_redis)

def execute_tasks_batch_with_celery(tasks: list, database_name: str, shared_rules_path: str = None) -> dict:
    """Execute multiple tasks using Celery for parallel processing."""
    print(f"🚀 Submitting {len(tasks)} tasks to Celery...")

    task_ids = []
    for task_config in tasks:
        task = general_purpose_task.delay(task_config, database_name, shared_rules_path)
        task_ids.append(task.id)
        task_type = task_config.get('task_type', 'unknown')
        print(f"   Submitted: {task_type} (Task: {task.id})")

    # Wait for all tasks to complete
    return wait_for_batch_completion(task_ids)

def cleanup_logs(log_types=None):
    """Remove specific log files before task execution.

    Args:
        log_types: List of log types to clean. Options: 'main', 'general'
                  If None, cleans all log types.
    """
    if log_types is None:
        log_types = ['main', 'general']

    print("🧹 Cleaning up log files...")

    removed_count = 0

    # Main log files to clean
    if 'main' in log_types:
        log_files = [
            project_root / "logs" / "celery_tasks.log",
            project_root / "logs" / "celery_worker.log",
            project_root / "logs" / "fastapi.log",
            project_root / "logs" / "flower.log"
        ]

        # Remove individual log files
        for log_file in log_files:
            if log_file.exists():
                try:
                    log_file.unlink()
                    removed_count += 1
                except OSError as e:
                    print(f"   ⚠️  Could not remove {log_file}: {e}")

    # Clean old general purpose task log files (keep directory)
    if 'general' in log_types:
        general_logs_dir = project_root / "logs" / "general_tasks"
        if general_logs_dir.exists():
            try:
                for log_file in general_logs_dir.glob("*.log"):
                    log_file.unlink()
                    removed_count += 1
                print(f"   🗂️  Cleaned general task log files")
            except OSError as e:
                print(f"   ⚠️  Could not clean general log files in {general_logs_dir}: {e}")

    # Clear Redis log keys if Redis is available
    if redis_client:
        try:
            # Get all task log keys
            log_keys = redis_client.keys("task_logs:*")
            if log_keys:
                redis_client.delete(*log_keys)
                print(f"   🔑 Cleared {len(log_keys)} Redis log keys")
        except redis.RedisError as e:
            print(f"   ⚠️  Could not clear Redis logs: {e}")

    print(f"✅ Log cleanup completed. Removed {removed_count} log files")

def kill_all_tasks():
    """Kill all running Celery tasks and revoke pending tasks."""
    print("🛑 Killing all Celery tasks...")

    try:
        # Get active tasks from all workers
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()

        if active_tasks:
            all_task_ids = []
            for worker, tasks in active_tasks.items():
                task_ids = [task['id'] for task in tasks]
                all_task_ids.extend(task_ids)
                print(f"   📋 Worker {worker}: {len(task_ids)} active tasks")

            if all_task_ids:
                print(f"   🚫 Revoking {len(all_task_ids)} active tasks...")
                celery_app.control.revoke(all_task_ids, terminate=True)
                print(f"   ✅ Revoked {len(all_task_ids)} tasks")
            else:
                print("   ℹ️  No active tasks found")
        else:
            print("   ℹ️  No active workers or tasks found")

        # Get scheduled tasks and revoke them too
        scheduled_tasks = inspect.scheduled()
        if scheduled_tasks:
            all_scheduled_ids = []
            for worker, tasks in scheduled_tasks.items():
                task_ids = [task['request']['id'] for task in tasks]
                all_scheduled_ids.extend(task_ids)
                print(f"   📅 Worker {worker}: {len(task_ids)} scheduled tasks")

            if all_scheduled_ids:
                print(f"   🚫 Revoking {len(all_scheduled_ids)} scheduled tasks...")
                celery_app.control.revoke(all_scheduled_ids, terminate=True)
                print(f"   ✅ Revoked {len(all_scheduled_ids)} scheduled tasks")

        # Clear Redis task logs if available
        if redis_client:
            try:
                log_keys = redis_client.keys("task_logs:*")
                if log_keys:
                    redis_client.delete(*log_keys)
                    print(f"   🧹 Cleared {len(log_keys)} Redis log keys")
            except redis.RedisError as e:
                print(f"   ⚠️  Could not clear Redis logs: {e}")

        print("✅ All tasks killed successfully")

    except Exception as e:
        print(f"❌ Error killing tasks: {e}")
        sys.exit(1)

def ensure_worker_is_running():
    """Check if the Celery worker is running and start it if not."""
    worker_pid_file = project_root / "logs" / "celery_worker.pid"

    if worker_pid_file.exists():
        try:
            with open(worker_pid_file, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)
            print(f"✅ Celery worker is already running with PID: {pid}")
            return
        except (ValueError, OSError):
            print("⚠️  Stale PID file found. Starting a new worker.")
            worker_pid_file.unlink()

    print("👷 Starting Celery worker in the background...")

    if not initialize_services():
        print(f"❌ Error: Failed to initialize Celery services.")
        sys.exit(1)

    print("✅ Worker started successfully.")

def process_tasks(config_file: str, show_logs: bool = True, stream_redis: bool = True, shared_rules_path: str = None):
    """Process all tasks from configuration file using Celery."""
    config = load_json_config(config_file)
    tasks = config['tasks']
    database_name = config.get("database_name", "targetdbname")

    print(f"📋 Loaded configuration from: {config_file}")
    print(f"📊 Processing {len(tasks)} tasks")
    if shared_rules_path:
        print(f"📜 Using shared rules from: {shared_rules_path}")

    if len(tasks) == 1:
        print("🚀 Executing single task with Celery...")
        try:
            result = execute_task_with_celery(tasks[0], database_name, shared_rules_path, show_logs, stream_redis)

            if result.get('status') == 'success':
                print(f"✅ Task completed successfully")
            else:
                print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Task failed: {e}")
            sys.exit(1)
    else:
        print(f"🚀 Executing {len(tasks)} tasks in parallel with Celery...")
        try:
            results = execute_tasks_batch_with_celery(tasks, database_name, shared_rules_path)

            print(f"\n📊 Batch Processing Summary:")
            print(f"✅ Successful: {len(results['successful'])}/{len(tasks)}")
            print(f"❌ Failed: {len(results['failed'])}/{len(tasks)}")

            if results['failed']:
                print("\n❌ Failed tasks:")
                for failure in results['failed']:
                    print(f"   • {failure.get('task_id', 'unknown')}: {failure.get('error', 'Unknown error')}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
            sys.exit(1)

    print(f"\n🏁 All tasks completed successfully!")

def main():
    """CLI for general-purpose task processing using Redis-based Celery."""

    ensure_worker_is_running()

    print("🔄 Initializing Task Processor CLI...")
    ensure_events_and_monitoring()

    parser = argparse.ArgumentParser(
        description="General-Purpose Task Processor CLI with Redis-based Celery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process tasks from JSON config
  python task_processor_cli.py --process tasks_config.json

  # Kill all running tasks
  python task_processor_cli.py --kill-all-tasks

  # Run without showing logs during execution
  python task_processor_cli.py --process tasks_config.json --no-logs

JSON Configuration Format:
{
  "database_name": "mydb",
  "tasks": [
    {
      "task_type": "crud_service",
      "task_data": {
        "model_path": "Models/User.cs",
        "dbcontext_name": "AppDbContext"
      },
      "instructions": "Generate CRUD service...",
      "rules": "Follow these rules..."
    }
  ]
}

Features:
  • Uses Redis as message broker
  • Real-time task monitoring
  • Flower dashboard at http://localhost:5555
  • Generic task processing with embedded instructions
        """
    )

    parser.add_argument("--process", help="JSON configuration file for tasks")
    parser.add_argument("--task-name", help="Convention-based task name (e.g., 'model'). Will load {name}_array.json, {name}_instructions.json, {name}_rules.md")
    parser.add_argument("--folder-path", help="Base folder path for convention-based task files (defaults to script directory)")
    parser.add_argument("--shared-rules", help="Path to shared rules file (.md) to use for all tasks")
    parser.add_argument("--no-logs", action="store_true", help="Disable log display during task execution")
    parser.add_argument("--kill-all-tasks", action="store_true", help="Kill all running and scheduled Celery tasks")
    parser.add_argument("--status", help="Check status of task by ID")
    parser.add_argument("--logs", help="Get full logs for task by ID")
    parser.add_argument("--stream", help="Stream real-time logs for task by ID")
    parser.add_argument("--no-redis-stream", action="store_true", help="Disable Redis real-time log streaming")

    args = parser.parse_args()

    # Check task status if requested
    if args.status:
        print(f"🔍 Checking status for task: {args.status}")
        status = check_task_status(args.status)
        print(f"📊 Task Status:")
        print(f"   State: {status['state']}")
        print(f"   Ready: {status['ready']}")
        print(f"   Status: {status['status']}")
        if 'progress' in status:
            print(f"   Progress: {status['progress']}")
        if 'result' in status:
            print(f"   Result: {status['result']}")
        if 'error' in status:
            print(f"   Error: {status['error']}")
        return

    # Get full logs if requested
    if args.logs:
        print(f"📄 Fetching full logs for task: {args.logs}")
        logs = get_task_logs(args.logs)

        if logs:
            print(f"📄 Complete task logs ({len(logs)} entries):")
            display_logs(logs, show_all=True)
        else:
            print("   No logs available for this task")
        return

    # Stream real-time logs if requested
    if args.stream:
        print(f"📺 Starting real-time log stream for task: {args.stream}")
        stop_event = threading.Event()

        try:
            stream_logs_from_redis(args.stream, stop_event)
        except KeyboardInterrupt:
            print("\n   ⏹️  Log streaming stopped by user")
            stop_event.set()
        return

    if args.kill_all_tasks:
        kill_all_tasks()
        return

    # Require either --process or --task-name
    if not args.process and not args.task_name:
        print("❌ Error: Please provide either --process <config_file> or --task-name <name>")
        parser.print_help()
        sys.exit(1)

    if args.process and args.task_name:
        print("❌ Error: Cannot use both --process and --task-name. Choose one.")
        sys.exit(1)

    show_logs = not args.no_logs
    stream_redis = not args.no_redis_stream
    shared_rules_path = args.shared_rules

    cleanup_logs()

    # Load configuration based on mode
    if args.task_name:
        print(f"📋 Using convention-based loading for task: {args.task_name}")
        folder = Path(args.folder_path) if args.folder_path else None
        if folder:
            print(f"📁 Using custom folder path: {folder}")
        config = load_task_from_convention(args.task_name, base_path=folder)
        # Process tasks directly with the config
        tasks = config['tasks']
        database_name = config.get("database_name", "targetdbname")

        print(f"📊 Processing {len(tasks)} tasks")
        if shared_rules_path:
            print(f"📜 Using shared rules from: {shared_rules_path}")

        # Add shared_rules_path to each task if provided
        if shared_rules_path:
            for task in tasks:
                if 'shared_rules_path' not in task:
                    task['shared_rules_path'] = shared_rules_path

        if len(tasks) == 1:
            print("🚀 Executing single task with Celery...")
            try:
                result = execute_task_with_celery(tasks[0], database_name, shared_rules_path, show_logs, stream_redis)

                if result.get('status') == 'success':
                    print(f"✅ Task completed successfully")
                else:
                    print(f"❌ Task failed: {result.get('error', 'Unknown error')}")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Task failed: {e}")
                sys.exit(1)
        else:
            print(f"🚀 Executing {len(tasks)} tasks in parallel with Celery...")
            try:
                results = execute_tasks_batch_with_celery(tasks, database_name, shared_rules_path)

                print(f"\n📊 Batch Processing Summary:")
                print(f"✅ Successful: {len(results['successful'])}/{len(tasks)}")
                print(f"❌ Failed: {len(results['failed'])}/{len(tasks)}")

                if results['failed']:
                    print("\n❌ Failed tasks:")
                    for failure in results['failed']:
                        print(f"   • {failure.get('task_id', 'unknown')}: {failure.get('error', 'Unknown error')}")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ Batch processing failed: {e}")
                sys.exit(1)

        print(f"\n🏁 All tasks completed successfully!")

    else:
        process_tasks(args.process, show_logs, stream_redis, shared_rules_path)

if __name__ == "__main__":
    main()
