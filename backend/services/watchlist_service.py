"""Watchlist service - business logic for watchlist operations."""

import sqlite3
from datetime import datetime

from repositories.watchlist_repository import WatchlistRepository
from repositories.title_repository import TitleRepository
from models.schemas import (
    WatchlistItemResponse,
    WatchlistPageResponse,
)


class WatchlistService:
    """Service for watchlist business logic."""

    @staticmethod
    def get_watchlist_page(page: int, size: int) -> WatchlistPageResponse:
        """
        Get a paginated view of the watchlist.

        Args:
            page: Page number (1-indexed)
            size: Items per page

        Returns:
            WatchlistPageResponse with items and pagination info

        Raises:
            ValueError: If page or size are invalid
        """
        if page < 1 or size < 1:
            raise ValueError("Page and size must be greater than 0")

        items, total = WatchlistRepository.get_watchlist_page(page, size)
        
        # Convert to response models
        watchlist_items = [
            WatchlistItemResponse(
                watchlist_id=item["watchlist_id"],
                title_id=item["title_id"],
                title=item["title"],
                kind=item["kind"],
                release_year=item["release_year"],
                genre=item["genre"],
                is_watched=bool(item["is_watched"]),
                added_at=item["added_at"],
                watched_at=item["watched_at"],
            )
            for item in items
        ]
        
        return WatchlistPageResponse(
            items=watchlist_items,
            page=page,
            size=size,
            total=total,
        )

    @staticmethod
    def add_to_watchlist(title_id: int) -> None:
        """
        Add a title to the watchlist.

        Args:
            title_id: The ID of the title to add

        Raises:
            ValueError: If title_id is invalid
            sqlite3.IntegrityError: If title is already in watchlist
        """
        # Validate that the title exists
        title = TitleRepository.get_title_by_id(title_id)
        if not title:
            raise ValueError(f"Title with ID {title_id} not found")

        # Add to watchlist
        WatchlistRepository.add_title_to_watchlist(title_id)

    @staticmethod
    def mark_as_watched(watchlist_id: int, is_watched: bool) -> None:
        """
        Mark a watchlist item as watched or unwatched.

        Args:
            watchlist_id: The ID of the watchlist item
            is_watched: Whether the item is watched
        """
        WatchlistRepository.mark_as_watched(watchlist_id, is_watched)

    @staticmethod
    def get_recently_watched() -> list[WatchlistItemResponse]:
        """
        Get items watched today.

        Returns:
            List of recently watched items
        """
        today = datetime.utcnow().date().isoformat()
        items = WatchlistRepository.get_recently_watched(today)
        
        # Convert to response models
        return [
            WatchlistItemResponse(
                watchlist_id=item["watchlist_id"],
                title_id=item["title_id"],
                title=item["title"],
                kind=item["kind"],
                release_year=item["release_year"],
                genre=item["genre"],
                is_watched=bool(item["is_watched"]),
                added_at=item.get("added_at", ""),  # May not be in recent query
                watched_at=item["watched_at"],
            )
            for item in items
        ]
