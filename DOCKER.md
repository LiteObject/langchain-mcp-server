# MCP Server Docker Setup

This directory contains the Docker configuration for running the BMI MCP Server.

## Files Created

- `Dockerfile` - Multi-stage Docker build configuration
- `docker-compose.yml` - Docker Compose configuration for easy deployment
- `.dockerignore` - Files to exclude from Docker build context

## Building and Running

### Using Docker Compose (Recommended)

```bash
# Build and start the container
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# Stop the container
docker-compose down
```

### Using Docker directly

```bash
# Build the image
docker build -t mcp-server .

# Run the container
docker run -p 8000:8000 mcp-server

# Run in detached mode
docker run -d -p 8000:8000 --name mcp-server-container mcp-server
```

## Accessing the Server

Once running, the server will be available at:
- API: http://localhost:8000
- Health check: http://localhost:8000/health
- BMI calculation: http://localhost:8000/bmi?weight_kg=70&height_m=1.75

## Health Checks

The container includes health checks that verify the `/health` endpoint every 30 seconds.

## Environment Variables

The container sets:
- `PYTHONDONTWRITEBYTECODE=1` - Prevents Python from writing .pyc files
- `PYTHONUNBUFFERED=1` - Ensures Python output is sent straight to terminal
- `PYTHONPATH=/app` - Sets the Python path to the application directory
