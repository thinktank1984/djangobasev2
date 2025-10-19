# Project Context

## Purpose

This is a **Django SaaS boilerplate project** based on [eriktaveras/django-saas-boilerplate](https://github.com/eriktaveras/django-saas-boilerplate). It provides a complete foundation for building Software-as-a-Service applications with Django featuring:

- Multi-tenant architecture support
- User authentication and authorization with Django Allauth
- Subscription management and billing capabilities
- Admin interface for business operations
- RESTful API endpoints
- Blog/content management system
- Form handling and validation
- Database relationships using Django ORM
- Template inheritance with Django templates

The project serves as a production-ready starting point for SaaS applications using Django best practices.

## Tech Stack

### Core Framework
- **Django 5.2+** - Python web framework
- **Python 3.9+** (3.12+ recommended)
- **Django ORM** - Database abstraction layer
- **Django Templates** - Template engine
- **PostgreSQL** - Primary database backend

### Third-Party Packages
- **Django Allauth** - Authentication and user management
- **Django REST Framework** - API development
- **Celery** - Background task processing
- **Redis** - Caching and message broker
- **Whitenoise** - Static file serving
- **Gunicorn** - WSGI server

### Infrastructure & Deployment
- **Docker** - Primary development and deployment environment
- **Docker Compose** - Multi-container orchestration
- **PostgreSQL** - Production database
- **Nginx** - Reverse proxy (production)

### Development Tools
- **pytest** - Testing framework
- **coverage** - Test coverage reporting
- **black** - Code formatting
- **flake8** - Linting
- **pre-commit** - Git hooks

### Additional Capabilities
- Multi-tenant architecture with site-based separation
- Subscription management with billing integration
- User role and permission system
- Email notifications and templates
- File upload and media management
- API rate limiting and throttling
- Comprehensive logging and monitoring

## Project Conventions

### Code Style

**Python Conventions:**
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Prefer explicit over implicit
- Use type hints where beneficial
- Apply black code formatting

**Django-Specific Patterns:**
- Define models with clear field types and constraints
- Use `ForeignKey`, `ManyToManyField`, `OneToOneField` for relationships
- Validation in model classes and forms
- Use Django's class-based views where appropriate
- Use `@login_required` and permission decorators
- Return `HttpResponse` or render templates from views

**File Organization:**
- Main application in `blogapp/`
- Settings in `blogapp/core/settings.py`
- Templates in `blogapp/templates/`
- Static files in `blogapp/static/`
- Migrations in each app's `migrations/`
- Management commands in app's `management/commands/`

**Naming Conventions:**
- Models: PascalCase (e.g., `Post`, `Comment`, `User`)
- Views: PascalCase for class-based, snake_case for function-based
- Templates: lowercase with underscores (e.g., `post_list.html`, `base.html`)
- Database fields: snake_case
- URLs: snake_case

### Architecture Patterns

**Application Structure:**
- **Project Layout**: Standard Django project structure with `blogapp/` as main project
- **App-Based Modularity**: Features organized into Django apps
- **Settings Management**: Environment-based configuration
- **URL Routing**: Centralized URL configuration with app-specific includes

**Database & ORM:**
- Use Django ORM for all database operations
- Define models inheriting from `django.db.models.Model`
- Use migrations for schema changes: `python manage.py makemigrations`, `python manage.py migrate`
- Relationships via `ForeignKey`, `ManyToManyField`, `OneToOneField`
- Validation at model and form level
- Signals for cross-model operations

**Request/Response Handling:**
- Use Django's request-response cycle
- Class-based views for complex logic, function-based for simple cases
- Context processors for template data
- Middleware for cross-cutting concerns
- Django forms for validation and processing

**Authentication & Authorization:**
- Django Allauth for user management
- Login required decorators for protected views
- Django's built-in permission system
- Group-based permissions
- Session-based authentication

**Form Handling:**
- Django Form classes for validation
- ModelForm for database-backed forms
- CSRF protection enabled
- File upload handling

### Testing Strategy

**Primary Testing Approach:**
- **Always use Docker for running tests** - ensures consistent environment
- Use `pytest` as the testing framework
- Use Django's test client for endpoint testing
- Test both success and failure scenarios

**Running Tests:**
```bash
# Docker (REQUIRED - Primary method)
docker compose exec blogapp pytest

# With verbose output
docker compose exec blogapp pytest -v

# With coverage
docker compose exec blogapp pytest --cov=blogapp --cov-report=term-missing

# Specific test
docker compose exec blogapp pytest -k test_name
```

**Test Coverage Requirements:**
- Cover all view functions and classes
- Test model methods and properties
- Test form validation (success and failure)
- Test authentication flows
- Test API endpoints

**Test Organization:**
- Tests in each app's `tests.py` or `tests/` directory
- Use fixtures for common setup
- Clean up test data after tests

### Git Workflow

**Branching Strategy:**
- `main` - Production-ready code
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

## Domain Context

### Django SaaS Boilerplate Specifics

**Key Django Concepts:**
- **Settings Configuration**: Environment-based settings management
- **Middleware Stack**: Request processing through middleware layers
- **Class-Based Views**: Reusable view patterns
- **Custom Management Commands**: Administrative task automation
- **Signal System**: Event-driven programming

**Common Patterns:**
```python
# Model definition
class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# View definition
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'

# Form handling
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

# URL configuration
path('posts/', PostListView.as_view(), name='post-list')
```

**Database Operations:**
```python
# Query all
posts = Post.objects.all()

# Filter
posts = Post.objects.filter(published=True)

# Get by ID
post = Post.objects.get(id=pk)

# Create
post = Post.objects.create(title="...", content="...")

# Update
post.title = "New Title"
post.save()

# Delete
post.delete()
```

### SaaS Application Features

The boilerplate includes:
- User registration and authentication with email verification
- Subscription management with different tiers
- Multi-tenant site management
- Admin interface for business operations
- API endpoints for frontend integration
- Blog/content management system
- Comprehensive logging and error tracking

## Important Constraints

### Technical Constraints

1. **Docker-First Development**:
   - **MUST use Docker for all development and testing**
   - Docker environment includes all dependencies
   - Local scripts are fallback only, not primary workflow

2. **Python Version**:
   - Minimum Python 3.9
   - Recommended Python 3.12+

3. **Django Framework**:
   - Follow Django conventions and patterns
   - Use Django ORM for database operations
   - Use Django templates for frontend
   - Use Django Allauth for authentication

4. **Database**:
   - PostgreSQL for production
   - SQLite for development/testing if needed
   - All schema changes must have migrations

5. **Security**:
   - Use Django's built-in security features
   - Environment variables for sensitive data
   - HTTPS in production
   - Proper CORS and CSRF configuration

6. **Simplicity First**:
   - Default to <100 lines of new code
   - Single-app implementations until proven insufficient
   - Avoid frameworks without clear justification
   - Choose boring, proven patterns

### Development Constraints

1. **Testing**: Must pass all pytest tests before deployment
2. **Migrations**: All schema changes must have migrations
3. **No Breaking Changes**: Without proper deprecation and migration path

### Deployment Constraints

1. **Docker Deployment**: Application is containerized
2. **Environment Variables**: Configuration via environment
3. **Static Files**: Properly served and collected
4. **Database Migrations**: Applied during deployment

## External Dependencies

### Required Services
- **PostgreSQL**: Primary database (runs in Docker)
- **Redis**: Caching and message broker
- **Email Service**: For transactional emails (SMTP)

### Optional Services
- **Celery Workers**: For background tasks
- **Nginx**: Reverse proxy and static file serving
- **Monitoring**: Error tracking and performance monitoring

### Development Dependencies
- **Docker & Docker Compose**: Required for consistent development environment
- **Git**: Version control

### Python Package Dependencies
See `blogapp/requirements.txt` for complete list

### External Documentation
- [Django Documentation](https://docs.djangoproject.com/) - Official documentation
- [Django Allauth](https://django-allauth.readthedocs.io/) - Authentication documentation
- [Django REST Framework](https://www.django-rest-framework.org/) - API documentation

### External APIs
The application may integrate with external SaaS services:
- Payment processors (Stripe, etc.)
- Email services (SendGrid, etc.)
- Monitoring services (Sentry, etc.)