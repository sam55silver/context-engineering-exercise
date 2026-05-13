import { useEffect, useState } from "react";
import { Catalog } from "./components/Catalog";
import { Watchlist } from "./components/Watchlist";
import { RecentlyWatched } from "./components/RecentlyWatched";

type Tab = "watchlist" | "catalog" | "recent";
type Theme = "dark" | "light";

function getInitialTheme(): Theme {
  const stored = localStorage.getItem("theme");
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

export function App() {
  const [tab, setTab] = useState<Tab>("watchlist");
  const [theme, setTheme] = useState<Theme>(getInitialTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <div className="app">
      <div className="app-header">
        <h1>🎬 Watchlist</h1>
        <button
          className="theme-toggle"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
        >
          {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
        </button>
      </div>
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
