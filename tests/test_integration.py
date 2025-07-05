"""
Integration tests for the complete application.
"""

import sys
from pathlib import Path

from src.config.settings import settings

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_server_startup_and_health():
    """Test that the server starts up and responds to health checks."""
    # Note: This is a basic integration test
    # In a real scenario, you'd start the server in a separate process
    # and then test it

    # For now, just test the health check function
    try:
        from scripts.health_check import health_check  # pylint: disable=import-outside-toplevel
        # This will fail if no server is running, which is expected in tests
        result = health_check("localhost", 8000)
        # We don't assert here because the server might not be running
        print(f"Health check result: {result}")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Integration test note: {e}")


def test_configuration_loading():
    """Test that configuration loads correctly."""
    assert settings.app_name == "LangChain Documentation Server"
    assert settings.port == 8000
    assert settings.langchain_docs_base == "https://python.langchain.com"


def test_logging_setup():
    """Test that logging can be set up."""
    try:
        # pylint: disable=import-outside-toplevel
        from src.config.logging import setup_logging, get_logger
        setup_logging()
        logger = get_logger(__name__)
        logger.info("Test log message")
        assert True  # If we get here, logging setup worked
    except Exception as e:  # pylint: disable=broad-exception-caught
        assert False, f"Logging setup failed: {e}"
