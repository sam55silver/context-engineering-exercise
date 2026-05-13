import sqlite3
from pathlib import Path
from seed_data import SEED_TITLES

DB_PATH = Path(__file__).parent / "watchlist.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
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

    cur.execute("SELECT COUNT(*) FROM titles")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO titles (title, kind, release_year, genre) VALUES (:title, :kind, :release_year, :genre)",
            SEED_TITLES,
        )
        # Pre-populate the watchlist with the first 8 titles so users see data immediately.
        cur.execute("SELECT id FROM titles ORDER BY id LIMIT 8")
        ids = [row["id"] for row in cur.fetchall()]
        cur.executemany(
            "INSERT INTO watchlist (title_id) VALUES (?)",
            [(tid,) for tid in ids],
        )

    conn.commit()
    conn.close()
