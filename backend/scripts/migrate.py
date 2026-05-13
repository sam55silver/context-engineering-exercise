#!/usr/bin/env python
"""Run pending database migrations."""

import sqlite3
import sys
from pathlib import Path

# Add backend to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrate import get_runner


def run_migrations():
    """Run all pending migrations."""
    runner = get_runner()
    
    # Create database file if it doesn't exist
    if not runner.db_path.exists():
        sqlite3.connect(runner.db_path).close()
    
    print("🔄 Running migrations...")
    runner.migrate()
    print("✅ Migration complete!")


if __name__ == "__main__":
    run_migrations()
