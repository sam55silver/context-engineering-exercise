#!/usr/bin/env python
"""Reset the database completely - drops all tables and migrations."""

import sqlite3
import sys
from pathlib import Path

# Add backend to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from migrate import get_runner
from seed import get_seeder


def reset_db():
    """Reset database by:
    1. Creating the database file if needed
    2. Rolling back all migrations
    3. Removing migration log
    4. Re-running migrations
    5. Re-seeding data
    """
    runner = get_runner()
    seeder = get_seeder()
    
    print("🔄 Resetting database...")
    
    # Create database file if it doesn't exist
    if not runner.db_path.exists():
        sqlite3.connect(runner.db_path).close()
        print("Created database file")
    
    # Rollback all migrations
    applied = runner.get_applied_migrations()
    if applied:
        print(f"Rolling back {len(applied)} migration(s)...")
        runner.rollback(steps=len(applied))
    
    # Remove migration log
    if runner.log_path.exists():
        runner.log_path.unlink()
        print("Cleared migration log")
    
    # Re-run migrations
    print("Applying migrations...")
    runner.migrate()
    
    # Re-seed data
    print("Seeding data...")
    seeder.seed()
    
    print("✅ Database reset complete!")


if __name__ == "__main__":
    reset_db()
