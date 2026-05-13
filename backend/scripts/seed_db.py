#!/usr/bin/env python
"""Seed data into an existing database."""

import sqlite3
import sys
from pathlib import Path

# Add backend to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from seed import get_seeder


def seed_db():
    """Seed data into the database."""
    seeder = get_seeder()
    
    # Create database file if it doesn't exist
    if not seeder.db_path.exists():
        sqlite3.connect(seeder.db_path).close()
    
    print("🌱 Seeding database...")
    seeder.seed()
    print("✅ Seeding complete!")


if __name__ == "__main__":
    seed_db()
