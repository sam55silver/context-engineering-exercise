"""Watchlist repository - handles all watchlist-related database queries."""

import sqlite3
from datetime import datetime
from db import get_conn


class WatchlistRepository:
    """Repository for watchlist database operations."""

    @staticmethod
    def get_watchlist_page(page: int, size: int) -> tuple[list[dict], int]:
        """
        Retrieve a page of watchlist items with pagination.

        Args:
            page: Page number (1-indexed)
            size: Number of items per page

        Returns:
            Tuple of (list of watchlist items, total count)
        """
        conn = get_conn()
        try:
            offset = (page - 1) * size
            rows = conn.execute(
                """
                SELECT w.id as watchlist_id, w.is_watched, w.added_at, w.watched_at,
                       t.id as title_id, t.title, t.kind, t.release_year, t.genre
                FROM watchlist w
                JOIN titles t ON t.id = w.title_id
                ORDER BY w.id
                LIMIT ? OFFSET ?
                """,
                (size, offset),
            ).fetchall()
            
            total = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
            
            items = [dict(r) for r in rows]
            return items, total
        finally:
            conn.close()

    @staticmethod
    def add_title_to_watchlist(title_id: int) -> None:
        """
        Add a title to the watchlist.

        Args:
            title_id: The ID of the title to add

        Raises:
            sqlite3.IntegrityError: If title_id is invalid or already in watchlist
        """
        conn = get_conn()
        try:
            conn.execute("INSERT INTO watchlist (title_id) VALUES (?)", (title_id,))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def mark_as_watched(watchlist_id: int, is_watched: bool) -> None:
        """
        Mark a watchlist item as watched or unwatched.

        Args:
            watchlist_id: The ID of the watchlist item
            is_watched: Whether the item is watched
        """
        conn = get_conn()
        try:
            watched_at = datetime.utcnow().isoformat() if is_watched else None
            conn.execute(
                "UPDATE watchlist SET is_watched = ?, watched_at = ? WHERE id = ?",
                (1 if is_watched else 0, watched_at, watchlist_id),
            )
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def get_recently_watched(limit_date: str) -> list[dict]:
        """
        Retrieve items watched on or after a specific date.

        Args:
            limit_date: ISO format date string (e.g., '2024-01-15')

        Returns:
            List of recently watched watchlist items
        """
        conn = get_conn()
        try:
            rows = conn.execute(
                """
                SELECT w.id as watchlist_id, w.is_watched, w.watched_at,
                       t.id as title_id, t.title, t.kind, t.release_year, t.genre
                FROM watchlist w
                JOIN titles t ON t.id = w.title_id
                WHERE w.is_watched = 1 AND DATE(w.watched_at) = ?
                ORDER BY w.watched_at DESC
                """,
                (limit_date,),
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
