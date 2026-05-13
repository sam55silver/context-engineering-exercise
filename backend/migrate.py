"""Migration runner that tracks and applies database schema changes."""

import importlib
import json
import sqlite3
from pathlib import Path
from typing import Optional


def _load_migrations() -> list:
    """Load all migration classes dynamically."""
    migrations = []
    
    # Import 001_create_tables
    mod = importlib.import_module("migrations._001_create_tables")
    migrations.append(mod.CreateTables())
    
    return migrations


# List of all migrations in order
MIGRATIONS = _load_migrations()

DB_PATH = Path(__file__).parent / "watchlist.db"
MIGRATIONS_LOG = Path(__file__).parent / ".migrations.json"


class MigrationRunner:
    """Manages migration tracking and execution."""
    
    def __init__(self, db_path: Path = DB_PATH, log_path: Path = MIGRATIONS_LOG):
        self.db_path = db_path
        self.log_path = log_path
    
    def _load_migration_log(self) -> dict:
        """Load the migration log from file."""
        if self.log_path.exists():
            with open(self.log_path, "r") as f:
                return json.load(f)
        return {"applied": []}
    
    def _save_migration_log(self, log: dict) -> None:
        """Save the migration log to file."""
        with open(self.log_path, "w") as f:
            json.dump(log, f, indent=2)
    
    def get_applied_migrations(self) -> list[str]:
        """Get list of migration names that have been applied."""
        log = self._load_migration_log()
        return log.get("applied", [])
    
    def get_pending_migrations(self) -> list:
        """Get list of migration objects that haven't been applied."""
        applied = self.get_applied_migrations()
        return [m for m in MIGRATIONS if m.name not in applied]
    
    def apply_migration(self, migration, conn: sqlite3.Connection) -> None:
        """Apply a single migration."""
        migration.up(conn)
        
        # Update log
        log = self._load_migration_log()
        if migration.name not in log["applied"]:
            log["applied"].append(migration.name)
        self._save_migration_log(log)
        
        print(f"Applied migration: {migration.name}")
    
    def revert_migration(self, migration, conn: sqlite3.Connection) -> None:
        """Revert a single migration."""
        migration.down(conn)
        
        # Update log
        log = self._load_migration_log()
        if migration.name in log["applied"]:
            log["applied"].remove(migration.name)
        self._save_migration_log(log)
        
        print(f"Reverted migration: {migration.name}")
    
    def migrate(self, target: Optional[str] = None) -> None:
        """Apply all pending migrations up to an optional target migration.
        
        Args:
            target: Optional migration name to apply up to (inclusive).
                   If None, applies all pending migrations.
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        try:
            pending = self.get_pending_migrations()
            
            if not pending:
                print("No pending migrations")
                return
            
            for migration in pending:
                self.apply_migration(migration, conn)
                if target and migration.name == target:
                    break
            
            print(f"Migration complete. Applied {len(pending)} migration(s)")
        finally:
            conn.close()
    
    def rollback(self, steps: int = 1) -> None:
        """Rollback the last N migrations.
        
        Args:
            steps: Number of migrations to rollback (default: 1)
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        try:
            applied = self.get_applied_migrations()
            
            if not applied:
                print("No migrations to rollback")
                return
            
            # Migrations are reverted in reverse order
            migrations_by_name = {m.name: m for m in MIGRATIONS}
            reverted = 0
            
            for migration_name in reversed(applied):
                if reverted >= steps:
                    break
                
                migration = migrations_by_name.get(migration_name)
                if migration:
                    self.revert_migration(migration, conn)
                    reverted += 1
        finally:
            conn.close()


def get_runner() -> MigrationRunner:
    """Get a migration runner instance."""
    return MigrationRunner()
