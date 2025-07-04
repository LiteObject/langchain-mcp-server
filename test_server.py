#!/usr/bin/env python3
"""
Simple test script to verify the server is working correctly.
"""

import requests
import sys


def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False


def test_docs_endpoint():
    """Test the documentation root endpoint."""
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        print(f"Docs Status Code: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing docs endpoint: {e}")
        return False


if __name__ == "__main__":
    print("Testing LangChain Documentation Server...")

    print("\n1. Testing health endpoint...")
    health_ok = test_health_endpoint()

    print("\n2. Testing docs endpoint...")
    docs_ok = test_docs_endpoint()

    if health_ok and docs_ok:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
