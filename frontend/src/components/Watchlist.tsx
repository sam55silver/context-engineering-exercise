import { useEffect, useState } from "react";
import { fetchWatchlist, markWatched, type WatchlistItem } from "../api";
import { TitleCard } from "./TitleCard";
import { SkeletonGrid } from "./SkeletonGrid";

export function Watchlist() {
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState<"all" | "unwatched" | "watched">("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [toggling, setToggling] = useState<number | null>(null);
  const size = 5;

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchWatchlist(page, size);
      setItems(data.items);
      setTotal(data.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load watchlist.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, [page]);

  async function toggle(item: WatchlistItem) {
    setToggling(item.watchlist_id);
    try {
      await markWatched(item.watchlist_id, !item.is_watched);
      await load();
    } catch {
      // re-enable on error
    } finally {
      setToggling(null);
    }
  }

  const visible = items.filter((i) => {
    if (filter === "watched") return i.is_watched === true;
    if (filter === "unwatched") return i.is_watched === false;
    return true;
  });

  const totalPages = Math.max(1, Math.ceil(total / size));

  return (
    <>
      <div className="tabs" style={{ marginBottom: 14 }}>
        <button className={filter === "all" ? "active" : ""} onClick={() => setFilter("all")}>
          All
        </button>
        <button className={filter === "unwatched" ? "active" : ""} onClick={() => setFilter("unwatched")}>
          Unwatched
        </button>
        <button className={filter === "watched" ? "active" : ""} onClick={() => setFilter("watched")}>
          Watched
        </button>
      </div>

      {loading ? (
        <SkeletonGrid />
      ) : error ? (
        <div className="error-state">
          <p className="error-message">⚠ {error}</p>
          <button className="primary" onClick={load}>Retry</button>
        </div>
      ) : visible.length === 0 ? (
        <div className="empty">Nothing here.</div>
      ) : (
        <div className="grid">
          {visible.map((item) => (
            <TitleCard
              key={item.watchlist_id}
              item={item}
              watched={!!item.is_watched}
              action={
                <button
                  className="secondary"
                  disabled={toggling !== null}
                  onClick={() => toggle(item)}
                >
                  {toggling === item.watchlist_id
                    ? "Saving…"
                    : item.is_watched
                    ? "↺ Unwatch"
                    : "✓ Mark watched"}
                </button>
              }
            />
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          className="secondary"
          disabled={page <= 1 || loading}
          onClick={() => setPage((p) => p - 1)}
        >
          ← Prev
        </button>
        <span className="meta">
          Page {page} of {totalPages}
        </span>
        <button
          className="secondary"
          disabled={page >= totalPages || loading}
          onClick={() => setPage((p) => p + 1)}
        >
          Next →
        </button>
      </div>
    </>
  );
}
