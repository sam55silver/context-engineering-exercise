"""Data Transfer Objects (DTOs) for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ===== Request Models =====


class AddToWatchlistRequest(BaseModel):
    """Request to add a title to the watchlist."""

    title_id: int


class MarkWatchedRequest(BaseModel):
    """Request to mark a watchlist item as watched/unwatched."""

    is_watched: bool


# ===== Response Models =====


class TitleResponse(BaseModel):
    """Response model for a title in the catalog."""

    id: int
    title: str
    kind: str  # 'show' or 'movie'
    release_year: int
    genre: str


class WatchlistItemResponse(BaseModel):
    """Response model for a single watchlist item."""

    watchlist_id: int
    title_id: int
    title: str
    kind: str
    release_year: int
    genre: str
    is_watched: bool
    added_at: str
    watched_at: Optional[str] = None


class WatchlistPageResponse(BaseModel):
    """Response model for paginated watchlist."""

    items: list[WatchlistItemResponse]
    page: int
    size: int
    total: int


class SuccessResponse(BaseModel):
    """Generic success response."""

    ok: bool = True
