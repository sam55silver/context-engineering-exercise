"""001 - Create tables: titles and watchlist."""

import sqlite3
from migrations import Migration


class CreateTables(Migration):
    """Create the initial titles and watchlist tables."""
    
    name = "001_create_tables"
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Create the tables."""
        cur = conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS titles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                kind TEXT NOT NULL,
                release_year INTEGER NOT NULL,
                genre TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title_id INTEGER NOT NULL UNIQUE REFERENCES titles(id),
                is_watched INTEGER NOT NULL DEFAULT 0,
                added_at TEXT NOT NULL DEFAULT (datetime('now')),
                watched_at TEXT
            );
            """
        )
        conn.commit()
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Drop the tables."""
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS watchlist")
        cur.execute("DROP TABLE IF EXISTS titles")
        conn.commit()
