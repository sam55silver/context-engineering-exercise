import { useEffect, useState } from "react";
import { fetchRecent, type WatchlistItem } from "../api";
import { TitleCard } from "./TitleCard";

export function RecentlyWatched() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecent()
      .then(setItems)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty">Loading…</div>;
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
