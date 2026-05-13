"""
Tests for watchlist pagination off-by-one bug.

Bug: offset = page * size  (wrong)
Fix: offset = (page - 1) * size
"""
import sqlite3
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Redirect DB to a fresh temp file BEFORE importing app/db
import db as db_module

_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
db_module.DB_PATH = Path(_tmp.name)

from main import app  # noqa: E402 — must come after patching DB_PATH


def _reset_and_seed(n: int = 15) -> list[int]:
    """Drop all data, reset autoincrement, insert n titles + n watchlist rows."""
    conn = sqlite3.connect(str(db_module.DB_PATH))
    # Wipe rows and reset AUTOINCREMENT counters
    conn.executescript(
        """
        DELETE FROM watchlist;
        DELETE FROM titles;
        DELETE FROM sqlite_sequence WHERE name='watchlist';
        DELETE FROM sqlite_sequence WHERE name='titles';
        """
    )
    conn.executemany(
        "INSERT INTO titles (title, kind, release_year, genre) VALUES (?,?,?,?)",
        [(f"Title {i}", "movie", 2000, "drama") for i in range(1, n + 1)],
    )
    title_ids = [r[0] for r in conn.execute("SELECT id FROM titles ORDER BY id").fetchall()]
    conn.executemany("INSERT INTO watchlist (title_id) VALUES (?)", [(tid,) for tid in title_ids])
    conn.commit()
    watchlist_ids = [r[0] for r in conn.execute("SELECT id FROM watchlist ORDER BY id").fetchall()]
    conn.close()
    return watchlist_ids


@pytest.fixture(autouse=True)
def setup_db():
    db_module.init_db()  # ensure schema exists
    _reset_and_seed(15)
    yield


client = TestClient(app)


def test_page1_returns_first_5_items():
    """Page 1 should return the first 5 watchlist rows (lowest IDs)."""
    resp = client.get("/api/watchlist?page=1&size=5")
    assert resp.status_code == 200
    data = resp.json()
    items = data["items"]
    assert len(items) == 5, f"Expected 5 items on page 1, got {len(items)}"

    # After a clean reset the IDs are 1-5
    ids = [item["watchlist_id"] for item in items]
    assert ids == [1, 2, 3, 4, 5], (
        f"Page 1 should contain watchlist_ids 1-5, got {ids}. "
        "This indicates the off-by-one pagination bug is present."
    )


def test_page2_returns_items_6_to_10():
    """Page 2 should return watchlist rows 6-10."""
    resp = client.get("/api/watchlist?page=2&size=5")
    assert resp.status_code == 200
    data = resp.json()
    items = data["items"]
    assert len(items) == 5, f"Expected 5 items on page 2, got {len(items)}"

    ids = [item["watchlist_id"] for item in items]
    assert ids == [6, 7, 8, 9, 10], (
        f"Page 2 should contain watchlist_ids 6-10, got {ids}."
    )
