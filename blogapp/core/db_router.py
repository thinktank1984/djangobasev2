"""
Database router for logging application.

Routes logging-related models to the 'logs' SQLite database
and all other models to the 'default' database.
"""


class LoggingDatabaseRouter:
    """
    A router to control all database operations on models in the
    logging application.
    """

    logging_app_labels = {'auditlog'}

    def db_for_read(self, model, **hints):
        """
        Suggest the database to read data from for models of the logging app.
        """
        if model._meta.app_label in self.logging_app_labels:
            return 'logs'
        return None

    def db_for_write(self, model, **hints):
        """
        Suggest the database to write data to for models of the logging app.
        """
        if model._meta.app_label in self.logging_app_labels:
            return 'logs'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the logging app is involved.
        """
        # Allow relations if both models are in the logging app
        if (
            obj1._meta.app_label in self.logging_app_labels or
            obj2._meta.app_label in self.logging_app_labels
        ):
            return True
        # Allow if neither model is in the logging app
        elif (
            obj1._meta.app_label not in self.logging_app_labels and
            obj2._meta.app_label not in self.logging_app_labels
        ):
            return True
        # Otherwise, don't allow
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure that the logging app's models get created on the right database.
        """
        if app_label in self.logging_app_labels:
            return db == 'logs'
        return db == 'default'