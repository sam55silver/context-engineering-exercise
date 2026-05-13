"""Seed files for database initialization."""

import sqlite3
from abc import ABC, abstractmethod


class Seeder(ABC):
    """Base class for all seeders."""
    
    name: str
    
    @abstractmethod
    def seed(self, conn: sqlite3.Connection) -> None:
        """Insert seed data."""
        pass
