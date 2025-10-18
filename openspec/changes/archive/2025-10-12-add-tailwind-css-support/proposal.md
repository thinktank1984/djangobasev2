# Add Tailwind CSS Support

## Why

The application currently uses a minimal custom CSS file with basic styling. Adding Tailwind CSS will provide a modern utility-first CSS framework that enables rapid UI development, consistent design patterns, and responsive layouts without writing custom CSS. This will significantly improve the developer experience and UI quality for the Bloggy application and future features.

## What Changes

- Integrate Tailwind CSS into the Emmett Framework runtime application
- Set up Tailwind CSS build process using standalone CLI (no Node.js required)
- Configure Tailwind to scan Renoir templates for class usage
- Preserve existing styling while migrating to Tailwind utilities
- Add Tailwind-based responsive design capabilities
- Configure Docker environment to support Tailwind CSS builds
- Add watch mode for automatic CSS regeneration during development

## Impact

- Affected specs: `frontend-styling` (NEW)
- Affected code:
  - `runtime/templates/*.html` - Add Tailwind utility classes
  - `runtime/static/style.css` - Migrate to Tailwind or coexist with custom styles
  - `docker/Dockerfile` - Add Tailwind CLI binary
  - `docker/docker-compose.yaml` - Add Tailwind watch service (optional)
  - Development workflow - Add Tailwind build step
- Developer experience:
  - Faster UI development with utility classes
  - Consistent design system
  - No need to write custom CSS for common patterns
  - Better responsive design capabilities

