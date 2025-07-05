"""
Pytest configuration and fixtures.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from src.api.fastapi_app import app  # pylint: disable=import-outside-toplevel
    return TestClient(app)


@pytest.fixture
def mock_langchain_service():
    """Mock LangChain service for testing."""
    # This would contain mock implementations
    # for isolated unit testing
    return None


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return "llm"


@pytest.fixture
def sample_class_name():
    """Sample class name for testing."""
    return "ChatOpenAI"
