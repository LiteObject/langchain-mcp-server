"""
Main entry point for the LangChain Documentation Server.
"""

import asyncio
import sys
from pathlib import Path

from .config.settings import settings
from .config.logging import setup_logging

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))


def run_fastapi():
    """Run the FastAPI server."""
    import uvicorn  # pylint: disable=import-outside-toplevel
    from .api.fastapi_app import app  # pylint: disable=import-outside-toplevel

    setup_logging()

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug
    )


def run_mcp():
    """Run the MCP server."""
    from .api.mcp_server import main as mcp_main  # pylint: disable=import-outside-toplevel

    setup_logging()
    asyncio.run(mcp_main())


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        run_mcp()
    else:
        run_fastapi()


if __name__ == "__main__":
    main()
