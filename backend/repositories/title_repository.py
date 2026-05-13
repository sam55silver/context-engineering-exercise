"""Title repository - handles all title-related database queries."""

import sqlite3
from db import get_conn


class TitleRepository:
    """Repository for title database operations."""

    @staticmethod
    def get_all_titles() -> list[dict]:
        """
        Retrieve all titles from the catalog.

        Returns:
            List of title dictionaries with keys: id, title, kind, release_year, genre
        """
        conn = get_conn()
        try:
            rows = conn.execute("SELECT * FROM titles ORDER BY id").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_title_by_id(title_id: int) -> dict | None:
        """
        Retrieve a single title by ID.

        Args:
            title_id: The ID of the title to retrieve

        Returns:
            Title dictionary or None if not found
        """
        conn = get_conn()
        try:
            row = conn.execute("SELECT * FROM titles WHERE id = ?", (title_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
