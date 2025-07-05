#!/usr/bin/env python3
"""
Health check script for the LangChain Documentation Server.
"""

from src.config.settings import settings
import sys
import requests
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def health_check(host: str = None, port: int = None) -> bool:
    """
    Check if the server is healthy.

    Args:
        host: Server host (defaults to settings.host)
        port: Server port (defaults to settings.port)

    Returns:
        True if server is healthy, False otherwise
    """
    host = host or settings.host
    port = port or settings.port

    # Use localhost instead of 0.0.0.0 for health checks
    if host == "0.0.0.0":
        host = "localhost"

    url = f"http://{host}:{port}/health"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'Unknown')}")
            return True
        else:
            print(f"❌ Server returned status code {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Server at {url} timed out")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Health check for LangChain Documentation Server")
    parser.add_argument("--host", default=None, help="Server host")
    parser.add_argument("--port", type=int, default=None, help="Server port")

    args = parser.parse_args()

    print("Performing health check...")
    healthy = health_check(args.host, args.port)

    sys.exit(0 if healthy else 1)


if __name__ == "__main__":
    main()
