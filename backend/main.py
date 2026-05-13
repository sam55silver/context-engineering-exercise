from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import get_conn, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class WatchUpdate(BaseModel):
    is_watched: bool


class AddToWatchlist(BaseModel):
    title_id: int


def _normalize_release_year(row: dict) -> dict:
    release_year = row.pop("release_year", None)
    if release_year is not None:
        row["releaseYear"] = release_year
    return row


@app.get("/api/catalog")
def get_catalog():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, title, kind, release_year as releaseYear, genre FROM titles ORDER BY id"
    ).fetchall()
    conn.close()
    return [_normalize_release_year(dict(r)) for r in rows]


@app.get("/api/watchlist")
def get_watchlist(page: int = 1, size: int = 5):
    if page < 1:
        raise HTTPException(status_code=422, detail="page must be >= 1")
    if size < 1 or size > 100:
        raise HTTPException(status_code=422, detail="size must be between 1 and 100")

    conn = get_conn()
    offset = (page - 1) * size
    rows = conn.execute(
        """
        SELECT w.id as watchlist_id, w.is_watched, w.added_at, w.watched_at,
               t.id as title_id, t.title, t.kind, t.release_year as releaseYear, t.genre
        FROM watchlist w
        JOIN titles t ON t.id = w.title_id
        ORDER BY w.id
        LIMIT ? OFFSET ?
        """,
        (size, offset),
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    conn.close()
    return {
        "items": [_normalize_release_year(dict(r)) for r in rows],
        "page": page,
        "size": size,
        "total": total,
    }


@app.post("/api/watchlist")
def add_to_watchlist(body: AddToWatchlist):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO watchlist (title_id) VALUES (?)", (body.title_id,))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return {"ok": True}


@app.get("/api/watchlist/recent")
def get_recent():
    """Items watched today."""
    today = datetime.utcnow().date().isoformat()
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT w.id as watchlist_id, w.is_watched, w.watched_at,
               t.id as title_id, t.title, t.kind, t.release_year as releaseYear, t.genre
        FROM watchlist w
        JOIN titles t ON t.id = w.title_id
        WHERE w.is_watched = 1 AND DATE(w.watched_at) = ?
        ORDER BY w.watched_at DESC
        """,
        (today,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.patch("/api/watchlist/{watchlist_id}")
def mark_watched(watchlist_id: int, body: WatchUpdate):
    conn = get_conn()
    watched_at = datetime.utcnow().isoformat() if body.is_watched else None
    result = conn.execute(
        "UPDATE watchlist SET is_watched = ?, watched_at = ? WHERE id = ?",
        (1 if body.is_watched else 0, watched_at, watchlist_id),
    )
    if result.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="watchlist item not found")
    conn.commit()
    conn.close()
    return {"ok": True}
