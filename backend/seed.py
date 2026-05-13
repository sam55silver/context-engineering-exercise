"""Seeder runner that applies seed data to the database."""

import importlib
import sqlite3
from pathlib import Path


def _load_seeders() -> list:
    """Load all seeder classes dynamically."""
    seeders = []
    
    # Import seed_titles
    mod = importlib.import_module("seeds._seed_titles")
    seeders.append(mod.SeedTitles())
    
    return seeders


# List of all seeders
SEEDERS = _load_seeders()

DB_PATH = Path(__file__).parent / "watchlist.db"


class SeederRunner:
    """Manages seed data insertion."""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
    
    def seed(self, name: str = None) -> None:
        """Apply seed data to the database.
        
        Args:
            name: Optional seeder name to run. If None, runs all seeders.
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            seeders_to_run = SEEDERS
            
            if name:
                seeders_to_run = [s for s in SEEDERS if s.name == name]
                if not seeders_to_run:
                    raise ValueError(f"Seeder '{name}' not found")
            
            for seeder in seeders_to_run:
                seeder.seed(conn)
            
            print(f"Seeding complete")
        finally:
            conn.close()


def get_seeder() -> SeederRunner:
    """Get a seeder runner instance."""
    return SeederRunner()
