import { useEffect, useState } from "react";
import { addToWatchlist, fetchCatalog, type Title } from "../api";
import { TitleCard } from "./TitleCard";

export function Catalog() {
  const [titles, setTitles] = useState<Title[]>([]);
  const [adding, setAdding] = useState<number | null>(null);

  useEffect(() => {
    fetchCatalog().then(setTitles);
  }, []);

  async function handleAdd(id: number) {
    setAdding(id);
    try {
      await addToWatchlist(id);
    } finally {
      setAdding(null);  // fix: always re-enable button, even on error
    }
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
