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
  is_watched: boolean;
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
  return res.json();
}

export async function fetchWatchlist(page: number, size = 5): Promise<WatchlistPage> {
  const res = await fetch(`/api/watchlist?page=${page}&size=${size}`);
  return res.json();
}

export async function addToWatchlist(titleId: number): Promise<void> {
  await fetch("/api/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title_id: titleId }),
  });
}

export async function markWatched(watchlistId: number, isWatched: boolean): Promise<void> {
  await fetch(`/api/watchlist/${watchlistId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_watched: isWatched }),
  });
}

export async function fetchRecent(): Promise<WatchlistItem[]> {
  const res = await fetch("/api/watchlist/recent");
  return res.json();
}
