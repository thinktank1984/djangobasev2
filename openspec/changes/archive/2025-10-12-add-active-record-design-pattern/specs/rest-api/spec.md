# REST API Auto-Generation Specification

## ADDED Requirements

### Requirement: Automatic REST API Generation
The system SHALL automatically generate RESTful API endpoints for all Active Record models with standard CRUD operations.

#### Scenario: Generate CRUD endpoints for model
- **WHEN** a model inherits from `ActiveRecord` with `Meta.auto_generate_api = True`
- **THEN** generate five standard endpoints: list (GET), retrieve (GET), create (POST), update (PUT), delete (DELETE)
- **AND** register endpoints with the application router automatically
- **AND** use model name (pluralized and lowercased) as the resource path

#### Scenario: List endpoint with pagination
- **WHEN** GET request to `/api/{model_plural}` (e.g., `/api/posts`)
- **THEN** return paginated list of all records
- **AND** support query parameters: `page`, `per_page`, `sort`, `filter`
- **AND** return response with metadata: `total`, `page`, `per_page`, `items`

#### Scenario: Retrieve single record
- **WHEN** GET request to `/api/{model_plural}/:id`
- **THEN** return single record with all fields
- **AND** return 404 if record not found
- **AND** include related records if specified in query parameter `include`

#### Scenario: Create new record via API
- **WHEN** POST request to `/api/{model_plural}` with JSON body
- **THEN** validate request data using model validators
- **AND** create new record if validation passes
- **AND** return 201 with created record and `Location` header
- **AND** return 422 with validation errors if validation fails

#### Scenario: Update existing record via API
- **WHEN** PUT request to `/api/{model_plural}/:id` with JSON body
- **THEN** validate request data using model validators
- **AND** update record if validation passes and permissions allow
- **AND** return 200 with updated record
- **AND** return 404 if record not found
- **AND** return 403 if user lacks permission

#### Scenario: Delete record via API
- **WHEN** DELETE request to `/api/{model_plural}/:id`
- **THEN** soft-delete or hard-delete record based on model configuration
- **AND** return 204 No Content on success
- **AND** return 404 if record not found
- **AND** return 403 if user lacks permission

---

### Requirement: Automatic OpenAPI/Swagger Documentation
The system SHALL automatically generate OpenAPI 3.0 specification for all auto-generated REST endpoints.

#### Scenario: Generate OpenAPI spec from models
- **WHEN** accessing `/api/docs` or `/swagger.json`
- **THEN** return complete OpenAPI 3.0 specification
- **AND** include all model schemas with field types and constraints
- **AND** include all endpoints with request/response schemas
- **AND** include validation rules from model validators

#### Scenario: Swagger UI for interactive documentation
- **WHEN** accessing `/api/docs` or `/swagger`
- **THEN** render interactive Swagger UI
- **AND** allow testing endpoints directly from the browser
- **AND** show authentication options if endpoints require auth

#### Scenario: Include validation constraints in schema
- **WHEN** model has `@validates` decorators
- **THEN** include validation rules in OpenAPI schema
- **AND** map Python validators to OpenAPI formats (e.g., `minLength`, `pattern`, `format`)
- **AND** include custom validation error messages in description

---

### Requirement: Request Validation
The system SHALL automatically validate API requests using model validators before processing.

#### Scenario: Validate required fields
- **WHEN** API request missing required fields
- **THEN** return 422 Unprocessable Entity
- **AND** include error details: `{"field": "title", "error": "Field is required"}`

#### Scenario: Validate field types
- **WHEN** API request contains invalid field type
- **THEN** return 422 Unprocessable Entity
- **AND** include error details: `{"field": "age", "error": "Must be an integer"}`

#### Scenario: Run custom validators
- **WHEN** API request triggers custom `@validates` decorator
- **THEN** execute validator function
- **AND** return 422 if validator returns error message
- **AND** proceed with operation if validator passes

---

### Requirement: Response Serialization
The system SHALL automatically serialize model instances to JSON responses with consistent formatting.

#### Scenario: Serialize single record
- **WHEN** API endpoint returns single model instance
- **THEN** convert to JSON with all public fields
- **AND** exclude private fields (starting with `_`)
- **AND** include computed fields marked with `@computed_field`
- **AND** exclude relationships unless explicitly included

#### Scenario: Serialize list of records
- **WHEN** API endpoint returns multiple model instances
- **THEN** convert to JSON array with pagination metadata
- **AND** format: `{"items": [...], "total": 100, "page": 1, "per_page": 25}`

#### Scenario: Include nested relationships
- **WHEN** API request includes `?include=user,comments` query parameter
- **THEN** serialize nested relationships
- **AND** prevent circular references
- **AND** limit nesting depth to prevent performance issues

---

### Requirement: Error Handling
The system SHALL provide consistent error responses across all auto-generated API endpoints.

#### Scenario: Resource not found
- **WHEN** requesting non-existent record
- **THEN** return 404 Not Found
- **AND** include error message: `{"error": "Post not found", "code": "not_found"}`

#### Scenario: Validation error
- **WHEN** request data fails validation
- **THEN** return 422 Unprocessable Entity
- **AND** include all validation errors with field names

#### Scenario: Permission denied
- **WHEN** user lacks required permissions
- **THEN** return 403 Forbidden
- **AND** include error message indicating required permission

#### Scenario: Server error
- **WHEN** unexpected error occurs during processing
- **THEN** return 500 Internal Server Error
- **AND** log full error details server-side
- **AND** return generic error message to client (no stack traces)

---

### Requirement: Query Parameters
The system SHALL support standard query parameters for filtering, sorting, and pagination on list endpoints.

#### Scenario: Pagination with page and per_page
- **WHEN** GET `/api/posts?page=2&per_page=10`
- **THEN** return records 11-20
- **AND** include pagination metadata in response

#### Scenario: Sorting with sort parameter
- **WHEN** GET `/api/posts?sort=-created_at,title`
- **THEN** sort by `created_at` descending, then `title` ascending
- **AND** validate sort fields exist on model

#### Scenario: Filtering with field parameters
- **WHEN** GET `/api/posts?published=true&user_id=123`
- **THEN** filter records matching all specified field values
- **AND** support operators: `field__gt`, `field__lt`, `field__contains`, etc.

#### Scenario: Search across text fields
- **WHEN** GET `/api/posts?q=search+term`
- **THEN** search across all text fields defined in model
- **AND** use case-insensitive matching
- **AND** return ranked results by relevance

---

### Requirement: API Versioning
The system SHALL support API versioning through URL prefix configuration.

#### Scenario: Configure API version prefix
- **WHEN** model specifies `Meta.api_prefix = '/api/v1'`
- **THEN** generate endpoints under `/api/v1/posts` instead of `/api/posts`

#### Scenario: Multiple API versions
- **WHEN** application has models with different API versions
- **THEN** maintain separate endpoint namespaces for each version
- **AND** each version has its own OpenAPI documentation

---

### Requirement: Bulk Operations
The system SHALL support bulk operations for creating, updating, and deleting multiple records.

#### Scenario: Bulk create
- **WHEN** POST `/api/posts/bulk` with array of objects
- **THEN** create all valid records
- **AND** return 207 Multi-Status with individual results
- **AND** report validation errors for invalid items

#### Scenario: Bulk update
- **WHEN** PUT `/api/posts/bulk` with array of id-value pairs
- **THEN** update all specified records
- **AND** check permissions for each record
- **AND** return results for each update attempt

#### Scenario: Bulk delete
- **WHEN** DELETE `/api/posts/bulk` with array of IDs
- **THEN** delete all specified records
- **AND** check permissions for each record
- **AND** return count of successfully deleted records

---

### Requirement: Rate Limiting
The system SHALL provide configurable rate limiting for auto-generated API endpoints.

#### Scenario: Configure rate limit per model
- **WHEN** model specifies `Meta.rate_limit = '100/hour'`
- **THEN** enforce rate limit on all endpoints for that model
- **AND** return 429 Too Many Requests when limit exceeded
- **AND** include `Retry-After` header

#### Scenario: Different limits for different operations
- **WHEN** model specifies `Meta.rate_limits = {'read': '1000/hour', 'write': '100/hour'}`
- **THEN** apply different limits to GET vs POST/PUT/DELETE
- **AND** track limits separately per operation type

---

### Requirement: Webhook Support
The system SHALL optionally trigger webhooks for create, update, and delete operations.

#### Scenario: Register webhooks for model events
- **WHEN** model specifies `Meta.webhooks = True`
- **THEN** trigger webhook on create, update, delete operations
- **AND** POST event data to configured webhook URLs
- **AND** include event type, timestamp, and record data

#### Scenario: Webhook delivery guarantee
- **WHEN** webhook endpoint is unreachable
- **THEN** retry with exponential backoff
- **AND** log failed webhook deliveries
- **AND** provide webhook delivery status API

---

## Configuration Reference

### Model Meta Options

```python
class Post(Model, ActiveRecord):
    class Meta:
        # API Generation
        auto_generate_api = True           # Default: True
        api_prefix = '/api'                # Default: '/api'
        api_version = 'v1'                 # Default: None
        
        # Pagination
        list_page_size = 25                # Default: 25
        max_page_size = 100                # Default: 100
        
        # Permissions
        require_auth_for_read = False      # Default: False
        require_auth_for_write = True      # Default: True
        ownership_field = 'user_id'        # Default: 'user_id'
        
        # Features
        enable_bulk_operations = True      # Default: True
        enable_search = True               # Default: True
        searchable_fields = ['title', 'content']  # Default: all text fields
        
        # Rate Limiting
        rate_limit = '100/hour'            # Default: None
        rate_limits = {                    # Default: None
            'read': '1000/hour',
            'write': '100/hour'
        }
        
        # Webhooks
        webhooks = False                   # Default: False
        webhook_events = ['create', 'update', 'delete']  # Default: all
        
        # Soft Delete
        soft_delete = False                # Default: False
        soft_delete_field = 'deleted_at'   # Default: 'deleted_at'
```

---

## Integration Example

### Model Definition

```python
class Post(Model, ActiveRecord):
    tablename = "posts"
    
    title = Field.string()
    content = Field.text()
    user_id = Field.int()
    published = Field.bool(default=False)
    
    @validates('title')
    def validate_title(self, value):
        if len(value) < 3:
            return "Title must be at least 3 characters"
    
    class Meta:
        auto_generate_api = True
        api_prefix = '/api/v1'
        require_auth_for_write = True
        ownership_field = 'user_id'
        searchable_fields = ['title', 'content']
```

### Generated Endpoints

```
GET    /api/v1/posts           - List posts (public)
GET    /api/v1/posts/:id       - Get post (public)
POST   /api/v1/posts           - Create post (auth required)
PUT    /api/v1/posts/:id       - Update post (owner or admin)
DELETE /api/v1/posts/:id       - Delete post (owner or admin)
POST   /api/v1/posts/bulk      - Bulk create (auth required)
PUT    /api/v1/posts/bulk      - Bulk update (auth required)
DELETE /api/v1/posts/bulk      - Bulk delete (auth required)
```

### Generated OpenAPI Schema

```yaml
components:
  schemas:
    Post:
      type: object
      required: [title, content]
      properties:
        id:
          type: integer
          readOnly: true
        title:
          type: string
          minLength: 3
        content:
          type: string
        published:
          type: boolean
          default: false
        created_at:
          type: string
          format: date-time
          readOnly: true
```

