#!/usr/bin/env python3
"""
Detailed test script to debug the health endpoint issue.
"""

import requests


def test_health_detailed():
    """Test the health endpoint with detailed error reporting."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Raw Response: {response.text}")

        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"JSON Response: {json_response}")
            except Exception as e:
                print(f"Failed to parse JSON: {e}")

    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    print("Debugging health endpoint...")
    test_health_detailed()
