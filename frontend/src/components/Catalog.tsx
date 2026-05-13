import { useState } from "react";
import { useCatalog } from "../hooks/useCatalog";
import { TitleCard } from "./TitleCard";

export function Catalog() {
  const { titles, loading, error, addToWatchlist } = useCatalog();
  const [adding, setAdding] = useState<number | null>(null);

  async function handleAdd(id: number) {
    setAdding(id);
    try {
      await addToWatchlist(id);
    } finally {
      setAdding(null);
    }
  }

  if (loading) {
    return <div className="empty">Loading catalog…</div>;
  }

  if (error) {
    return <div className="empty">Error loading catalog: {error.message}</div>;
  }

  if (titles.length === 0) {
    return <div className="empty">No titles available.</div>;
  }

  return (
    <div className="grid">
      {titles.map((t) => (
        <TitleCard
          key={t.id}
          item={t}
          action={
            <button
              className="primary"
              disabled={adding === t.id}
              onClick={() => handleAdd(t.id)}
            >
              {adding === t.id ? "Adding…" : "+ Watchlist"}
            </button>
          }
        />
      ))}
    </div>
  );
}
