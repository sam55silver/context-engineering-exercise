import { useEffect, useState } from "react";
import { addToWatchlist, fetchCatalog, type Title } from "../api";
import { TitleCard } from "./TitleCard";
import { SkeletonGrid } from "./SkeletonGrid";

export function Catalog() {
  const [titles, setTitles] = useState<Title[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [adding, setAdding] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCatalog();
      setTitles(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load catalog.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleAdd(id: number) {
    setAdding(id);
    try {
      await addToWatchlist(id);
    } catch {
      // button re-enables on error; user can retry
    } finally {
      setAdding(null);
    }
  }

  if (loading) return <SkeletonGrid />;

  if (error) {
    return (
      <div className="error-state">
        <p className="error-message">⚠ {error}</p>
        <button className="primary" onClick={load}>Retry</button>
      </div>
    );
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
              disabled={adding !== null}
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
