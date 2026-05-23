// Loading screen
export function Loading() {
  return (
    <div className="loading">
      <div
        className="spinner-grow text-muted"
        role="status"
        style={{ width: 100, height: 100, animationDuration: "2s" }}
      />
    </div>
  );
}
