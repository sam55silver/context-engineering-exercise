import { useState, useEffect } from "react";
import { WatchlistItem } from "../api";
import { apiClient } from "./ApiClient";

type UseRecentlyWatchedReturn = {
  items: WatchlistItem[];
  loading: boolean;
  error: Error | null;
};

export function useRecentlyWatched(): UseRecentlyWatchedReturn {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    apiClient
      .fetchRecent()
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err : new Error("Failed to load recently watched")))
      .finally(() => setLoading(false));
  }, []);

  return { items, loading, error };
}
