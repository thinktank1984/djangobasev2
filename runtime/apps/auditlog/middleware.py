"""
Middleware for logging HTTP requests and responses.
"""

import time
import logging
from django.utils import timezone
from django.conf import settings

from .utils import log_api_request, log_error


class RequestLoggingMiddleware:
    """
    Middleware to log HTTP requests and responses to the SystemLog model.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('auditlog.middleware')

    def __call__(self, request):
        # Skip certain requests to avoid noise
        if self.should_skip_request(request):
            return self.get_response(request)

        # Start timing
        start_time = time.time()

        # Process request
        response = self.get_response(request)

        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # Log the request
        try:
            log_api_request(request, response, duration_ms)
        except Exception as e:
            # Don't let logging errors break the application
            self.logger.error(f"Failed to log API request: {e}")

        return response

    def should_skip_request(self, request):
        """Determine if a request should be skipped from logging."""
        # Skip static files and media
        skip_paths = getattr(settings, 'LOGGING_SKIP_PATHS', [
            '/static/',
            '/media/',
            '/favicon.ico',
        ])

        # Skip health check endpoints
        skip_paths.extend([
            '/health/',
            '/healthz',
            '/ping/',
            '/ready/',
        ])

        # Skip admin requests to avoid infinite loops during admin access
        skip_paths.append('/admin/auditlog/')

        # Check if path should be skipped
        path = request.path
        for skip_path in skip_paths:
            if path.startswith(skip_path):
                return True

        # Skip based on HTTP method
        skip_methods = getattr(settings, 'LOGGING_SKIP_METHODS', ['OPTIONS', 'HEAD'])
        if request.method in skip_methods:
            return True

        # Skip based on user agent (common bots/crawlers)
        skip_user_agents = getattr(settings, 'LOGGING_SKIP_USER_AGENTS', [
            'Mozilla/5.0 (compatible; Googlebot/',
            'Mozilla/5.0 (compatible; bingbot/',
            'Mozilla/5.0 (compatible; YandexBot/',
        ])

        user_agent = request.META.get('HTTP_USER_AGENT', '')
        for ua in skip_user_agents:
            if ua in user_agent:
                return True

        return False


class ErrorLoggingMiddleware:
    """
    Middleware to catch and log exceptions that occur during request processing.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('auditlog.errors')

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            # Log the error
            try:
                # Get user info if available
                user_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = request.user.id

                # Get request context
                request_id = getattr(request, 'log_request_id', None)

                # Build metadata
                metadata = {
                    'method': request.method,
                    'path': request.path,
                    'get_params': dict(request.GET),
                    'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
                }

                # Add POST data if not sensitive
                if request.method == 'POST' and not self.is_sensitive_path(request.path):
                    # Only include safe POST data
                    safe_post_data = {}
                    for key, value in request.POST.items():
                        if not self.is_sensitive_key(key):
                            safe_post_data[key] = str(value)[:100]  # Truncate long values
                    metadata['post_data'] = safe_post_data

                log_error(
                    message=f"Unhandled exception: {str(e)}",
                    exception=e,
                    user_id=user_id,
                    request_id=request_id,
                    metadata=metadata
                )

            except Exception as log_error:
                # If logging fails, at least log to standard error
                self.logger.error(f"Failed to log exception: {log_error}")
                self.logger.error(f"Original exception: {e}")

            # Re-raise the exception so Django's normal error handling takes over
            raise

    def is_sensitive_path(self, path):
        """Check if a path contains sensitive information."""
        sensitive_paths = [
            '/admin/',
            '/login/',
            '/logout/',
            '/signup/',
            '/password/',
            '/api/auth/',
            '/api/payments/',
            '/api/billing/',
        ]
        return any(path.startswith(sensitive_path) for sensitive_path in sensitive_paths)

    def is_sensitive_key(self, key):
        """Check if a form key contains sensitive information."""
        sensitive_keys = [
            'password', 'passwd', 'secret', 'token', 'key',
            'csrf', 'session', 'auth', 'credit', 'card',
            'ssn', 'social', 'bank', 'account'
        ]
        key_lower = key.lower()
        return any(sensitive in key_lower for sensitive in sensitive_keys)


class PerformanceLoggingMiddleware:
    """
    Middleware to log slow requests for performance monitoring.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_request_threshold = getattr(settings, 'SLOW_REQUEST_THRESHOLD_MS', 1000)
        self.logger = logging.getLogger('auditlog.performance')

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Log slow requests
        if duration_ms > self.slow_request_threshold:
            try:
                from .utils import create_log_entry

                # Get user info if available
                user_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = request.user.id

                # Get request context
                request_id = getattr(request, 'log_request_id', None)

                # Build metadata
                metadata = {
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'threshold_ms': self.slow_request_threshold,
                }

                create_log_entry(
                    level='WARN',
                    category='api',
                    message=f"Slow request detected: {request.method} {request.path} took {duration_ms}ms",
                    user_id=user_id,
                    metadata=metadata,
                    request_id=request_id
                )

            except Exception as e:
                # Don't let logging errors break the application
                self.logger.error(f"Failed to log slow request: {e}")

        return response