import { useState, useEffect, useCallback } from "react";
import { WatchlistItem } from "../api";
import { apiClient } from "./ApiClient";

const PAGE_SIZE = 5;

type UseWatchlistReturn = {
  items: WatchlistItem[];
  page: number;
  totalPages: number;
  loading: boolean;
  error: Error | null;
  filter: "all" | "unwatched" | "watched";
  setPage: (page: number) => void;
  setFilter: (filter: "all" | "unwatched" | "watched") => void;
  markWatched: (item: WatchlistItem) => Promise<void>;
};

export function useWatchlist(): UseWatchlistReturn {
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<"all" | "unwatched" | "watched">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadWatchlist = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.fetchWatchlist(page, PAGE_SIZE);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Failed to load watchlist"));
    } finally {
      setLoading(false);
    }
  }, [page]);

  useEffect(() => {
    loadWatchlist();
  }, [loadWatchlist]);

  const markWatched = useCallback(
    async (item: WatchlistItem) => {
      await apiClient.markWatched(item.watchlist_id, !item.is_watched);
      // Reload the watchlist after marking watched
      await loadWatchlist();
    },
    [loadWatchlist]
  );

  // Filter visible items
  const visibleItems = items.filter((i) => {
    if (filter === "watched") return i.is_watched === true;
    if (filter === "unwatched") return i.is_watched === false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return {
    items: visibleItems,
    page,
    totalPages,
    loading,
    error,
    filter,
    setPage,
    setFilter,
    markWatched,
  };
}
