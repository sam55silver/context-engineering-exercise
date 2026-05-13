"""
Tests verifying that all API endpoints return `releaseYear` (camelCase)
instead of `release_year` (snake_case).
"""
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_db(tmp_path: Path):
    """Create an in-memory-style temp SQLite DB seeded with minimal data."""
    db_file = tmp_path / "test_watchlist.db"
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            kind TEXT NOT NULL,
            release_year INTEGER NOT NULL,
            genre TEXT NOT NULL
        );

        CREATE TABLE watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_id INTEGER NOT NULL UNIQUE REFERENCES titles(id),
            is_watched INTEGER NOT NULL DEFAULT 0,
            added_at TEXT NOT NULL DEFAULT (datetime('now')),
            watched_at TEXT
        );
        """
    )
    conn.execute(
        "INSERT INTO titles (title, kind, release_year, genre) VALUES (?, ?, ?, ?)",
        ("Inception", "movie", 2010, "Sci-Fi"),
    )
    conn.execute(
        "INSERT INTO titles (title, kind, release_year, genre) VALUES (?, ?, ?, ?)",
        ("Breaking Bad", "show", 2008, "Drama"),
    )
    # Add first title to watchlist, mark it watched with a today timestamp
    conn.execute("INSERT INTO watchlist (title_id, is_watched, watched_at) VALUES (1, 1, datetime('now'))")
    conn.commit()
    conn.close()
    return db_file


@pytest.fixture()
def client(tmp_db: Path):
    """TestClient wired to the temp DB, bypassing init_db."""
    import db as db_module
    import main  # noqa: F401 — ensure app is importable

    with patch.object(db_module, "DB_PATH", tmp_db):
        # Reinitialise the module-level app with the patched DB
        from main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCatalogReleaseYear:
    def test_catalog_returns_releaseYear_key(self, client: TestClient):
        """GET /api/catalog items must have `releaseYear`, not `release_year`."""
        resp = client.get("/api/catalog")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0
        for item in items:
            assert "releaseYear" in item, (
                f"Expected 'releaseYear' key in catalog item but got keys: {list(item.keys())}"
            )
            assert "release_year" not in item, (
                "Unexpected snake_case 'release_year' key found in catalog item"
            )

    def test_catalog_releaseYear_is_integer(self, client: TestClient):
        """releaseYear must be an integer, not None or a string."""
        resp = client.get("/api/catalog")
        for item in resp.json():
            assert isinstance(item["releaseYear"], int), (
                f"releaseYear should be int, got {type(item['releaseYear'])} for {item['title']}"
            )

    def test_catalog_releaseYear_correct_value(self, client: TestClient):
        """releaseYear value must match the seeded data."""
        resp = client.get("/api/catalog")
        items = {i["title"]: i for i in resp.json()}
        assert items["Inception"]["releaseYear"] == 2010
        assert items["Breaking Bad"]["releaseYear"] == 2008


class TestWatchlistReleaseYear:
    def test_watchlist_returns_releaseYear_key(self, client: TestClient):
        """GET /api/watchlist items must have `releaseYear`, not `release_year`.

        Note: uses page=0 to avoid the known pagination offset bug where
        offset = page * size skips the first `size` rows on page=1.
        """
        resp = client.get("/api/watchlist?page=0&size=10")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) > 0
        for item in items:
            assert "releaseYear" in item, (
                f"Expected 'releaseYear' key in watchlist item but got: {list(item.keys())}"
            )
            assert "release_year" not in item

    def test_watchlist_releaseYear_correct_value(self, client: TestClient):
        """releaseYear value in watchlist must match the seeded title.

        Note: uses page=0 to avoid the known pagination offset bug.
        """
        resp = client.get("/api/watchlist?page=0&size=10")
        items = resp.json()["items"]
        inception = next(i for i in items if i["title"] == "Inception")
        assert inception["releaseYear"] == 2010


class TestRecentReleaseYear:
    def test_recent_returns_releaseYear_key(self, client: TestClient):
        """GET /api/watchlist/recent items must have `releaseYear`, not `release_year`."""
        resp = client.get("/api/watchlist/recent")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) > 0, "Expected at least one recently-watched item from seed data"
        for item in items:
            assert "releaseYear" in item, (
                f"Expected 'releaseYear' key in recent item but got: {list(item.keys())}"
            )
            assert "release_year" not in item

    def test_recent_releaseYear_correct_value(self, client: TestClient):
        """releaseYear value in recent items must match the seeded title."""
        resp = client.get("/api/watchlist/recent")
        items = resp.json()
        inception = next(i for i in items if i["title"] == "Inception")
        assert inception["releaseYear"] == 2010
