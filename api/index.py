"""Vercel Serverless Function Entrypoint for FraudSentinel FastAPI API."""

import os
import sys
import tempfile
from pathlib import Path

# Ensure Matplotlib and temporary artifacts use writable directory in AWS Lambda / Vercel
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())
os.environ.setdefault("VERCEL", "1")

# Resolve repository paths
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

for p in [str(ROOT_DIR), str(BACKEND_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.main import app

# Expose ASGI application for @vercel/python
handler = app

