"""
Test FastAPI server without MCP integration to isolate the issue.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI

# Create a simple FastAPI app without MCP
test_app = FastAPI(
    title="Test LangChain Documentation Server",
    description="Testing without MCP integration",
    version="1.0.0"
)


@test_app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Health check endpoint to verify the service is running.

    Returns:
        Service status and current timestamp
    """
    return {
        "status": "ok",
        "service": "Test LangChain Documentation Server (No MCP)",
        "timestamp": datetime.now().isoformat(),
        "test": True
    }


@test_app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Test server running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(test_app, host="0.0.0.0", port=8001)
