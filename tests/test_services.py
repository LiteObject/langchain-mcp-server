"""
Tests for the LangChain service layer.
"""

import sys
from pathlib import Path

import pytest

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_langchain_service_import():
    """Test that the LangChain service can be imported."""
    try:
        # pylint: disable=import-outside-toplevel
        from src.services.langchain_service import LangChainDocumentationService
        service = LangChainDocumentationService()
        assert service is not None
    except ImportError as e:
        pytest.fail(f"Failed to import LangChainDocumentationService: {e}")


def test_service_models_import():
    """Test that service models can be imported."""
    try:
        # pylint: disable=import-outside-toplevel
        from src.services.langchain_service import (
            DocSearchResult,
            APIReference,
            GitHubExample,
            TutorialInfo,
            VersionInfo
        )
        assert all([DocSearchResult, APIReference,
                   GitHubExample, TutorialInfo, VersionInfo])
    except ImportError as e:
        pytest.fail(f"Failed to import service models: {e}")


# Note: Additional service tests would go here
# These would test the actual service methods with mocked external dependencies
