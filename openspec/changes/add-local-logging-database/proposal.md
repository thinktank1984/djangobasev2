## Why

The Django SaaS boilerplate lacks a comprehensive logging architecture that separates operational diagnostics from business data. Adding a dedicated local-only logging database will provide better observability, auditability, and data isolation without relying on external cloud services, following Django best practices for multi-database applications.

## What Changes

- Add a dedicated SQLite database for all operational logs (errors, warnings, API requests, audit trails)
- Implement Django database routing to direct log-related models to the separate database
- Create unified log storage models and Django management commands
- Add log viewing capabilities via Django admin interface and CLI tools
- Implement log rotation and maintenance procedures
- Create a new Django app `logging` to encapsulate all logging functionality
- **BREAKING**: Changes to database configuration and adds new Django app

## Impact

- **Affected specs**: error-tracking, database, logging (new capability)
- **Affected code**:
  - Database configuration in `blogapp/core/settings.py`
  - New Django app `blogapp/apps/logging/`
  - Database router implementation
  - Django admin interface extensions
  - Management commands for log viewing and maintenance
  - Docker environment setup for log directory persistence
- **Dependencies**: No external dependencies - uses existing Django and SQLite support