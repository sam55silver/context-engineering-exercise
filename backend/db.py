"""Database connection management.

Schema migrations and data seeding are now handled separately:
- Schema changes: Use backend/migrate.py and backend/migrations/
- Data seeding: Use backend/seed.py and backend/seeds/
- Database setup: Call migrate() and seed() during app initialization
"""

import sqlite3
from pathlib import Path

from migrate import get_runner
from seed import get_seeder

DB_PATH = Path(__file__).parent / "watchlist.db"


def get_conn() -> sqlite3.Connection:
    """Get a database connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the database.
    
    This function:
    1. Creates the database file if it doesn't exist
    2. Applies all pending migrations
    3. Seeds initial data if not already seeded
    
    Called automatically during app startup via lifespan.
    """
    # Ensure database file exists (create it if needed)
    if not DB_PATH.exists():
        sqlite3.connect(DB_PATH).close()
    
    # Apply migrations
    runner = get_runner()
    pending = runner.get_pending_migrations()
    if pending:
        print(f"Applying {len(pending)} pending migration(s)...")
        runner.migrate()
    
    # Seed data
    seeder = get_seeder()
    seeder.seed()
