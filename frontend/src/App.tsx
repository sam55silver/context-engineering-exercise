import { useState } from "react";
import { Catalog } from "./components/Catalog";
import { Watchlist } from "./components/Watchlist";
import { RecentlyWatched } from "./components/RecentlyWatched";

type Tab = "watchlist" | "catalog" | "recent";

export function App() {
  const [tab, setTab] = useState<Tab>("watchlist");

  return (
    <div className="app">
      <h1>🎬 Watchlist</h1>
      <div className="tabs">
        <button className={tab === "watchlist" ? "active" : ""} onClick={() => setTab("watchlist")}>
          My Watchlist
        </button>
        <button className={tab === "catalog" ? "active" : ""} onClick={() => setTab("catalog")}>
          Browse Catalog
        </button>
        <button className={tab === "recent" ? "active" : ""} onClick={() => setTab("recent")}>
          Watched Today
        </button>
      </div>
      {tab === "watchlist" && <Watchlist />}
      {tab === "catalog" && <Catalog />}
      {tab === "recent" && <RecentlyWatched />}
    </div>
  );
}
