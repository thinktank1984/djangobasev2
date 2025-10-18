# Design Document: Tailwind CSS Integration

## Context

The Bloggy application currently uses a minimal custom CSS file (`runtime/static/style.css`) with ~16 lines of basic styling. As the application grows and needs more sophisticated UI components, writing custom CSS for every component becomes time-consuming and leads to inconsistent designs. Tailwind CSS provides a utility-first approach that can accelerate UI development while maintaining consistency.

**Background:**
- Emmett Framework application using Renoir templates
- Docker-based development workflow
- No existing frontend build process
- Simple static file serving via Emmett

**Constraints:**
- Must work within Docker environment
- Should not require Node.js/npm for simplicity
- Must not break existing styling
- Should be optional (projects can still use custom CSS only)

**Stakeholders:**
- Developers building UI features
- DevOps maintaining Docker infrastructure

## Goals / Non-Goals

**Goals:**
- Integrate Tailwind CSS using standalone CLI (no Node.js dependency)
- Enable utility-first CSS development in Emmett applications
- Provide development watch mode for automatic CSS rebuilds
- Support production builds with CSS purging/optimization
- Maintain compatibility with existing custom CSS
- Document usage patterns for Emmett + Tailwind

**Non-Goals:**
- Complete migration of existing styles to Tailwind (optional enhancement)
- Integration with JavaScript build tools
- PostCSS plugins beyond Tailwind's built-in capabilities
- Custom Tailwind plugin development
- Component library creation

## Decisions

### Decision 1: Use Tailwind CSS Standalone CLI

**What:** Use the official Tailwind CSS standalone CLI binary instead of Node.js/npm installation.

**Why:**
- Simplifies dependencies (no Node.js, npm, or package.json needed)
- Single binary, easy to install in Docker
- Faster builds (compiled Go binary)
- Consistent with project's preference for simplicity
- No dependency version conflicts

**Alternatives considered:**
- **Node.js + npm installation**: More common approach, but adds Node.js dependency, package.json management, and complexity
- **CDN-hosted Tailwind**: Easy but lacks purging, large file size, no custom configuration
- **Compiled CSS only**: No rebuild capability, inflexible

### Decision 2: Tailwind Configuration Location

**What:** Place `tailwind.config.js` in `runtime/` directory alongside application code.

**Why:**
- Collocated with templates and static files
- Follows Emmett's single-application structure
- Easy for developers to find and modify
- Scans templates in same directory tree

**Alternatives considered:**
- Root directory: Separates config from runtime code, less intuitive
- Separate `frontend/` directory: Over-engineering for current needs

### Decision 3: CSS File Strategy

**What:** Create `runtime/static/input.css` with Tailwind directives, output to `runtime/static/tailwind.css`, preserve `style.css` for custom styles.

**Structure:**
```
runtime/static/
├── input.css        # Tailwind directives (@tailwind base, components, utilities)
├── tailwind.css     # Generated Tailwind output (gitignored)
└── style.css        # Existing custom styles (preserved, loaded after Tailwind)
```

**Why:**
- Clear separation between source (input.css) and output (tailwind.css)
- Preserves existing custom CSS for gradual migration
- CSS cascade order: Tailwind base → Tailwind utilities → custom overrides
- Allows projects to use both Tailwind and custom CSS

**Alternatives considered:**
- Single CSS file: Loses separation, harder to maintain
- Replace style.css entirely: Breaking change, requires full migration
- Multiple output files: Unnecessary complexity

### Decision 4: Development Workflow

**What:** Provide three build modes:
1. **One-time build**: `./tailwind -i runtime/static/input.css -o runtime/static/tailwind.css`
2. **Watch mode**: Same command with `--watch` flag for development
3. **Production build**: Same command with `--minify` flag

**Why:**
- Simple, explicit commands
- Watch mode enables rapid development
- Production builds are optimized
- No complex build scripts required

**Alternatives considered:**
- Docker Compose service for watch: Adds complexity, auto-starts even when not needed
- Makefile: Extra abstraction layer, less transparent
- Custom wrapper script: Unnecessary for simple CLI commands

### Decision 5: Docker Integration

**What:** Add Tailwind CLI binary to Dockerfile, document usage commands, but don't auto-run builds.

**Why:**
- Developers control when to rebuild CSS
- No hidden build processes
- Clear separation of concerns (app server vs. CSS builds)
- Can add watch service later if needed

**Alternatives considered:**
- Auto-build on container start: Unnecessary overhead, slows startup
- Separate CSS build container: Over-engineering for current scale
- Build CSS during Docker image build: Requires source files in image build context, inflexible

## Risks / Trade-offs

### Risk 1: Tailwind CLI Binary Updates
**Risk:** Standalone CLI needs manual updates, might lag behind npm version.
**Mitigation:** 
- Document current version in Dockerfile
- Check for updates periodically
- Standalone CLI is well-maintained and stable

### Risk 2: Learning Curve
**Risk:** Developers unfamiliar with Tailwind utility-first approach.
**Mitigation:**
- Provide documentation with common patterns
- Keep custom CSS as fallback
- Include example templates with Tailwind classes
- Link to official Tailwind documentation

### Risk 3: CSS File Size
**Risk:** Without proper purging, Tailwind CSS can be large (~3MB development, ~10KB production).
**Mitigation:**
- Configure content paths correctly in tailwind.config.js
- Use production build with --minify for deployment
- Tailwind automatically purges unused classes

### Risk 4: Template Scanning
**Risk:** Renoir templates might have dynamic class names that Tailwind can't detect.
**Mitigation:**
- Document safelist configuration for dynamic classes
- Encourage static class names where possible
- Provide examples of Tailwind-safe template patterns

## Trade-offs

| Aspect | Trade-off | Decision |
|--------|-----------|----------|
| Simplicity vs. Features | Standalone CLI simpler but fewer features than full Node.js setup | Chose simplicity (standalone CLI) |
| Auto-rebuild vs. Control | Watch mode convenient but uses resources | Provide watch mode but don't auto-start |
| Migration Strategy | Full migration vs. gradual adoption | Support both (coexist with custom CSS) |
| Configuration | Convention vs. customization | Start with defaults, allow customization |

## Migration Plan

### Phase 1: Setup (This Change)
1. Install Tailwind CLI in Docker
2. Create configuration files
3. Generate initial Tailwind CSS output
4. Update layout.html to include Tailwind CSS
5. Verify existing styles still work

### Phase 2: Documentation
1. Document build commands
2. Add usage examples
3. Create migration guide for custom CSS → Tailwind

### Phase 3: Optional Enhancement (Future)
1. Migrate existing templates to Tailwind utilities
2. Remove redundant custom CSS
3. Add responsive design improvements
4. Create reusable Tailwind component examples

### Rollback Plan
If Tailwind causes issues:
1. Remove Tailwind CSS include from layout.html
2. Revert to style.css only
3. Remove Tailwind files (no impact on application logic)
4. Dockerfile changes can remain (unused binary has minimal impact)

## Implementation Notes

### Tailwind Config Structure
```javascript
// runtime/tailwind.config.js
module.exports = {
  content: [
    "./templates/**/*.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Input CSS Structure
```css
/* runtime/static/input.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Template Integration
```html
<!-- runtime/templates/layout.html -->
{{include_static 'tailwind.css'}}  <!-- Tailwind utilities first -->
{{include_static 'style.css'}}     <!-- Custom overrides second -->
```

### Docker Commands
```bash
# Development watch mode
docker compose -f docker/docker-compose.yaml exec runtime ./tailwind -i static/input.css -o static/tailwind.css --watch

# Production build
docker compose -f docker/docker-compose.yaml exec runtime ./tailwind -i static/input.css -o static/tailwind.css --minify
```

## Open Questions

1. **Should we include any Tailwind plugins by default?** (e.g., forms, typography)
   - Recommendation: Start minimal, add plugins as needed
   
2. **Should we create a wrapper script for common Tailwind commands?**
   - Recommendation: Keep it simple initially, add script only if repetitive

3. **Should Tailwind watch run as a Docker Compose service?**
   - Recommendation: Optional service, not default (developers can start manually)

4. **Should we migrate all existing templates immediately?**
   - Recommendation: No, gradual migration, keep custom CSS working

5. **Should we add dark mode support?**
   - Recommendation: Document how to enable, don't enable by default

