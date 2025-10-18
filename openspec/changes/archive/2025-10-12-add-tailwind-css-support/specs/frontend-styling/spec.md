## ADDED Requirements

### Requirement: Tailwind CSS Integration

The system SHALL provide Tailwind CSS integration for utility-first styling in Emmett Framework applications.

#### Scenario: Tailwind CLI Installation
- **GIVEN** the Docker development environment
- **WHEN** the runtime container is built
- **THEN** the Tailwind CSS standalone CLI binary SHALL be installed and accessible
- **AND** the CLI SHALL be executable without requiring Node.js or npm

#### Scenario: Configuration Files
- **GIVEN** the runtime application directory
- **WHEN** Tailwind CSS is configured
- **THEN** a `tailwind.config.js` file SHALL exist in the `runtime/` directory
- **AND** the config SHALL specify `./templates/**/*.html` as content source
- **AND** an `input.css` file SHALL exist in `runtime/static/` with Tailwind directives

### Requirement: CSS Build Process

The system SHALL provide commands to build Tailwind CSS from source to output.

#### Scenario: Development Build
- **GIVEN** the Tailwind input CSS and configuration
- **WHEN** a developer runs the build command
- **THEN** Tailwind SHALL generate `runtime/static/tailwind.css` with all utility classes
- **AND** the output SHALL include all classes detected in template files
- **AND** the build SHALL complete in under 5 seconds for typical projects

#### Scenario: Watch Mode
- **GIVEN** the development environment
- **WHEN** a developer enables watch mode
- **THEN** Tailwind SHALL automatically rebuild CSS when template files change
- **AND** Tailwind SHALL automatically rebuild CSS when input.css changes
- **AND** the watch process SHALL continue until manually stopped

#### Scenario: Production Build
- **GIVEN** the application ready for deployment
- **WHEN** a production build command is executed
- **THEN** Tailwind SHALL generate minified CSS output
- **AND** unused CSS classes SHALL be purged from the output
- **AND** the output file size SHALL be significantly smaller than development builds

### Requirement: Template Integration

The system SHALL integrate Tailwind CSS into Emmett Renoir templates.

#### Scenario: CSS Loading Order
- **GIVEN** the base layout template
- **WHEN** the page is rendered
- **THEN** Tailwind CSS SHALL be loaded before custom CSS
- **AND** custom CSS rules SHALL be able to override Tailwind utilities
- **AND** both Tailwind and custom styles SHALL apply correctly

#### Scenario: Utility Class Usage
- **GIVEN** a Renoir template file
- **WHEN** developers add Tailwind utility classes to HTML elements
- **THEN** the classes SHALL be detected by Tailwind's content scanner
- **AND** the corresponding styles SHALL appear in the generated CSS
- **AND** the styles SHALL render correctly in the browser

### Requirement: Docker Workflow

The system SHALL support Tailwind CSS builds within the Docker development environment.

#### Scenario: Build Command in Docker
- **GIVEN** the running runtime container
- **WHEN** a developer executes Tailwind build commands in the container
- **THEN** the commands SHALL execute successfully
- **AND** the generated CSS SHALL be accessible to the Emmett application
- **AND** changes SHALL be reflected immediately in the running application

#### Scenario: File Watching in Docker
- **GIVEN** the Docker container with mounted volumes
- **WHEN** watch mode is active
- **THEN** file changes in the host system SHALL trigger rebuilds in the container
- **AND** the rebuilt CSS SHALL be immediately available to the application

### Requirement: Backward Compatibility

The system SHALL maintain backward compatibility with existing custom CSS.

#### Scenario: Existing Styles Preserved
- **GIVEN** an application with existing `style.css` custom styles
- **WHEN** Tailwind CSS is integrated
- **THEN** existing custom styles SHALL continue to work
- **AND** existing pages SHALL render without visual regressions
- **AND** developers SHALL be able to use both Tailwind utilities and custom CSS simultaneously

#### Scenario: Gradual Migration
- **GIVEN** templates using custom CSS classes
- **WHEN** developers migrate to Tailwind utilities
- **THEN** they SHALL be able to migrate templates incrementally
- **AND** migrated and non-migrated templates SHALL coexist
- **AND** no breaking changes SHALL be required to existing templates

### Requirement: Configuration and Customization

The system SHALL allow customization of Tailwind CSS configuration.

#### Scenario: Theme Customization
- **GIVEN** the `tailwind.config.js` configuration file
- **WHEN** developers modify theme settings (colors, spacing, fonts, etc.)
- **THEN** the customizations SHALL be reflected in generated utility classes
- **AND** the Tailwind build process SHALL incorporate the custom theme
- **AND** templates SHALL have access to custom utility classes

#### Scenario: Content Path Configuration
- **GIVEN** the Tailwind configuration
- **WHEN** developers add additional content paths (e.g., custom components)
- **THEN** Tailwind SHALL scan all configured paths for class usage
- **AND** classes from all paths SHALL be included in the output

#### Scenario: Safelist for Dynamic Classes
- **GIVEN** templates with dynamically generated class names
- **WHEN** developers add classes to the safelist configuration
- **THEN** safelisted classes SHALL always be included in the output
- **AND** safelisted classes SHALL work even if not detected in template scanning

### Requirement: Documentation and Developer Experience

The system SHALL provide clear documentation for Tailwind CSS usage.

#### Scenario: Build Command Documentation
- **GIVEN** project documentation
- **WHEN** developers need to build Tailwind CSS
- **THEN** documentation SHALL provide clear commands for development builds
- **AND** documentation SHALL provide clear commands for watch mode
- **AND** documentation SHALL provide clear commands for production builds

#### Scenario: Usage Examples
- **GIVEN** project documentation or example templates
- **WHEN** developers need to use Tailwind in Emmett applications
- **THEN** examples SHALL demonstrate common Tailwind utility class patterns
- **AND** examples SHALL show integration with Renoir template syntax
- **AND** examples SHALL demonstrate responsive design patterns

#### Scenario: Migration Guide
- **GIVEN** an existing application with custom CSS
- **WHEN** developers want to migrate to Tailwind
- **THEN** documentation SHALL provide a migration strategy
- **AND** documentation SHALL explain how to coexist with custom CSS
- **AND** documentation SHALL provide before/after examples

### Requirement: Performance and Optimization

The system SHALL ensure Tailwind CSS does not negatively impact application performance.

#### Scenario: Production Bundle Size
- **GIVEN** a production-ready application
- **WHEN** Tailwind CSS is built for production with purging enabled
- **THEN** the CSS file size SHALL be minimal (typically under 20KB compressed)
- **AND** only classes used in templates SHALL be included
- **AND** the CSS SHALL load quickly in browsers

#### Scenario: Build Performance
- **GIVEN** a typical Emmett application with Tailwind
- **WHEN** the CSS build process runs
- **THEN** the build SHALL complete in under 5 seconds
- **AND** watch mode SHALL rebuild incrementally within 1-2 seconds
- **AND** the build process SHALL not block application startup

#### Scenario: Runtime Performance
- **GIVEN** templates using Tailwind utility classes
- **WHEN** pages are rendered by the Emmett application
- **THEN** CSS loading SHALL not add significant page load time
- **AND** utility classes SHALL not cause performance degradation compared to custom CSS
- **AND** the application SHALL maintain responsive page loads

