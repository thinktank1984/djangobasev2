from django.apps import AppConfig


class AuditlogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.auditlog"

    def ready(self):
        """Import signal handlers when app is ready."""
        import apps.auditlog.signals
