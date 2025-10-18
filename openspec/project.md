# Project Context

## Purpose

This is an **Emmett Framework demonstration project** featuring "Bloggy", a complete micro-blogging application that showcases Emmett's web development capabilities including:
- User authentication and authorization
- Admin-only content creation
- Blog posts with comments
- Form handling and validation
- Database relationships using pyDAL ORM
- Template inheritance with Renoir

The project serves as both a reference implementation and learning resource for building web applications with the Emmett framework.

## Tech Stack

### Core Framework
- **Emmett 2.5.0+** - Python web framework (similar to Flask but more batteries-included)
- **Python 3.9+** (3.13+ recommended)
- **pyDAL** - Database abstraction layer (ORM)
- **Renoir** - Template engine (Python-like syntax)
- **PostgreSQL 16** - Primary database backend

### Infrastructure & Deployment
- **Docker** - Primary development and deployment environment
- **Granian** - ASGI server for production
- **PostgreSQL 16** - Production database (Alpine image)

### Development Tools
- **pytest** - Testing framework
- **coverage** - Test coverage reporting
- **uv** - Python package manager (for local development fallback)

### Additional Capabilities
- Built-in authentication module (`Auth`)
- Session management (cookie-based, file-based, Redis-backed)
- WebSocket support for real-time features
- RESTful API capabilities via `emmett-rest`
- Caching (RAM, Disk, Redis, Valkey)
- Email sending (`Mailer`)
- Internationalization support

## Project Conventions

### Code Style

**Python Conventions:**
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Prefer explicit over implicit
- Use type hints where beneficial

**Emmett-Specific Patterns:**
- Define models with clear field types and validation rules
- Use `Field.belongs_to()`, `Field.has_many()` for relationships
- Validation dictionaries in model classes
- Async route handlers: `async def route_name():`
- Use `@app.route()` decorator for routing
- Return dictionaries from routes for template context

**File Organization:**
- Main application in `runtime/app.py`
- Templates in `runtime/templates/`
- Static files in `runtime/static/`
- Migrations in `runtime/migrations/`
- Integration tests in `integration_tests/` (at project root)

**Naming Conventions:**
- Models: PascalCase (e.g., `Post`, `Comment`, `User`)
- Routes: snake_case function names (e.g., `show_post`, `new_post`)
- Templates: lowercase with underscores (e.g., `new_post.html`, `layout.html`)
- Database fields: snake_case

### Architecture Patterns

**Application Structure:**
- **Single Application File**: Core app definition in `app.py`
- **Decorator-Based Routing**: Routes defined with `@app.route()` decorator
- **Pipeline System**: Request processing through middleware layers
- **Model-View-Template (MVT)**: Similar to Django/Rails patterns

**Database & ORM:**
- Use pyDAL ORM for all database operations
- Define models with `Model` class inheritance
- Use migrations for schema changes: `emmett migrations generate`, `emmett migrations up`
- Relationships via `belongs_to`, `has_many`, `has_one`, `refers_to`
- Validation at model level with `validation` dictionary
- Callbacks: `before_insert`, `after_insert`, `before_update`, `after_update`, `before_delete`, `after_delete`

**Request/Response Handling:**
- Routes return dictionaries that become template context
- Use `request` object for form data, headers, cookies
- `redirect()` for redirects, `url()` for URL generation
- Pipeline decorators for request processing

**Authentication & Authorization:**
- Built-in `Auth` module for user management
- `@requires()` decorator for protected routes
- Session-based authentication
- Group and permission system available

**Form Handling:**
- `Form` class for generic forms
- `ModelForm` for database-backed forms (deprecated, use `Form.from_model()`)
- Async form processing: `form = await Form.from_model(Model)`
- Built-in validators (presence, email, URL, length, etc.)

### Testing Strategy

**Primary Testing Approach:**
- **Always use Docker for running tests** - ensures consistent environment across all development machines
- Use `pytest` as the testing framework
- Use Emmett's test client for endpoint testing
- Test both success and failure scenarios

**Running Tests:**
```bash
# Docker (REQUIRED - Primary method)
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py

# With verbose output
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v

# With coverage
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py --cov=runtime --cov-report=term-missing

# Specific test
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -k test_name
```

**Local Fallback (Only if Docker unavailable):**
```bash
./run_tests.sh
```

**Test Coverage Requirements:**
- Cover all route handlers
- Test authentication flows
- Test form validation (success and failure)
- Test database operations (CRUD)
- Test authorization rules

**Test Organization:**
- All tests in `runtime/tests.py`
- Use fixtures for common setup
- Clean up test data after tests

### Git Workflow

**Branching Strategy:**
- `master` - Production-ready code
- Feature branches for new capabilities
- Use OpenSpec for planning significant changes

**Commit Conventions:**
- Use clear, descriptive commit messages
- Reference issue/spec numbers when applicable
- Format: `<type>: <description>` (e.g., `feat: add comment system`, `fix: correct validation error`)

**OpenSpec Integration:**
- Create proposals for new features/breaking changes
- Implement from approved proposals
- Archive changes after deployment
- Keep specs in sync with implementation

**Never:**
- Force push to main/master
- Skip commit hooks
- Commit directly without specs for significant changes

## Domain Context

### Emmett Framework Specifics

**Documentation Location:**
- Complete Emmett docs in `/emmett_documentation/`
- Quick reference: `emmett_documentation/documentation_summary.md`
- ORM details: `emmett_documentation/docs/orm/`
- Tutorial: `emmett_documentation/docs/tutorial.md`

**Key Emmett Concepts:**
- **App Configuration**: Set via `app.config.property = value`
- **Pipeline**: Middleware system for request processing
- **Services**: Decorators for JSON/XML output (`@service.json`, `@service.xml`)
- **Extensions**: Pluggable functionality (Auth, CORS, etc.)
- **CLI Commands**: Custom commands via `@app.command()`

**Common Patterns:**
```python
# Route definition
@app.route('/posts/<int:post_id>')
async def show_post(post_id):
    post = Post.get(post_id)
    return {'post': post}

# Form handling
@app.route('/new', methods=['get', 'post'])
async def new_post():
    form = await Form.from_model(Post)
    if form.accepted:
        redirect(url('index'))
    return {'form': form}

# Authentication
@app.route('/admin')
@requires(lambda: auth.user is not None, url('login'))
async def admin():
    return {}
```

**Database Operations:**
```python
# Query all
posts = Post.all().select()

# Filter
posts = Post.where(lambda p: p.published == True).select()

# Get by ID
post = Post.get(id)

# Create
post = Post.create(title="...", text="...")

# Update
post.update_record(title="New Title")

# Delete
post.delete_record()
```

### Bloggy Application

The example application in `runtime/` demonstrates:
- User registration and login
- Admin role for content creation
- Blog post CRUD operations
- Template inheritance (`layout.html` base template)
- Static file serving (CSS)
- Form validation and error handling

## Important Constraints

### Technical Constraints

1. **Docker-First Development**: 
   - **MUST use Docker for all development and testing**
   - Docker environment includes all dependencies (Gemini CLI, Python packages, system libraries)
   - Local scripts are fallback only, not primary workflow

2. **Python Version**: 
   - Minimum Python 3.9
   - Recommended Python 3.13+

3. **Emmett Framework**:
   - Follow Emmett conventions and patterns
   - Use pyDAL for ORM (not SQLAlchemy or other ORMs)
   - Use Renoir for templates (not Jinja2)
   - Use built-in Auth module (not custom auth)

4. **Async/Await**:
   - All route handlers should be async
   - Use `await` for async operations (forms, database queries in some cases)

5. **URL Generation**:
   - Always use `url()` function for URL generation
   - Never hardcode URLs

6. **Simplicity First**:
   - Default to <100 lines of new code
   - Single-file implementations until proven insufficient
   - Avoid frameworks without clear justification
   - Choose boring, proven patterns

### Development Constraints

1. **Testing**: Must pass all pytest tests before deployment
2. **Migrations**: All schema changes must have migrations
3. **No Breaking Changes**: Without proper deprecation and migration path

### Deployment Constraints

1. **Docker Deployment**: Application is containerized
2. **Port 8081**: Default application port
3. **Environment Variables**: Configuration via environment or config files

## External Dependencies

### Required Services
- **PostgreSQL 16**: Primary database (runs in Docker)
- **ASGI Server**: Granian (included)

### Optional Services
- **Redis/Valkey**: For session storage and caching (if configured)
- **SMTP Server**: For email functionality via Mailer
- **WebSocket Support**: Built into Emmett, no external service needed

### Development Dependencies
- **Docker & Docker Compose**: Required for consistent development environment
- **Git**: Version control
- **Gemini CLI**: Available in Docker for AI assistance

### Python Package Dependencies
See `setup/requirements.txt` for complete list:
- emmett>=2.5.0
- granian>=1.3.1
- pytest>=7.0.0
- coverage>=7.0.0
- PyYAML
- And others...

### External Documentation
- [Emmett Framework](https://emmett.sh/docs) - Official documentation
- [Emmett GitHub](https://github.com/emmett-framework/emmett) - Source code and issues
- [pyDAL Documentation](http://www.web2py.com/books/default/chapter/29/06/the-database-abstraction-layer) - ORM reference

### No External APIs
The current Bloggy application is self-contained and doesn't depend on external APIs or services beyond the database.
