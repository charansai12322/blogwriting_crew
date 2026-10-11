"""
Root entrypoint for deployment platforms (Render, Heroku, etc.).
Guarantees the repository root is placed on sys.path before loading the FastAPI app.

Supports both start commands:
    uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    uvicorn main:app --host 0.0.0.0 --port $PORT
"""

import sys
from pathlib import Path

# Ensure repository root is in sys.path
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from backend.main import app

__all__ = ["app"]
