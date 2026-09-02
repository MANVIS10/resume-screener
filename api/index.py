"""Vercel serverless entrypoint.

Vercel's Python runtime looks for an ASGI callable named ``app`` in this file
and routes every request here (see the rewrite in vercel.json).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: E402

__all__ = ["app"]
