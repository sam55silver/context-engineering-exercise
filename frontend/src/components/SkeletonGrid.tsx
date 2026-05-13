export function SkeletonGrid() {
  return (
    <div className="grid">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="card skeleton">
          <div className="skeleton-line skeleton-title" />
          <div className="skeleton-line skeleton-meta" />
          <div className="skeleton-line skeleton-btn" />
        </div>
      ))}
    </div>
  );
}
