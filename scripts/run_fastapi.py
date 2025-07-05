#!/usr/bin/env python3
"""
Script to run the FastAPI server.
"""

from src.main import run_fastapi
import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


if __name__ == "__main__":
    run_fastapi()
