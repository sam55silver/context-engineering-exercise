from datetime import datetime, timezone
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


@app.get("/api/catalog")
def get_catalog():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM titles ORDER BY id").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.get("/api/watchlist")
def get_watchlist(page: int = 1, size: int = 5):
    conn = get_conn()
    try:
        offset = (page - 1) * size  # fix: was `page * size` (off-by-one)
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
        return {
            "items": [dict(r) for r in rows],
            "page": page,
            "size": size,
            "total": total,
        }
    finally:
        conn.close()


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


# fix: /recent must be declared before /{watchlist_id} to avoid route shadowing
@app.get("/api/watchlist/recent")
def get_recent():
    """Items watched today."""
    today = datetime.now(timezone.utc).date().isoformat()
    conn = get_conn()
    try:
        rows = conn.execute(
            """
            SELECT w.id as watchlist_id, w.is_watched, w.added_at, w.watched_at,
                   t.id as title_id, t.title, t.kind, t.release_year, t.genre
            FROM watchlist w
            JOIN titles t ON t.id = w.title_id
            WHERE w.is_watched = 1 AND DATE(w.watched_at) = ?
            ORDER BY w.watched_at DESC
            """,
            (today,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@app.patch("/api/watchlist/{watchlist_id}")
def mark_watched(watchlist_id: int, body: WatchUpdate):
    conn = get_conn()
    try:
        watched_at = datetime.now(timezone.utc).isoformat() if body.is_watched else None
        cur = conn.execute(
            "UPDATE watchlist SET is_watched = ?, watched_at = ? WHERE id = ?",
            (1 if body.is_watched else 0, watched_at, watchlist_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        conn.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
    return {"ok": True}
