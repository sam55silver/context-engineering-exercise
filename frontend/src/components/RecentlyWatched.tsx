import { useRecentlyWatched } from "../hooks/useRecentlyWatched";
import { TitleCard } from "./TitleCard";

export function RecentlyWatched() {
  const { items, loading, error } = useRecentlyWatched();

  if (error) {
    return <div className="empty">Error loading recently watched: {error.message}</div>;
  }

  if (loading) {
    return <div className="empty">Loading recently watched…</div>;
  }

  if (items.length === 0) {
    return <div className="empty">Nothing watched today yet.</div>;
  }

  return (
    <div className="grid">
      {items.map((item) => (
        <TitleCard key={item.watchlist_id} item={item} watched />
      ))}
    </div>
  );
}
