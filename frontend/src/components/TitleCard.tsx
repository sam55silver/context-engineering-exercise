import type { WatchlistItem, Title } from "../api";

type Props = {
  item: WatchlistItem | Title;
  action?: React.ReactNode;
  watched?: boolean;
};

export function TitleCard({ item, action, watched }: Props) {
  return (
    <div className={`card ${watched ? "watched" : ""}`}>
      <h3>{item.title}</h3>
      <div className="meta">
        <span className="kind">{item.kind}</span> · {item.release_year} · {item.genre}
      </div>
      {action}
    </div>
  );
}
