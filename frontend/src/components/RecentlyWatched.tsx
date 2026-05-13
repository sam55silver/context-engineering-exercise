import { useEffect, useState } from "react";
import { fetchRecent, type WatchlistItem } from "../api";
import { TitleCard } from "./TitleCard";
import { SkeletonGrid } from "./SkeletonGrid";

export function RecentlyWatched() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecent();
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load recent titles.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <SkeletonGrid />;

  if (error) {
    return (
      <div className="error-state">
        <p className="error-message">⚠ {error}</p>
        <button className="primary" onClick={load}>Retry</button>
      </div>
    );
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
