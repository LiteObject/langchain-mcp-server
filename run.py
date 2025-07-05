#!/usr/bin/env python3
"""
Simple entry point for the LangChain Documentation Server.
This file provides a convenient way to run the server.
"""

import sys
from pathlib import Path

from src.main import main

# Add src to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))


if __name__ == "__main__":
    main()
