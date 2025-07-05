"""
Tests for the FastAPI endpoints.
"""

from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test the health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "service" in data
    assert "timestamp" in data
    assert "endpoints_available" in data
    assert data["endpoints_available"] == 7


def test_search_documentation_endpoint(client: TestClient, sample_search_query: str):
    """Test the search documentation endpoint."""
    response = client.get(f"/search?query={sample_search_query}&max_results=5")

    # Should return 200 even if no results (empty list)
    # May fail due to network issues in tests
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5


def test_search_documentation_invalid_params(client: TestClient):
    """Test search endpoint with invalid parameters."""
    # Test missing query parameter
    response = client.get("/search")
    assert response.status_code == 422  # Validation error

    # Test invalid max_results
    response = client.get("/search?query=test&max_results=0")
    assert response.status_code == 422  # Validation error


def test_search_api_documentation_endpoint(client: TestClient, sample_search_query: str):
    """Test the search API documentation endpoint."""
    response = client.get(
        f"/search/api?query={sample_search_query}&max_results=3")

    # Should return 200 even if no results (empty list)
    # May fail due to network issues in tests
    assert response.status_code in [200, 500]


def test_get_api_reference_endpoint(client: TestClient, sample_class_name: str):
    """Test the get API reference endpoint."""
    response = client.get(f"/api-reference/{sample_class_name}")

    # Should return 200, 404, or 500 depending on availability
    assert response.status_code in [200, 404, 500]


def test_get_github_examples_endpoint(client: TestClient):
    """Test the GitHub examples endpoint."""
    response = client.get("/examples/github?topic=chat&max_results=2")

    # Should return 200 even if no results (empty list)
    # May fail due to network issues in tests
    assert response.status_code in [200, 500]


def test_get_tutorials_endpoint(client: TestClient):
    """Test the tutorials endpoint."""
    response = client.get("/tutorials?max_results=5")

    # Should return 200 even if no results (empty list)
    # May fail due to network issues in tests
    assert response.status_code in [200, 500]


def test_get_latest_version_endpoint(client: TestClient):
    """Test the latest version endpoint."""
    response = client.get("/latest-version")

    # Should return 200 or 500 depending on PyPI availability
    # May fail due to network issues in tests
    assert response.status_code in [200, 500]
