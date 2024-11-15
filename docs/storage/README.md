# Storage System Documentation

The storage system provides a robust way to persist API requests, responses, and session data. It features automatic compression, TTL (time-to-live), flexible metadata filtering, and pagination support. The system is designed to be easy to integrate while providing powerful querying capabilities.

## Core Features

- Store and retrieve API requests/responses
- Automatic session management
- Flexible metadata filtering
- Data compression
- Time-to-live (TTL) support 
- Pagination
- Warning system for non-critical issues
- Timezone-aware date filtering

## Setting Up Storage

The easiest way to integrate storage is using the `@store_api_data` decorator. This automatically captures requests, responses, and manages sessions.

### Basic Usage

```python
from app.core.storage.decorators import store_api_data
from app.models.enums import StorageType

@store_api_data(storage_type=StorageType.BOTH)
def my_endpoint():
    return {"message": "This request and response will be stored"}
```

### Advanced Configuration

The decorator supports several options for customizing storage behavior:

```python
@store_api_data(
    storage_type=StorageType.BOTH,      # Store both request and response
    ttl_days=7,                         # Auto-delete after 7 days
    compress=True,                      # Enable compression
    metadata={"version": "v1"},         # Add custom metadata
    session_timeout_minutes=60          # Custom session timeout
)
def advanced_endpoint():
    return {"message": "Configured storage"}
```

The decorator automatically captures:
- Complete request data:
  - HTTP method
  - Request path
  - Query parameters
  - Headers
  - Request body (if JSON)
- Response data
- Session information
- Custom metadata

## Querying Stored Data

The storage system provides several endpoints for retrieving stored data.

### Query Storage
`POST /storage/query`

Query stored API requests and responses with flexible filtering options.

**Request:**
```json
{
    "storage_type": "response",
    "endpoint": "/api/v1/users",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02T00:00:00Z", 
    "metadata_filters": {
        "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "version": "v1"
    },
    "page": 1,
    "page_size": 20
}
```

**Success Response:**
```json
{
    "success": true,
    "message": "Storage entries retrieved",
    "data": {
        "items": [{
            "id": 1,
            "type": "response",
            "endpoint": "/api/v1/users",
            "created_at": "2024-01-01T12:00:00Z",
            "ttl": "2024-01-08T12:00:00Z",
            "storage_info": {
                "session_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "version": "v1"
            },
            "data": {
                "original_response": "data"
            }
        }],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "has_more": false
    }
}
```

### Session Management

Sessions automatically group related requests and responses. The system provides two endpoints for working with sessions:

#### List Sessions (Simple)
`GET /storage/sessions`

Returns a paginated list of sessions with basic information.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `endpoint`: Filter by endpoint
- `storage_type`: Filter by type
- `start_date`: ISO 8601 datetime
- `end_date`: ISO 8601 datetime
- `session_id`: Specific session filter

#### Query Sessions (Detailed)
`POST /storage/sessions/query`

Returns detailed session data including all storage entries.

**Request:**
```json
{
    "endpoint": "/api/v1/users",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-02T00:00:00Z",
    "storage_type": "response",
    "metadata_filters": {
        "version": "v1"
    },
    "page": 1,
    "page_size": 20
}
```

### Data Management

#### Delete Storage (Admin Only)
`POST /storage/delete`

Allows administrators to delete specific storage entries.

```json
{
    "storage_ids": [1, 2, 3],
    "force": false  // Set true to bypass TTL checks
}
```

## Warning System

Instead of failing requests, the system uses warnings to indicate non-critical issues. These warnings help optimize usage and identify potential problems.

### Warning Structure
```json
{
    "code": "WARNING_CODE",
    "message": "Human readable message",
    "severity": "LOW|MEDIUM|HIGH"
}
```

Common warning codes:
- `NO_RESULTS_FOUND`: Query returned empty results
- `PARAMETER_PRECEDENCE`: Conflicting parameters provided
- `DATE_RANGE_LARGE`: Date range might affect performance
- `COMPRESSION_RECOMMENDED`: Large payload detected without compression
- `SESSION_TIMEOUT`: Session timeout occurred
- `METADATA_CONFLICT`: Conflicting metadata values

## Best Practices

### Session Management
- Let the system handle session IDs automatically
- Use session queries to retrieve related data
- Configure session timeout based on your use case (default: 30 minutes)
- Monitor session warnings for timeouts

### Storage Optimization
- Enable compression for large payloads (>1KB)
- Set appropriate TTL values based on data retention needs
- Use indexes effectively (endpoint, user_id, created_at)
- Clean up expired data regularly

### Query Optimization
- Use specific filters to reduce result set size
- Always include date ranges for large datasets
- Combine multiple metadata filters when possible
- Check warning messages for query optimization hints
- Use session_id parameter instead of metadata filter when possible

### Error Handling
- Monitor warning messages in responses
- Handle validation errors gracefully (422)
- Implement retry logic for transient failures (500)
- Log warning messages for debugging