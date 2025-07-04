#!/usr/bin/env python3
"""
Test the health endpoint function directly.
"""

try:
    from datetime import datetime
    print("datetime import: OK")
except Exception as e:
    print(f"datetime import failed: {e}")

try:
    from fastapi_server import app
    print("fastapi_server import: OK")
except Exception as e:
    print(f"fastapi_server import failed: {e}")

try:
    # Test the health endpoint function directly
    from fastapi_server import health_check
    result = health_check()
    print(f"health_check function result: {result}")
except Exception as e:
    print(f"health_check function failed: {e}")
    import traceback
    traceback.print_exc()
