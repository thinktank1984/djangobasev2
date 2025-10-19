"""
Django signal handlers for automatic audit logging.
"""

import logging
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from .utils import log_audit_action, log_error, create_log_entry


logger = logging.getLogger('auditlog.signals')


@receiver(pre_save)
def log_model_changes(sender, instance, **kwargs):
    """
    Log model changes before they are saved.
    This tracks what fields are being modified.
    """
    # Skip logging for SystemLog model itself to avoid infinite loops
    if sender.__name__ == 'SystemLog':
        return

    # Skip if instance doesn't have an ID yet (being created)
    if not instance.pk:
        return

    try:
        # Get the old version from database
        old_instance = sender.objects.get(pk=instance.pk)

        # Compare fields
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            if hasattr(old_instance, field_name) and hasattr(instance, field_name):
                old_value = getattr(old_instance, field_name)
                new_value = getattr(instance, field_name)

                if old_value != new_value:
                    # Handle foreign keys
                    if hasattr(old_value, 'pk'):
                        old_value = old_value.pk
                    if hasattr(new_value, 'pk'):
                        new_value = new_value.pk

                    changes[field_name] = {
                        'old': old_value,
                        'new': new_value
                    }

        # Store changes on instance for post_save to use
        if changes:
            instance._auditlog_changes = changes

    except sender.DoesNotExist:
        # Object doesn't exist in database yet (new object)
        pass
    except Exception as e:
        logger.error(f"Error in pre_save signal handler: {e}")


@receiver(post_save)
def log_model_creation_and_updates(sender, instance, created, **kwargs):
    """
    Log model creation and updates.
    """
    # Skip logging for SystemLog model itself
    if sender.__name__ == 'SystemLog':
        return

    try:
        # Get user from thread-local storage (set by middleware)
        from .handlers import get_request_context
        context = get_request_context()
        user_id = context.get('user_id')
        request_id = context.get('request_id')

        # Get object type
        model_name = sender.__name__

        if created:
            # Log creation
            create_log_entry(
                level='INFO',
                category='audit',
                message=f"Created {model_name} (ID: {instance.pk})",
                user_id=user_id,
                object_id=instance.pk,
                metadata={
                    'action': 'create',
                    'model': model_name,
                    'object_id': instance.pk,
                },
                request_id=request_id
            )
        else:
            # Log updates if there were changes
            changes = getattr(instance, '_auditlog_changes', None)
            if changes:
                create_log_entry(
                    level='INFO',
                    category='audit',
                    message=f"Updated {model_name} (ID: {instance.pk})",
                    user_id=user_id,
                    object_id=instance.pk,
                    metadata={
                        'action': 'update',
                        'model': model_name,
                        'object_id': instance.pk,
                        'changes': changes,
                        'changed_fields': list(changes.keys()),
                    },
                    request_id=request_id
                )

    except Exception as e:
        logger.error(f"Error in post_save signal handler: {e}")


@receiver(post_delete)
def log_model_deletion(sender, instance, **kwargs):
    """
    Log model deletions.
    """
    # Skip logging for SystemLog model itself
    if sender.__name__ == 'SystemLog':
        return

    try:
        # Get user from thread-local storage
        from .handlers import get_request_context
        context = get_request_context()
        user_id = context.get('user_id')
        request_id = context.get('request_id')

        model_name = sender.__name__

        create_log_entry(
            level='INFO',
            category='audit',
            message=f"Deleted {model_name} (ID: {instance.pk})",
            user_id=user_id,
            object_id=instance.pk,
            metadata={
                'action': 'delete',
                'model': model_name,
                'object_id': instance.pk,
            },
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"Error in post_delete signal handler: {e}")


# Authentication signals
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log successful user logins.
    """
    try:
        get_client_ip = getattr(request, 'META', {}).get
        ip_address = get_client_ip('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        create_log_entry(
            level='INFO',
            category='auth',
            message=f"User login: {user.username} (ID: {user.id})",
            user_id=user.id,
            metadata={
                'action': 'login',
                'username': user.username,
                'email': user.email,
                'ip_address': ip_address,
                'user_agent': user_agent,
            },
            ip_address=ip_address,
            user_agent=user_agent
        )

    except Exception as e:
        logger.error(f"Error in user_logged_in signal handler: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logouts.
    """
    try:
        if user:
            get_client_ip = getattr(request, 'META', {}).get
            ip_address = get_client_ip('REMOTE_ADDR')

            create_log_entry(
                level='INFO',
                category='auth',
                message=f"User logout: {user.username} (ID: {user.id})",
                user_id=user.id,
                metadata={
                    'action': 'logout',
                    'username': user.username,
                    'ip_address': ip_address,
                },
                ip_address=ip_address
            )

    except Exception as e:
        logger.error(f"Error in user_logged_out signal handler: {e}")


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Log failed login attempts.
    """
    try:
        get_client_ip = getattr(request, 'META', {}).get
        ip_address = get_client_ip('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        username = credentials.get('username', 'unknown')

        create_log_entry(
            level='WARN',
            category='auth',
            message=f"Failed login attempt for username: {username}",
            metadata={
                'action': 'login_failed',
                'username': username,
                'ip_address': ip_address,
                'user_agent': user_agent,
            },
            ip_address=ip_address,
            user_agent=user_agent
        )

    except Exception as e:
        logger.error(f"Error in user_login_failed signal handler: {e}")


# Django error handling
def log_django_exception(sender, request=None, **kwargs):
    """
    Log Django exceptions through the got_request_exception signal.
    """
    try:
        from django.core.signals import got_request_exception

        exception = kwargs.get('exception')
        if not exception:
            return

        # Get user info if available
        user_id = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id

        # Get request info if available
        metadata = {}
        if request:
            metadata.update({
                'method': request.method,
                'path': request.path,
                'get_params': dict(request.GET),
            })

            # Add request ID if available
            request_id = getattr(request, 'log_request_id', None)
        else:
            request_id = None

        log_error(
            message=f"Django exception: {type(exception).__name__}: {str(exception)}",
            exception=exception,
            user_id=user_id,
            request_id=request_id,
            metadata=metadata
        )

    except Exception as e:
        logger.error(f"Error in exception logging: {e}")


# Register the exception handler
from django.core.signals import got_request_exception
got_request_exception.connect(log_django_exception)