# LangChain Documentation MCP Server

A comprehensive dual-mode server that provides real-time access to LangChain documentation, API references, and code examples. Supports both FastAPI web service and native Model Context Protocol (MCP) server modes, fetching live data from official LangChain sources.

## 🚀 Features

- **�️ Dual Server Modes** - Run as FastAPI web service or native MCP server
- **�📚 Live Documentation Search** - Search through official LangChain documentation in real-time
- **🔍 API Reference Lookup** - Get detailed API references from GitHub source code
- **🐙 GitHub Code Examples** - Fetch real code examples from the LangChain repository
- **📖 Tutorial Discovery** - Find and access LangChain tutorials and guides
- **📦 Version Tracking** - Get latest version information from PyPI
- **🔗 Direct API Search** - Search specifically through API reference documentation
- **🔌 MCP Protocol Support** - Native Model Context Protocol implementation

## 🌐 Data Sources

This server fetches live data from:
- **python.langchain.com** - Official LangChain documentation
- **GitHub LangChain Repository** - Source code and examples
- **PyPI** - Latest version and release information

## 📋 API Endpoints

### Core Endpoints
- `GET /` - API documentation (Swagger UI)
- `GET /health` - Health check and service status

### LangChain Documentation
- `GET /search` - Search general documentation
- `GET /search/api` - Search API reference specifically
- `GET /api-reference/{class_name}` - Get detailed API reference for a class
- `GET /examples/github` - Get real code examples from GitHub
- `GET /tutorials` - Get tutorials and guides
- `GET /latest-version` - Get latest LangChain version info

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/LiteObject/langchain-mcp-server.git
   cd langchain-mcp-server
   ```

2. **Start the FastAPI server**
   ```bash
   docker-compose up --build
   ```

3. **Access the API**
   - API Documentation: http://localhost:8080/docs
   - Health Check: http://localhost:8080/health

### Option 2: Local Development

#### FastAPI Mode
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI server**
   ```bash
   # Using the main entry point
   python run.py
   
   # Or using the dedicated script
   python scripts/run_fastapi.py
   
   # Or directly with uvicorn
   uvicorn src.api.fastapi_app:app --host 0.0.0.0 --port 8000
   ```

#### MCP Server Mode
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the MCP server**
   ```bash
   # Using the main entry point
   python run.py mcp
   
   # Or using the dedicated script
   python scripts/run_mcp.py
   ```

## 📚 Usage Examples

### Search Documentation
```bash
# Search for "ChatOpenAI" in documentation
curl "http://localhost:8080/search?query=ChatOpenAI&limit=5"

# Search API reference specifically
curl "http://localhost:8080/search/api?query=embeddings"
```

### Get API Reference
```bash
# Get detailed API reference for ChatOpenAI
curl "http://localhost:8080/api-reference/ChatOpenAI"

# Get API reference for LLMChain
curl "http://localhost:8080/api-reference/LLMChain"
```

### Fetch Code Examples
```bash
# Get real examples from GitHub
curl "http://localhost:8080/examples/github?query=chatbot&limit=3"

# Get general examples
curl "http://localhost:8080/examples/github"
```

### Get Tutorials
```bash
# Fetch all available tutorials
curl "http://localhost:8080/tutorials"
```

### Version Information
```bash
# Get latest version from PyPI
curl "http://localhost:8080/latest-version"
```

## 🔌 MCP Server Usage

When running in MCP mode, the server provides the following tools:

### Available MCP Tools
- `search_langchain_docs` - Search LangChain documentation
- `search_api_reference` - Search API reference specifically  
- `get_api_reference` - Get detailed API reference for a class
- `get_github_examples` - Get code examples from GitHub
- `get_tutorials` - Get available tutorials
- `get_latest_version` - Get latest LangChain version

### MCP Client Integration
```json
{
  "mcpServers": {
    "langchain-docs": {
      "command": "python",
      "args": ["path/to/langchain-mcp-server/run.py", "mcp"],
      "env": {
        "PYTHONPATH": "path/to/langchain-mcp-server"
      }
    }
  }
}
```

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host address | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `DEBUG` | Enable debug mode | False |
| `LOG_LEVEL` | Logging level | INFO |
| `REQUEST_TIMEOUT` | Timeout for external API calls | 30 seconds |
| `GITHUB_TOKEN` | GitHub API token (optional) | None |

### Docker Configuration

The service runs on port 8080 by default to avoid conflicts. You can modify this in `docker-compose.yml`:

```yaml
ports:
  - "8080:8000"  # Host:Container
```

## 🔧 Development

### Project Structure
```
├── src/                    # Main source code package
│   ├── main.py            # Main entry point with dual mode support
│   ├── api/               # API layer
│   │   ├── fastapi_app.py # FastAPI application
│   │   └── mcp_server.py  # Native MCP server implementation
│   ├── config/            # Configuration management
│   │   ├── settings.py    # Application settings
│   │   └── logging.py     # Logging configuration
│   ├── models/            # Data models and schemas
│   │   └── schemas.py     # Pydantic models
│   ├── services/          # Business logic
│   │   └── langchain_service.py # LangChain documentation service
│   └── utils/             # Utility modules
│       ├── exceptions.py  # Custom exceptions
│       └── helpers.py     # Helper functions
├── scripts/               # Convenience scripts
│   ├── run_fastapi.py    # Run FastAPI mode
│   ├── run_mcp.py        # Run MCP mode
│   └── health_check.py   # Health check utility
├── tests/                 # Test suite
│   ├── test_api.py       # API tests
│   ├── test_services.py  # Service tests
│   └── test_integration.py # Integration tests
├── docs/                  # Documentation
│   └── API.md            # API documentation
├── logs/                  # Log files
├── run.py                # Simple entry point
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project configuration
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── DOCKER.md           # Docker documentation
└── README.md           # This file
```

### Key Dependencies
- **FastAPI** - Web framework for REST API mode
- **MCP** - Native Model Context Protocol support
- **FastAPI-MCP** - MCP integration for FastAPI
- **httpx** - Async HTTP client for external API calls
- **BeautifulSoup4** - HTML parsing for documentation scraping
- **Pydantic** - Data validation and settings management
- **uvicorn** - ASGI server for FastAPI

### Adding New Endpoints

1. Define Pydantic models for request/response
2. Add endpoint function with proper type hints
3. Include comprehensive docstrings
4. Add error handling with specific exceptions
5. Update health check endpoint count

## 🐛 Error Handling

The server includes robust error handling for:
- **Network failures** - Graceful degradation when external APIs are unavailable
- **Rate limiting** - Handles GitHub API rate limits
- **Invalid requests** - Proper HTTP status codes and error messages
- **Timeouts** - Configurable request timeouts

## 📊 Health Monitoring

The `/health` endpoint provides:
- Service status
- Available endpoints count
- Data source URLs
- Current timestamp
- Updated documentation sections

## 🔒 Security Considerations

- **Rate Limiting** - Consider implementing rate limiting for production
- **CORS** - Configure CORS headers if needed for web access
- **API Keys** - Add GitHub token for higher API limits
- **Input Validation** - All inputs are validated using Pydantic

## 🚀 Production Deployment

For production use, consider:

1. **Caching** - Add Redis/Memcached for response caching
2. **Rate Limiting** - Implement request rate limiting
3. **Monitoring** - Add application monitoring and logging
4. **Load Balancing** - Use multiple instances behind a load balancer
5. **Database** - Store frequently accessed data
6. **CI/CD** - Set up automated deployment pipeline

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Links

- [LangChain Documentation](https://python.langchain.com)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Model Context Protocol](https://github.com/modelcontextprotocol/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## 🆘 Support

If you encounter any issues:

1. Check the [health endpoint](http://localhost:8080/health) for service status (FastAPI mode)
2. Review Docker logs: `docker-compose logs`
3. Check application logs in the `logs/` directory
4. Ensure network connectivity to external APIs
5. Verify all dependencies are installed correctly
6. For MCP mode issues, check the MCP client configuration

---

**Note**: This server requires internet connectivity to fetch live data from LangChain's official sources. API rate limits may apply for GitHub API calls.