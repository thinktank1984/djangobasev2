## Why

To establish a modular plugin architecture that allows features to be developed, deployed, and maintained independently. Moving todo_tasks to a plugin system will serve as a foundation for future modularity and provide a clear pattern for adding new features.

## What Changes

- Create plugin system infrastructure under `/plugins/` directory
- Move `apps/todo_tasks/` functionality to `plugins/todo/` as a plugin
- Implement plugin discovery and loading mechanism
- Add plugin configuration and management capabilities
- Update URL routing to support plugin endpoints
- Migrate database models and data from todo_tasks to plugin system
- **BREAKING**: Change URL patterns from `/tasks/` to plugin-based routing
- **BREAKING**: Update app registration from `apps.todo_tasks` to plugin system

## Impact

- **Affected specs**:
  - New `plugins` capability for plugin infrastructure
  - New `tasks` capability for todo functionality (moved from apps)
- **Affected code**:
  - `apps/todo_tasks/` → `plugins/todo/`
  - `core/settings.py` (app registration)
  - `core/urls.py` (URL routing)
  - Database migrations (model relocation)
- **Migration requirements**: Data migration from todo_tasks tables to plugin-specific tables