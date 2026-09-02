"""Create the schema on the configured database.

Run once per environment (local file or Turso) before starting the app:

    python scripts/init_db.py
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db  # noqa: E402

if __name__ == "__main__":
    init_db()
    print(f"Schema applied to {os.environ.get('DATABASE_URL', '').split('@')[-1]}")
