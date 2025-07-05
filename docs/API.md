# API Documentation

## Overview

The LangChain Documentation Server provides a comprehensive REST API for accessing LangChain documentation, API references, code examples, and tutorials in real-time.

## Base URL

- **Local Development**: `http://localhost:8000`
- **Docker**: `http://localhost:8080`

## Authentication

Currently, no authentication is required. Rate limiting may be implemented in the future.

## Endpoints

### Health Check

**GET** `/health`

Returns the current status of the service.

**Response:**
```json
{
  "status": "ok",
  "service": "LangChain Documentation Server",
  "timestamp": "2025-07-04T10:34:12.123456",
  "endpoints_available": 7,
  "data_sources": [
    "python.langchain.com",
    "github.com/langchain-ai/langchain", 
    "pypi.org/project/langchain"
  ],
  "features": [
    "documentation_search",
    "api_reference_lookup",
    "github_examples", 
    "tutorials",
    "version_info"
  ],
  "architecture": "shared_service_layer"
}
```

### Search Documentation

**GET** `/search`

Search through LangChain documentation.

**Parameters:**
- `query` (required): Search term
- `max_results` (optional): Maximum results to return (1-50, default: 10)

**Example:**
```bash
curl "http://localhost:8000/search?query=llm&max_results=5"
```

### Search API Reference

**GET** `/search/api`

Search specifically through API reference documentation.

**Parameters:**
- `query` (required): Search term  
- `max_results` (optional): Maximum results to return (1-50, default: 10)

### Get API Reference

**GET** `/api-reference/{class_name}`

Get detailed API reference for a specific class.

**Example:**
```bash
curl "http://localhost:8000/api-reference/ChatOpenAI"
```

### Get GitHub Examples

**GET** `/examples/github`

Get code examples from the LangChain GitHub repository.

**Parameters:**
- `topic` (required): Topic to search for
- `max_results` (optional): Maximum results to return (1-20, default: 5)

### Get Tutorials

**GET** `/tutorials`

Get LangChain tutorials and guides.

**Parameters:**
- `difficulty` (optional): Filter by difficulty level
- `max_results` (optional): Maximum results to return (1-30, default: 10)

### Get Latest Version

**GET** `/latest-version`

Get the latest LangChain version information from PyPI.

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: External API error

Error responses include a detail message:

```json
{
  "detail": "Error description"
}
```

## Rate Limiting

Currently no rate limiting is implemented, but it may be added in the future for production deployments.

## Interactive Documentation

Visit `/docs` when the server is running to access the interactive Swagger UI documentation.
