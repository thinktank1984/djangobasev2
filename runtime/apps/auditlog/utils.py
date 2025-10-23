"""
Utility functions for logging and creating log entries.
"""

import json
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import SystemLog
from .handlers import set_request_context, get_request_context


def create_log_entry(level, category, message, user_id=None, object_id=None,
                    metadata=None, request_id=None, ip_address=None, user_agent=None):
    """
    Create a SystemLog entry directly.

    Args:
        level (str): Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
        category (str): Log category (api, error, migration, audit, auth, system)
        message (str): Log message
        user_id (int, optional): User ID associated with the log entry
        object_id (int, optional): Object ID associated with the log entry
        metadata (dict, optional): Additional metadata
        request_id (str, optional): Request ID
        ip_address (str, optional): Client IP address
        user_agent (str, optional): Client user agent

    Returns:
        SystemLog: The created log entry
    """
    # Get request context if not provided
    if not any([request_id, ip_address, user_agent]):
        context = get_request_context()
        request_id = request_id or context.get('request_id')
        ip_address = ip_address or context.get('ip_address')
        user_agent = user_agent or context.get('user_agent')
        if user_id is None:
            user_id = context.get('user_id')

    # Ensure metadata is a dict
    if metadata is None:
        metadata = {}
    elif not isinstance(metadata, dict):
        metadata = {'data': metadata}

    return SystemLog.objects.create(
        level=level,
        category=category,
        message=message,
        user_id=user_id,
        object_id=object_id,
        metadata=metadata,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
        timestamp=timezone.now()
    )


def log_api_request(request, response, duration_ms=None):
    """
    Log an API request/response.

    Args:
        request: Django request object
        response: Django response object
        duration_ms (int, optional): Request duration in milliseconds
    """
    # Get request context
    context = get_request_context()
    request_id = context.get('request_id')
    user_id = context.get('user_id')
    ip_address = context.get('ip_address')
    user_agent = context.get('user_agent')

    # Build metadata
    metadata = {
        'method': request.method,
        'path': request.get_full_path(),
        'status_code': response.status_code,
        'content_type': response.get('Content-Type', ''),
    }

    if duration_ms is not None:
        metadata['duration_ms'] = duration_ms

    # Add request body size if available
    if hasattr(request, 'body') and request.body:
        metadata['request_size'] = len(request.body)

    # Add response body size if available
    if hasattr(response, 'content') and response.content:
        metadata['response_size'] = len(response.content)

    # Add query parameters
    if request.GET:
        metadata['query_params'] = dict(request.GET)

    # Determine log level based on status code
    if response.status_code >= 500:
        level = 'ERROR'
    elif response.status_code >= 400:
        level = 'WARN'
    else:
        level = 'INFO'

    message = f"{request.method} {request.get_full_path()} - {response.status_code}"

    return create_log_entry(
        level=level,
        category='api',
        message=message,
        user_id=user_id,
        metadata=metadata,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


def log_error(message, exception=None, user_id=None, request_id=None, metadata=None):
    """
    Log an error with optional exception details.

    Args:
        message (str): Error message
        exception (Exception, optional): Exception object
        user_id (int, optional): User ID
        request_id (str, optional): Request ID
        metadata (dict, optional): Additional metadata
    """
    if metadata is None:
        metadata = {}

    if exception:
        metadata['exception'] = {
            'type': type(exception).__name__,
            'message': str(exception),
        }

    # Get request context if not provided
    context = get_request_context()
    user_id = user_id or context.get('user_id')
    request_id = request_id or context.get('request_id')

    return create_log_entry(
        level='ERROR',
        category='error',
        message=message,
        user_id=user_id,
        metadata=metadata,
        request_id=request_id
    )


def log_audit_action(action, model_name, object_id, user_id=None, changes=None,
                    request_id=None, metadata=None):
    """
    Log an audit action (create, update, delete).

    Args:
        action (str): Action type (create, update, delete)
        model_name (str): Name of the model
        object_id (int): ID of the object
        user_id (int, optional): User ID performing the action
        changes (dict, optional): Dictionary of changes made
        request_id (str, optional): Request ID
        metadata (dict, optional): Additional metadata
    """
    if metadata is None:
        metadata = {}

    metadata['action'] = action
    metadata['model'] = model_name

    if changes:
        metadata['changes'] = changes

    # Get request context if not provided
    context = get_request_context()
    user_id = user_id or context.get('user_id')
    request_id = request_id or context.get('request_id')

    message = f"{action.capitalize()} {model_name} (ID: {object_id})"

    return create_log_entry(
        level='INFO',
        category='audit',
        message=message,
        user_id=user_id,
        object_id=object_id,
        metadata=metadata,
        request_id=request_id
    )


def cleanup_old_logs(days_to_keep=30, level=None, category=None):
    """
    Delete old log entries.

    Args:
        days_to_keep (int): Number of days to keep logs
        level (str, optional): Filter by log level
        category (str, optional): Filter by category

    Returns:
        tuple: (number_deleted, number_remaining)
    """
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    queryset = SystemLog.objects.filter(timestamp__lt=cutoff_date)

    if level:
        queryset = queryset.filter(level=level)

    if category:
        queryset = queryset.filter(category=category)

    # Count before deletion
    count_to_delete = queryset.count()

    # Delete old logs
    queryset.delete()

    # Count remaining
    count_remaining = SystemLog.objects.count()

    return count_to_delete, count_remaining


def get_log_stats():
    """
    Get statistics about log entries.

    Returns:
        dict: Statistics about log entries
    """
    total_logs = SystemLog.objects.count()

    if total_logs == 0:
        return {
            'total': 0,
            'by_level': {},
            'by_category': {},
            'recent_24h': 0,
            'recent_7d': 0,
        }

    # Stats by level
    by_level = {}
    for level, _ in SystemLog.LEVEL_CHOICES:
        count = SystemLog.objects.filter(level=level).count()
        if count > 0:
            by_level[level] = count

    # Stats by category
    by_category = {}
    for category, _ in SystemLog.CATEGORY_CHOICES:
        count = SystemLog.objects.filter(category=category).count()
        if count > 0:
            by_category[category] = count

    # Recent counts
    now = timezone.now()
    recent_24h = SystemLog.objects.filter(timestamp__gte=now - timedelta(hours=24)).count()
    recent_7d = SystemLog.objects.filter(timestamp__gte=now - timedelta(days=7)).count()

    return {
        'total': total_logs,
        'by_level': by_level,
        'by_category': by_category,
        'recent_24h': recent_24h,
        'recent_7d': recent_7d,
    }