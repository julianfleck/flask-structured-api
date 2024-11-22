# Storage System Documentation

The storage system helps you persist API requests, responses, and session data. It's particularly useful for tracking AI model interactions, caching expensive operations, or maintaining audit trails of user interactions. With built-in features like compression and TTL management, it aims to make data storage and retrieval straightforward while giving you the flexibility to query and analyze your stored data.

## Use Cases

Common scenarios where the storage system can help:

- **AI Model Interactions**: Track prompts and responses for analysis or training
- **Caching**: Store expensive computation results
- **Audit Trails**: Monitor user interactions and changes
- **Debugging**: Review past API behavior
- **Analytics**: Understand API usage patterns

## Quick Start

Add storage to any endpoint with a single decorator:

```python
from flask_structured_api.core.storage.decorators import store_api_data

@store_api_data()  # Stores both request and response by default
def generate_text():
    response = ai_service.generate(request.json["prompt"])
    return {"text": response}
```

## Core Concepts

### Storage Types

The system can store requests, responses, or both:
```python
@store_api_data(storage_type=StorageType.RESPONSE)  # Store only responses
@store_api_data(storage_type=StorageType.REQUEST)   # Store only requests
@store_api_data(storage_type=StorageType.BOTH)      # Store both (default)
```

### Sessions

Sessions automatically group related requests. For example, when a user is refining AI-generated text through multiple iterations, all those interactions are part of one session.

```python
@store_api_data(
    session_timeout_minutes=60  # Group requests for 60 minutes
)
def refine_text():
    return ai_service.refine(request.json["text"])
```

### Data Management

The system includes built-in features for efficient data handling:

```python
@store_api_data(
    ttl_days=30,        # Auto-expire after 30 days
    compress=True,      # Compress large responses
    metadata={          # Add custom metadata
        "model": "gpt-4",
        "version": "1.0"
    }
)
```

## API Reference

### Storage Endpoints

#### Query Storage
`POST /storage/query`

Search through stored requests and responses.

**Parameters:**
- `storage_type`: Type of data to retrieve (`request`|`response`)
- `endpoint`: Filter by API endpoint
- `start_date`: ISO 8601 datetime
- `end_date`: ISO 8601 datetime
- `metadata_filters`: Custom metadata filters
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Example Request:**
```json
{
    "storage_type": "response",
    "endpoint": "/api/v1/ai/generate",
    "start_date": "2024-03-01T00:00:00Z",
    "end_date": "2024-03-02T00:00:00Z",
    "metadata_filters": {
        "model": "gpt-4"
    },
    "page": 1,
    "page_size": 20
}
```

**Example Response:**
```json
{
    "success": true,
    "data": {
        "items": [{
            "id": 1,
            "type": "response",
            "endpoint": "/api/v1/ai/generate",
            "created_at": "2024-03-01T12:00:00Z",
            "ttl": "2024-03-31T12:00:00Z",
            "storage_info": {
                "model": "gpt-4",
                "session_id": "f47ac10b-58cc"
            },
            "data": {
                "text": "Generated response",
                "tokens": 150
            }
        }],
        "total": 1,
        "page": 1,
        "page_size": 20,
        "has_more": false
    }
}
```

### Session Endpoints

#### List Sessions
`GET /storage/sessions`

Get an overview of storage sessions.

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `endpoint`: Filter by endpoint
- `start_date`: ISO 8601 datetime
- `end_date`: ISO 8601 datetime
- `session_id`: Specific session filter

#### Query Session Details
`POST /storage/sessions/query`

Get detailed session data including storage entries.

**Parameters:**
All parameters from List Sessions, plus:
- `entries_per_session`: Maximum entries to return per session
- `metadata_filters`: Filter by custom metadata

### Admin Endpoints

#### Delete Storage
`POST /storage/delete` (Admin Only)

Delete specific storage entries.

**Parameters:**
- `storage_ids`: Array of IDs to delete
- `force`: Bypass TTL checks (default: false)

## Warning System

The system uses warnings to indicate potential issues or optimization opportunities:

```json
{
    "code": "WARNING_CODE",
    "message": "Human readable message",
    "severity": "LOW|MEDIUM|HIGH"
}
```

### Implemented Warnings

- `NO_RESULTS_FOUND`: Query returned no matching entries
  - Severity: MEDIUM
  - Includes details about which filters caused no matches

- `PARAMETER_PRECEDENCE`: Multiple ways to specify the same parameter
  - Severity: LOW
  - Example: "Both session_id parameter and metadata_filters['session_id'] provided"

- `ENDPOINT_NORMALIZED`: Endpoint was normalized to match stored data
  - Severity: LOW
  - Shows original and normalized endpoint paths

## Best Practices

### Data Management
- Set realistic TTL values
- Use compression for responses >1KB
- Add relevant metadata for querying
- Clean up expired data regularly

### Query Optimization
- Include date ranges
- Filter by specific endpoints
- Use metadata filters effectively
- Monitor warning messages

### Session Management
- Let the system handle session IDs
- Set appropriate timeouts
- Use session queries for related data
- Watch for session warnings

## Security

### Access Control
- Users can only access their own data
- Sessions are user-isolated
- Deletion requires admin rights

### Data Protection
- Filter sensitive data before storage
- Track sensitive data with metadata
- Use compression for large payloads

### Resource Management
- Set appropriate TTLs
- Use pagination
- Monitor usage per user

## Troubleshooting

### Missing Data
- Verify TTL settings
- Check user permissions
- Confirm storage configuration

### Performance Issues
- Use date filters
- Enable compression
- Add recommended indexes

### Session Problems
- Check timeout settings
- Verify session IDs
- Monitor session warnings

The storage system aims to make data persistence straightforward while giving you the tools to manage and analyze your API interactions effectively. Start with the basic decorator and add features as needed.


### Future Improvements

#### High Priority
1. **Query Improvements**
   - Full-text search in stored data
   - Advanced metadata filtering (regex, ranges)
   - Bulk operations for data management
   - Query performance metrics

2. **Storage Optimization**
   - Smart compression based on content type
   - Automatic cleanup of expired entries
   - Storage quota management per user
   - Compression ratio monitoring

3. **Session Enhancements**
   - Session tagging for organization
   - Session context tracking
   - Cross-session analysis
   - Custom session grouping rules

#### Medium Priority
4. **Data Analysis**
   - Usage statistics per endpoint
   - Pattern detection in stored data
   - Basic analytics endpoints
   - Export functionality (CSV, JSON)

5. **Warning System Expansion**
- `LARGE_PAYLOAD`: Response size exceeds recommended limits
- `SESSION_TIMEOUT`: Session has timed out
- `INDEX_MISSING`: Query performance could be improved with index
- `TTL_APPROACHING`: Entries near expiration
- `COMPRESSION_RECOMMENDED`: Large uncompressed payload detected
- `DUPLICATE_METADATA`: Conflicting metadata values

#### Future Considerations
6. **Integration Features**
   - Webhook notifications
   - External storage support (S3)
   - Logging system integration
   - Backup/restore functionality

7. **Advanced Analytics**
   - Custom metrics tracking
   - Trend analysis
   - Usage forecasting
   - Cost optimization suggestions
