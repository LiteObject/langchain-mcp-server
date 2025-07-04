#!/usr/bin/env python3
"""
Test the LangChain documentation endpoints.
"""

import requests
import json


def test_latest_version():
    """Test the latest version endpoint."""
    try:
        response = requests.get(
            "http://localhost:8000/latest-version", timeout=30)
        print(f"Latest Version Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"LangChain Version: {data.get('version', 'Unknown')}")
            print(f"Release Date: {data.get('release_date', 'Unknown')}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Latest version test failed: {e}")
        return False


def test_search():
    """Test the search endpoint."""
    try:
        response = requests.get(
            "http://localhost:8000/search?query=llm&max_results=2",
            timeout=30
        )
        print(f"Search Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} search results")
            if data:
                print(f"First result: {data[0].get('title', 'No title')}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"Search test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing LangChain Documentation Endpoints...")

    print("\n1. Testing latest version endpoint...")
    version_ok = test_latest_version()

    print("\n2. Testing search endpoint...")
    search_ok = test_search()

    if version_ok and search_ok:
        print("\n✅ LangChain documentation service is working!")
    else:
        print("\n⚠️ Some endpoints may need time to initialize or network access")
