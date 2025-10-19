"""
Custom exception handling and logging utilities.
"""

import logging
import traceback
from contextlib import contextmanager
from functools import wraps
from django.utils import timezone

from .utils import log_error, create_log_entry


class AuditLogException(Exception):
    """Base exception for audit logging related errors."""
    pass


def log_function_call(level='DEBUG', category='system', include_args=False, include_result=False):
    """
    Decorator to automatically log function calls.

    Args:
        level (str): Log level for the entry
        category (str): Log category
        include_args (bool): Whether to include function arguments in metadata
        include_result (bool): Whether to include function result in metadata
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = timezone.now()
            function_name = f"{func.__module__}.{func.__name__}"

            # Build metadata
            metadata = {
                'function': function_name,
                'module': func.__module__,
            }

            if include_args:
                metadata['args'] = str(args)[:500]  # Truncate long args
                metadata['kwargs'] = str(kwargs)[:500]

            try:
                result = func(*args, **kwargs)

                # Calculate execution time
                duration = (timezone.now() - start_time).total_seconds()
                metadata['duration_seconds'] = duration
                metadata['success'] = True

                if include_result:
                    metadata['result'] = str(result)[:200]  # Truncate long results

                create_log_entry(
                    level=level,
                    category=category,
                    message=f"Function call completed: {function_name}",
                    metadata=metadata
                )

                return result

            except Exception as e:
                duration = (timezone.now() - start_time).total_seconds()
                metadata['duration_seconds'] = duration
                metadata['success'] = False
                metadata['exception_type'] = type(e).__name__
                metadata['exception_message'] = str(e)

                log_error(
                    message=f"Function call failed: {function_name}",
                    exception=e,
                    metadata=metadata
                )
                raise

        return wrapper
    return decorator


@contextmanager
def log_operation(operation_name, level='INFO', category='audit', user_id=None):
    """
    Context manager to log an operation with start and end.

    Args:
        operation_name (str): Name of the operation
        level (str): Log level
        category (str): Log category
        user_id (int): User ID performing the operation
    """
    start_time = timezone.now()
    operation_id = f"{operation_name}_{int(start_time.timestamp())}"

    # Log operation start
    create_log_entry(
        level=level,
        category=category,
        message=f"Operation started: {operation_name}",
        user_id=user_id,
        metadata={
            'operation': operation_name,
            'operation_id': operation_id,
            'phase': 'started',
            'start_time': start_time.isoformat(),
        }
    )

    try:
        yield operation_id

        # Log successful completion
        duration = (timezone.now() - start_time).total_seconds()
        create_log_entry(
            level=level,
            category=category,
            message=f"Operation completed: {operation_name}",
            user_id=user_id,
            metadata={
                'operation': operation_name,
                'operation_id': operation_id,
                'phase': 'completed',
                'duration_seconds': duration,
                'success': True,
            }
        )

    except Exception as e:
        # Log operation failure
        duration = (timezone.now() - start_time).total_seconds()
        log_error(
            message=f"Operation failed: {operation_name}",
            exception=e,
            user_id=user_id,
            metadata={
                'operation': operation_name,
                'operation_id': operation_id,
                'phase': 'failed',
                'duration_seconds': duration,
                'success': False,
            }
        )
        raise


def log_database_operation(operation_type, table_name, record_count=1, user_id=None, **kwargs):
    """
    Log database operations.

    Args:
        operation_type (str): Type of operation (insert, update, delete, select)
        table_name (str): Name of the database table
        record_count (int): Number of records affected
        user_id (int): User ID performing the operation
        **kwargs: Additional metadata
    """
    metadata = {
        'operation_type': operation_type,
        'table_name': table_name,
        'record_count': record_count,
    }
    metadata.update(kwargs)

    create_log_entry(
        level='DEBUG',
        category='audit',
        message=f"Database {operation_type} on {table_name}: {record_count} records",
        user_id=user_id,
        metadata=metadata
    )


def log_security_event(event_type, description, severity='INFO', user_id=None,
                      ip_address=None, user_agent=None, **metadata):
    """
    Log security-related events.

    Args:
        event_type (str): Type of security event
        description (str): Description of the event
        severity (str): Security level (INFO, WARN, ERROR, CRITICAL)
        user_id (int): User ID involved (if applicable)
        ip_address (str): IP address involved
        user_agent (str): User agent string
        **metadata: Additional security metadata
    """
    # Map security severity to log level
    level_mapping = {
        'INFO': 'INFO',
        'WARN': 'WARN',
        'ERROR': 'ERROR',
        'CRITICAL': 'CRITICAL',
    }
    level = level_mapping.get(severity, 'INFO')

    security_metadata = {
        'security_event': True,
        'event_type': event_type,
        'security_severity': severity,
    }
    security_metadata.update(metadata)

    create_log_entry(
        level=level,
        category='auth',
        message=f"Security event - {event_type}: {description}",
        user_id=user_id,
        metadata=security_metadata,
        ip_address=ip_address,
        user_agent=user_agent
    )


class OperationLogger:
    """
    A class for logging complex operations with multiple steps.
    """

    def __init__(self, operation_name, user_id=None, request_id=None):
        self.operation_name = operation_name
        self.user_id = user_id
        self.request_id = request_id
        self.start_time = timezone.now()
        self.steps = []

    def log_step(self, step_name, message, level='INFO', metadata=None):
        """Log a step within the operation."""
        step_data = {
            'step': step_name,
            'message': message,
            'level': level,
            'timestamp': timezone.now(),
            'metadata': metadata or {},
        }
        self.steps.append(step_data)

        create_log_entry(
            level=level,
            category='system',
            message=f"{self.operation_name} - {step_name}: {message}",
            user_id=self.user_id,
            request_id=self.request_id,
            metadata={
                'operation': self.operation_name,
                'step': step_name,
                'step_number': len(self.steps),
                **(metadata or {})
            }
        )

    def complete(self, success=True, final_metadata=None):
        """Complete the operation and log summary."""
        duration = (timezone.now() - self.start_time).total_seconds()

        metadata = {
            'operation': self.operation_name,
            'duration_seconds': duration,
            'total_steps': len(self.steps),
            'success': success,
            'steps': [step['step'] for step in self.steps],
        }

        if final_metadata:
            metadata.update(final_metadata)

        level = 'INFO' if success else 'ERROR'
        status = 'completed' if success else 'failed'

        create_log_entry(
            level=level,
            category='system',
            message=f"Operation {status}: {self.operation_name} ({duration:.2f}s, {len(self.steps)} steps)",
            user_id=self.user_id,
            request_id=self.request_id,
            metadata=metadata
        )

        return success