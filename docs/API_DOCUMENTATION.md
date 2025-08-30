# IPDR Analysis System - API Documentation

## API Overview

The IPDR Analysis System provides comprehensive RESTful API access for programmatic integration with external systems, automated workflows, and custom analysis tools. The API is organized into multiple tiers with different authentication requirements and access levels.

## Authentication and Security

### API Key Authentication
- **Header**: `X-API-Key: <your_api_key>`
- **Bearer Token**: `Authorization: Bearer <your_api_key>`
- **Rate Limiting**: 60 requests per minute per API key (configurable)
- **CORS Support**: Cross-origin resource sharing enabled

### Admin Authentication
- **Header**: `X-Admin-Password: <admin_password>`
- **Query Parameter**: `?admin_password=<admin_password>`
- **IP Restrictions**: Configurable IP address allowlisting

## Public API v1 (`/api/v1/*`)

### Health and Status Endpoints

#### GET `/api/v1/health`
System health check and status information.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "data_loaded": true,
    "dataset_path": "data/raw/hackathon_ipdr_main.csv"
  }
}
```

#### GET `/api/v1/datasets`
List available datasets with metadata.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "name": "hackathon_ipdr_main.csv",
      "path": "data/raw/hackathon_ipdr_main.csv",
      "size": 1048576,
      "modified": "2024-01-15T10:30:15",
      "active": true
    }
  ]
}
```

### Data Access Endpoints

#### GET `/api/v1/records`
Query communication records with advanced filtering and pagination.

**Query Parameters:**
- `limit` (integer, default: 50): Number of records per page
- `page` (integer, default: 1): Page number
- `sort` (string): Sort order (e.g., "timestamp:desc")
- `a_party` (string): Filter by initiating party
- `b_party` (string): Filter by receiving party
- `a_parties` (string): Comma-separated list of A parties
- `b_parties` (string): Comma-separated list of B parties
- `service_type` (string): Filter by service type (VOICE, SMS, DATA)
- `from` (datetime): Start timestamp filter
- `to` (datetime): End timestamp filter
- `min_duration` (integer): Minimum duration filter
- `max_duration` (integer): Maximum duration filter
- `contains` (string): Regex pattern for party matching

**Response:**
```json
{
  "success": true,
  "data": [...],
  "page": 1,
  "limit": 50,
  "total": 1000
}
```

#### GET `/api/v1/records/export`
Export filtered records as CSV file.

**Query Parameters:** Same as records endpoint
**Response:** CSV file download

### Network Analysis Endpoints

#### GET `/api/v1/network/summary`
Get network graph summary statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": 150,
    "edges": 300
  }
}
```

#### GET `/api/v1/network/graph`
Get network graph data for visualization.

**Query Parameters:**
- `nodes` (integer, default: 100): Maximum number of nodes
- `edges` (integer, default: 200): Maximum number of edges

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "entity1",
        "label": "entity1",
        "degree": 5,
        "size": 10
      }
    ],
    "edges": [
      {
        "source": "entity1",
        "target": "entity2"
      }
    ]
  }
}
```

#### GET `/api/v1/network/ego`
Get ego network for specific entity.

**Query Parameters:**
- `entity` (string, required): Target entity identifier
- `hops` (integer, default: 1): Number of network hops

**Response:**
```json
{
  "success": true,
  "data": {
    "nodes": [...],
    "edges": [...]
  }
}
```

### Pattern Analysis Endpoints

#### GET `/api/v1/patterns`
Get communication pattern analysis results.

**Response:**
```json
{
  "success": true,
  "data": {
    "time_patterns": {
      "peak_hours": [9, 10, 14, 15],
      "quiet_hours": [2, 3, 4, 5]
    },
    "top_communicators": {
      "initiators": [["entity1", 150], ["entity2", 120]],
      "recipients": [["entity3", 200], ["entity4", 180]]
    }
  }
}
```

### Job Management Endpoints

#### POST `/api/v1/jobs/records/export`
Create asynchronous export job.

**Request Body:**
```json
{
  "a_party": "entity1",
  "service_type": "VOICE",
  "from": "2024-01-01T00:00:00",
  "to": "2024-01-31T23:59:59"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-string"
  }
}
```

#### GET `/api/v1/jobs/<job_id>`
Get job status and progress.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "job_id",
    "type": "export",
    "status": "completed",
    "progress": 100,
    "result_path": "outputs/exports/export_job_id.csv"
  }
}
```

#### GET `/api/v1/jobs/<job_id>/download`
Download completed export job results.

**Response:** File download

### Documentation Endpoints

#### GET `/api/v1/docs/openapi.json`
OpenAPI 3.0 specification document.

#### GET `/api/v1/docs`
Interactive Swagger UI documentation interface.

## Internal Web Dashboard APIs (`/api/*`)

### Data Management Endpoints

#### POST `/api/load-data`
Load IPDR dataset into system memory.

**Response:**
```json
{
  "success": true,
  "message": "Loaded 1000 records",
  "records_count": 1000,
  "dataset_path": "data/raw/hackathon_ipdr_main.csv"
}
```

#### POST `/api/upload-data`
Upload new dataset file.

**Request:** Multipart form data with file
**Response:**
```json
{
  "success": true,
  "message": "Uploaded dataset.csv. Activate it from the dataset selector to use.",
  "path": "data/raw/uploaded_1234567890_dataset.csv"
}
```

#### POST `/api/generate-data`
Generate synthetic test dataset.

**Request Body:**
```json
{
  "num_records": 10000,
  "days_span": 30
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated dataset saved as generated_1234567890.csv",
  "path": "data/raw/generated_1234567890.csv"
}
```

#### POST `/api/activate-dataset`
Activate specific dataset for analysis.

**Request Body:**
```json
{
  "path": "data/raw/dataset.csv"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Activated dataset with 1000 records",
  "dataset_path": "data/raw/dataset.csv"
}
```

### Analysis Endpoints

#### GET `/api/overview`
Get dashboard overview statistics.

**Response:**
```json
{
  "total_records": 1000,
  "unique_a_parties": 150,
  "unique_b_parties": 200,
  "network_nodes": 150,
  "network_edges": 300,
  "avg_duration": 120,
  "suspicious_count": 5,
  "peak_hours": [9, 10, 14, 15],
  "quiet_hours": [2, 3, 4, 5]
}
```

#### GET `/api/search`
Search for specific entity.

**Query Parameters:**
- `q` (string, required): Search query

**Response:**
```json
{
  "entity": "entity1",
  "total_communications": 150,
  "as_initiator": 100,
  "as_recipient": 50,
  "communication_partners": ["entity2", "entity3"],
  "time_range": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-31T23:59:59"
  },
  "top_partners": [
    {"entity": "entity2", "count": 80},
    {"entity": "entity3", "count": 70}
  ],
  "recent_activity": [...]
}
```

#### GET `/api/suspicious`
Get suspicious activity detection results.

**Response:**
```json
{
  "suspicious_activities": [
    {
      "entity": "entity1",
      "pattern": "unusual_frequency",
      "score": 0.85,
      "details": "Communication frequency 3x above normal"
    }
  ]
}
```

#### GET `/api/network`
Get network graph data for visualization.

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

#### GET `/api/patterns`
Get communication pattern analysis.

**Response:**
```json
{
  "time_patterns": {...},
  "top_communicators": {...}
}
```

### Enhanced Features Endpoints

#### GET `/api/enhanced-analysis`
Get enhanced B-party analysis results.

**Response:**
```json
{
  "success": true,
  "analysis_results": {...},
  "report": {...}
}
```

#### GET `/api/advanced-filtering`
Get advanced filtering system results.

**Response:**
```json
{
  "success": true,
  "filtered_data": [...],
  "statistics": {
    "original_count": 1000,
    "filtered_count": 250,
    "filtered_out_count": 750,
    "active_filters": 3,
    "filter_effectiveness": 25.0
  },
  "active_filters": [...]
}
```

### Case Management Endpoints

#### GET `/api/case-management`
Get case management data and statistics.

**Response:**
```json
{
  "success": true,
  "cases": [...],
  "statistics": {...}
}
```

#### POST `/api/case-management/create`
Create new investigation case.

**Request Body:**
```json
{
  "name": "Case Name",
  "description": "Case description",
  "priority": "high"
}
```

**Response:**
```json
{
  "success": true,
  "case_id": "case_uuid",
  "message": "Case 'Case Name' created successfully"
}
```

#### POST `/api/case-management/<case_id>/add-evidence`
Add evidence to investigation case.

**Request Body:**
```json
{
  "type": "ipdr_record",
  "description": "Evidence description",
  "source": "Analysis Tool"
}
```

**Response:**
```json
{
  "success": true,
  "evidence_id": "evidence_uuid",
  "message": "Evidence added successfully"
}
```

## Administrative APIs (`/api/v1/admin/*`)

### API Key Management

#### GET `/api/v1/admin/keys`
List configured API keys.

**Response:**
```json
{
  "success": true,
  "data": ["key1", "key2", "key3"]
}
```

#### POST `/api/v1/admin/keys`
Add new API key.

**Request Body:**
```json
{
  "key": "new_api_key_string"
}
```

**Response:**
```json
{
  "success": true
}
```

#### DELETE `/api/v1/admin/keys/<key>`
Remove API key.

**Response:**
```json
{
  "success": true
}
```

### Admin Password Management

#### GET `/api/v1/admin/password`
Retrieve admin password (localhost only).

**Response:**
```json
{
  "success": true,
  "data": {
    "password": "admin_password",
    "auto_generated": true
  }
}
```

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human readable error message"
  }
}
```

### Common Error Codes
- `400`: Bad Request - Invalid parameters or request format
- `401`: Unauthorized - Missing or invalid API key
- `403`: Forbidden - Insufficient permissions
- `404`: Not Found - Resource not found
- `429`: Rate Limited - Rate limit exceeded
- `500`: Internal Server Error - Server-side error

## Rate Limiting

### Rate Limit Headers
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets
- `Retry-After`: Seconds to wait before retrying (when rate limited)

### Default Limits
- **Standard API**: 60 requests per minute per API key
- **Admin API**: 60 requests per minute per admin session
- **Export Jobs**: 10 concurrent export jobs per system

## Data Formats

### Supported Input Formats
- **CSV**: Comma-separated values with standard IPDR fields
- **JSON**: JavaScript Object Notation format
- **TXT**: Text-based format with pipe-delimited fields

### IPDR Field Structure
- `timestamp`: ISO 8601 datetime format
- `a_party`: String identifier for initiating party
- `b_party`: String identifier for receiving party
- `duration`: Integer duration in seconds
- `service_type`: Enumeration (VOICE, SMS, DATA)

### Output Formats
- **JSON**: Structured data for API responses
- **CSV**: Tabular data for external analysis tools
- **Binary**: File downloads for exports and visualizations
