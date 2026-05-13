import { useWatchlist } from "../hooks/useWatchlist";
import { TitleCard } from "./TitleCard";

export function Watchlist() {
  const {
    items,
    page,
    totalPages,
    loading,
    error,
    filter,
    setPage,
    setFilter,
    markWatched,
  } = useWatchlist();

  if (error) {
    return <div className="empty">Error loading watchlist: {error.message}</div>;
  }

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
        <div className="empty">Loading watchlist…</div>
      ) : items.length === 0 ? (
        <div className="empty">Nothing here.</div>
      ) : (
        <div className="grid">
          {items.map((item) => (
            <TitleCard
              key={item.watchlist_id}
              item={item}
              watched={!!item.is_watched}
              action={
                <button className="secondary" onClick={() => markWatched(item)}>
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
          onClick={() => setPage(page - 1)}
        >
          ← Prev
        </button>
        <span className="meta">
          Page {page} of {totalPages}
        </span>
        <button
          className="secondary"
          disabled={page >= totalPages}
          onClick={() => setPage(page + 1)}
        >
          Next →
        </button>
      </div>
    </>
  );
}
