"""
Vercel Serverless Function entry point for Student Result Management System.
Exposes the ASGI FastAPI application for Vercel Python runtime.
"""

import os
import sys

# Ensure project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
