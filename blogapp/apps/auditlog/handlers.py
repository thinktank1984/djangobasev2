"""
Django logging handlers for writing to SystemLog model.
"""

import logging
import threading
from uuid import uuid4

from django.utils import timezone
from django.conf import settings


# Thread-local storage for request context
_request_local = threading.local()


def set_request_context(request_id=None, user_id=None, ip_address=None, user_agent=None):
    """Set request context in thread-local storage."""
    if not hasattr(_request_local, 'context'):
        _request_local.context = {}

    if request_id is not None:
        _request_local.context['request_id'] = request_id
    if user_id is not None:
        _request_local.context['user_id'] = user_id
    if ip_address is not None:
        _request_local.context['ip_address'] = ip_address
    if user_agent is not None:
        _request_local.context['user_agent'] = user_agent


def get_request_context():
    """Get request context from thread-local storage."""
    if hasattr(_request_local, 'context'):
        return _request_local.context.copy()
    return {}


def clear_request_context():
    """Clear request context from thread-local storage."""
    if hasattr(_request_local, 'context'):
        _request_local.context.clear()


class DatabaseLogHandler(logging.Handler):
    """
    A logging handler that writes log records to the SystemLog model.
    """

    def __init__(self, level=logging.NOTSET, default_category='system'):
        super().__init__(level)
        self.default_category = default_category

    def emit(self, record):
        """
        Emit a log record by creating a SystemLog entry.
        """
        try:
            from .models import SystemLog

            # Get request context
            context = get_request_context()

            # Extract category from record if available
            category = getattr(record, 'category', self.default_category)

            # Extract object_id from record if available
            object_id = getattr(record, 'object_id', None)

            # Extract metadata from record
            metadata = {}

            # Add basic record info
            metadata['module'] = record.module if hasattr(record, 'module') else record.name
            metadata['function'] = record.funcName
            metadata['line'] = record.lineno
            metadata['thread'] = record.thread
            metadata['process'] = record.process

            # Add exception info if available
            if record.exc_info:
                metadata['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': self.formatter.formatException(record.exc_info) if self.formatter else None
                }

            # Add any extra fields from the record
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                              'filename', 'module', 'lineno', 'funcName', 'created',
                              'msecs', 'relativeCreated', 'thread', 'threadName',
                              'processName', 'process', 'getMessage', 'exc_info',
                              'exc_text', 'stack_info', 'category', 'object_id']:
                    metadata[key] = value

            # Create SystemLog entry
            SystemLog.objects.create(
                level=record.levelname,
                category=category,
                message=record.getMessage(),
                user_id=context.get('user_id'),
                object_id=object_id,
                metadata=metadata,
                request_id=context.get('request_id'),
                ip_address=context.get('ip_address'),
                user_agent=context.get('user_agent'),
                timestamp=timezone.datetime.fromtimestamp(record.created, tz=timezone.utc)
            )

        except Exception:
            # Don't let logging errors crash the application
            # Log to stderr as fallback
            import sys
            print(f"Error in DatabaseLogHandler: {sys.exc_info()}", file=sys.stderr)

    def close(self):
        """
        Close the handler and clean up resources.
        """
        super().close()


class RequestLoggingMiddleware:
    """
    Middleware to set request context for logging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate unique request ID
        request_id = str(uuid4())

        # Get user info if authenticated
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id

        # Get IP address
        ip_address = self.get_client_ip(request)

        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Set request context for logging
        set_request_context(
            request_id=request_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Add request_id to request object for later use
        request.log_request_id = request_id

        try:
            response = self.get_response(request)
        finally:
            # Clear context after request is processed
            clear_request_context()

        return response

    def get_client_ip(self, request):
        """
        Get the client IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip