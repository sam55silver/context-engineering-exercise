"""Database migrations system for schema versioning and changes."""

import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path


class Migration(ABC):
    """Base class for all migrations.
    
    Each migration must have a unique name and implement up() and down() methods.
    """
    
    name: str
    
    @abstractmethod
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply the migration."""
        pass
    
    @abstractmethod
    def down(self, conn: sqlite3.Connection) -> None:
        """Revert the migration."""
        pass
