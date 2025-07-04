#!/usr/bin/env python3
"""
Test the test server on port 8001.
"""

import requests


def test_health_on_8001():
    """Test the health endpoint on the test server."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    print("Testing server without MCP integration...")
    if test_health_on_8001():
        print("✅ Test server works!")
    else:
        print("❌ Test server failed!")
