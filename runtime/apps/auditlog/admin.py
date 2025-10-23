import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import SafeString

from .models import SystemLog
from .utils import cleanup_old_logs, get_log_stats


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    """
    Admin interface for SystemLog model with comprehensive filtering and search.
    """

    list_display = [
        'get_display_level_badge',
        'get_display_category_icon',
        'message_preview',
        'user_info',
        'timestamp',
        'ip_address_short',
    ]

    list_filter = [
        'level',
        'category',
        'timestamp',
        'user_id',
    ]

    search_fields = [
        'message',
        'metadata',
        'user_agent',
        'request_id',
    ]

    date_hierarchy = 'timestamp'

    ordering = ['-timestamp']

    # Actions for log management
    actions = ['cleanup_old_logs_action', 'mark_as_reviewed']

    # Read-only by default to prevent accidental modifications
    readonly_fields = [
        'level', 'category', 'message', 'timestamp', 'user_id',
        'object_id', 'metadata_formatted', 'request_id', 'ip_address',
        'user_agent', 'metadata_json_pretty'
    ]

    # Show fieldsets for better organization
    fieldsets = (
        ('Basic Information', {
            'fields': ('level', 'category', 'message', 'timestamp')
        }),
        ('User & Request Context', {
            'fields': ('user_id', 'request_id', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Object Reference', {
            'fields': ('object_id',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata_formatted',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of log entries through admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """Make log entries read-only."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete log entries."""
        return request.user.is_superuser

    def get_queryset(self, request):
        """Optimize queries for better performance."""
        return super().get_queryset(request).select_related().prefetch_related()

    def get_display_level_badge(self, obj):
        """Display log level with color-coded badge."""
        level_colors = {
            'DEBUG': '#6c757d',
            'INFO': '#17a2b8',
            'WARN': '#ffc107',
            'ERROR': '#dc3545',
            'CRITICAL': '#6f42c1',
        }
        color = level_colors.get(obj.level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.level
        )
    get_display_level_badge.short_description = 'Level'
    get_display_level_badge.admin_order_field = 'level'

    def get_display_category_icon(self, obj):
        """Display category with appropriate icon."""
        category_icons = {
            'api': '🌐',
            'error': '❌',
            'migration': '🔄',
            'audit': '📋',
            'auth': '🔐',
            'system': '⚙️',
        }
        icon = category_icons.get(obj.category, '📝')
        return format_html('<span title="{}">{} {}</span>',
                          obj.get_category_display(), icon, obj.get_category_display())
    get_display_category_icon.short_description = 'Category'
    get_display_category_icon.admin_order_field = 'category'

    def message_preview(self, obj):
        """Show a preview of the message with full message in title."""
        if len(obj.message) <= 80:
            return obj.message
        return format_html('<span title="{}">{}</span>', obj.message, obj.message[:77] + '...')
    message_preview.short_description = 'Message'
    message_preview.admin_order_field = 'message'

    def user_info(self, obj):
        """Display user information if available."""
        if obj.user_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=obj.user_id)
                return format_html(
                    '<a href="{}">{} ({})</a>',
                    reverse('admin:auth_user_change', args=[user.id]),
                    user.get_full_name() or user.username,
                    obj.user_id
                )
            except:
                return format_html('User ID: {}', obj.user_id)
        return '-'
    user_info.short_description = 'User'
    user_info.admin_order_field = 'user_id'

    def ip_address_short(self, obj):
        """Show shortened IP address for better column display."""
        if obj.ip_address:
            return str(obj.ip_address)
        return '-'
    ip_address_short.short_description = 'IP Address'
    ip_address_short.admin_order_field = 'ip_address'

    def metadata_formatted(self, obj):
        """Display formatted metadata with proper indentation."""
        if not obj.metadata:
            return 'No metadata'

        try:
            formatted_json = json.dumps(obj.metadata, indent=2, sort_keys=True)
            # Escape HTML and preserve formatting
            return mark_safe(f'<pre style="background-color: #f8f9fa; padding: 10px; '
                             f'border-radius: 4px; white-space: pre-wrap; '
                             f'font-family: monospace; font-size: 12px;">{formatted_json}</pre>')
        except (TypeError, ValueError):
            return str(obj.metadata)
    metadata_formatted.short_description = 'Metadata'

    def metadata_json_pretty(self, obj):
        """Pretty-print JSON metadata."""
        return obj.metadata_json

    # Custom actions
    def cleanup_old_logs_action(self, request, queryset):
        """Action to clean up old log entries."""
        # This action doesn't use queryset - it cleans up based on age
        deleted_count, remaining_count = cleanup_old_logs(days_to_keep=30)

        self.message_user(
            request,
            f'Successfully deleted {deleted_count} old log entries. '
            f'{remaining_count} log entries remaining.',
            level='success'
        )
    cleanup_old_logs_action.short_description = 'Clean up logs older than 30 days'

    def mark_as_reviewed(self, request, queryset):
        """Mark logs as reviewed (placeholder for future functionality)."""
        count = queryset.count()
        self.message_user(
            request,
            f'Marked {count} log entries as reviewed.',
            level='info'
        )
    mark_as_reviewed.short_description = 'Mark as reviewed'

    def changelist_view(self, request, extra_context=None):
        """Add statistics to the changelist view."""
        extra_context = extra_context or {}

        # Get log statistics
        stats = get_log_stats()

        # Format stats for display
        extra_context.update({
            'log_stats': stats,
            'total_logs': stats['total'],
            'recent_24h': stats['recent_24h'],
            'recent_7d': stats['recent_7d'],
        })

        return super().changelist_view(request, extra_context)


# Admin site customization
admin.site.site_header = "Django SaaS Logging"
admin.site.site_title = "Logging Admin"
admin.site.index_title = "Welcome to Django SaaS Logging Administration"
