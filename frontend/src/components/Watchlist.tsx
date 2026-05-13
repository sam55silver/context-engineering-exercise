import { useEffect, useState } from "react";
import { fetchWatchlist, markWatched, type WatchlistItem } from "../api";
import { TitleCard } from "./TitleCard";

export function Watchlist() {
  const [page, setPage] = useState(1);
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [totalPages, setTotalPages] = useState(1);
  const [filter, setFilter] = useState<"all" | "unwatched" | "watched">("all");
  const size = 5;

  async function load() {
    const data = await fetchWatchlist(page, size);
    setItems(data.items);
    setTotalPages(data.total_pages);
  }

  useEffect(() => {
    load();
  }, [page]);

  useEffect(() => {
    setPage(1);
  }, [filter]);

  async function toggle(item: WatchlistItem) {
    await markWatched(item.watchlist_id, !item.is_watched);
    load();
  }

  const visible = items.filter((i) => {
    if (filter === "watched") return i.is_watched === true;
    if (filter === "unwatched") return i.is_watched === false;
    return true;
  });

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

      {visible.length === 0 ? (
        <div className="empty">Nothing here.</div>
      ) : (
        <div className="grid">
          {visible.map((item) => (
            <TitleCard
              key={item.watchlist_id}
              item={item}
              watched={!!item.is_watched}
              action={
                <button className="secondary" onClick={() => toggle(item)}>
                  {item.is_watched ? "↺ Unwatch" : "✓ Mark watched"}
                </button>
              }
            />
          ))}
        </div>
      )}

      <div className="pagination">
        <button
          className="secondary"
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
        >
          ← Prev
        </button>
        <span className="meta">
          Page {page} of {totalPages}
        </span>
        <button
          className="secondary"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next →
        </button>
      </div>
    </>
  );
}
