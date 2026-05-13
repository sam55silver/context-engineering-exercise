export type Title = {
  id: number;
  title: string;
  kind: "show" | "movie";
  release_year: number;
  genre: string;
};

export type WatchlistItem = {
  watchlist_id: number;
  title_id: number;
  title: string;
  kind: "show" | "movie";
  release_year: number;
  genre: string;
  is_watched: number; // SQLite returns 0 or 1, not a boolean
  added_at: string;
  watched_at: string | null;
};

export type WatchlistPage = {
  items: WatchlistItem[];
  page: number;
  size: number;
  total: number;
};

export async function fetchCatalog(): Promise<Title[]> {
  const res = await fetch("/api/catalog");
  if (!res.ok) throw new Error(`fetchCatalog failed: ${res.status}`);
  return res.json();
}

export async function fetchWatchlist(page: number, size = 5): Promise<WatchlistPage> {
  const res = await fetch(`/api/watchlist?page=${page}&size=${size}`);
  if (!res.ok) throw new Error(`fetchWatchlist failed: ${res.status}`);
  return res.json();
}

export async function addToWatchlist(titleId: number): Promise<void> {
  const res = await fetch("/api/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title_id: titleId }),
  });
  if (!res.ok) throw new Error(`addToWatchlist failed: ${res.status}`);
}

export async function markWatched(watchlistId: number, isWatched: boolean): Promise<void> {
  const res = await fetch(`/api/watchlist/${watchlistId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_watched: isWatched }),
  });
  if (!res.ok) throw new Error(`markWatched failed: ${res.status}`);
}

export async function fetchRecent(): Promise<WatchlistItem[]> {
  const res = await fetch("/api/watchlist/recent");
  if (!res.ok) throw new Error(`fetchRecent failed: ${res.status}`);
  return res.json();
}
