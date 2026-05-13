export type Title = {
  id: number;
  title: string;
  kind: "show" | "movie";
  releaseYear: number;
  genre: string;
};

export type WatchlistItem = {
  watchlist_id: number;
  title_id: number;
  title: string;
  kind: "show" | "movie";
  releaseYear: number;
  genre: string;
  isWatched: boolean;
  added_at: string;
  watched_at: string | null;
};

export type WatchlistPage = {
  items: WatchlistItem[];
  page: number;
  size: number;
  total: number;
};

type ApiTitle = {
  id: number;
  title: string;
  kind: "show" | "movie";
  release_year: number;
  genre: string;
};

type ApiWatchlistItem = {
  watchlist_id: number;
  title_id: number;
  title: string;
  kind: "show" | "movie";
  release_year: number;
  genre: string;
  is_watched: 0 | 1;
  added_at: string;
  watched_at: string | null;
};

type ApiWatchlistPage = {
  items: ApiWatchlistItem[];
  page: number;
  size: number;
  total: number;
};

async function buildHttpError(res: Response, context: string): Promise<Error> {
  let details = "";
  try {
    const body = await res.json();
    if (body && typeof body === "object") {
      const message =
        "message" in body && typeof body.message === "string"
          ? body.message
          : "detail" in body && typeof body.detail === "string"
            ? body.detail
            : null;
      if (message) {
        details = `: ${message}`;
      }
    }
  } catch {
    // Ignore non-JSON error bodies.
  }

  return new Error(`${context} failed (${res.status} ${res.statusText})${details}`);
}

function mapTitle(title: ApiTitle): Title {
  return {
    id: title.id,
    title: title.title,
    kind: title.kind,
    releaseYear: title.release_year,
    genre: title.genre,
  };
}

function mapWatchlistItem(item: ApiWatchlistItem): WatchlistItem {
  return {
    watchlist_id: item.watchlist_id,
    title_id: item.title_id,
    title: item.title,
    kind: item.kind,
    releaseYear: item.release_year,
    genre: item.genre,
    isWatched: item.is_watched === 1,
    added_at: item.added_at,
    watched_at: item.watched_at,
  };
}

export async function fetchCatalog(): Promise<Title[]> {
  const res = await fetch("/api/catalog");
  if (!res.ok) {
    throw await buildHttpError(res, "Fetching catalog");
  }
  const data: ApiTitle[] = await res.json();
  return data.map(mapTitle);
}

export async function fetchWatchlist(page: number, size = 5): Promise<WatchlistPage> {
  const res = await fetch(`/api/watchlist?page=${page}&size=${size}`);
  if (!res.ok) {
    throw await buildHttpError(res, "Fetching watchlist");
  }
  const data: ApiWatchlistPage = await res.json();
  return {
    ...data,
    items: data.items.map(mapWatchlistItem),
  };
}

export async function addToWatchlist(titleId: number): Promise<void> {
  const res = await fetch("/api/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title_id: titleId }),
  });
  if (!res.ok) {
    throw await buildHttpError(res, "Adding title to watchlist");
  }
}

export async function markWatched(watchlistId: number, isWatched: boolean): Promise<void> {
  const res = await fetch(`/api/watchlist/${watchlistId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_watched: isWatched }),
  });
  if (!res.ok) {
    throw await buildHttpError(res, "Updating watched status");
  }
}

export async function fetchRecent(): Promise<WatchlistItem[]> {
  const res = await fetch("/api/watchlist/recent");
  if (!res.ok) {
    throw await buildHttpError(res, "Fetching recently watched titles");
  }
  const data: ApiWatchlistItem[] = await res.json();
  return data.map(mapWatchlistItem);
}
