import { useContext, useState, useMemo } from "react";
import { OverlayWidgetData } from "../../types/map";
import Widget from "../widgets/Widget";
import { ManifestContext } from "../../common/contexts/ManifestContext";

interface OverlayContainerProps {
  group: string;
  view: string;
  widgets: Record<string, OverlayWidgetData>;
  moveUp?: () => void;
  moveDown?: () => void;
}

// Basically the overlay for the overlay's widget container
export default function OverlayContainer({
  group,
  view,
  widgets,
  moveUp,
  moveDown,
}: OverlayContainerProps) {
  const manifest = useContext(ManifestContext);

  const [show, setShow] = useState(true);

  // The Memoised widgets sorted by their specified order
  const sortedWidgets = useMemo(
    () =>
      Object.values(widgets).sort(
        (a, b) => (a.order ?? 1000) - (b.order ?? 1000),
      ),
    [widgets],
  );

  return (
    <div className="overlay-container leaflet-bar">
      <div className="overlay-header">
        <h1 className="overlay-title">
          {manifest[group].name} - {manifest[group].views[view].name}
        </h1>
        {moveUp && moveDown && (
          <div className="overlay-options">
            <button className="show-toggle" onClick={() => setShow((s) => !s)}>
              {show ? (
                <span className="material-symbols-outlined">minimize</span>
              ) : (
                <span className="material-symbols-outlined">add</span>
              )}
            </button>
            <button className="up-arrow" onClick={moveUp}>
              <span className="material-symbols-outlined">arrow_upward</span>
            </button>
            <button className="down-arrow" onClick={moveDown}>
              <span className="material-symbols-outlined">arrow_downward</span>
            </button>
          </div>
        )}
      </div>
      {show && (
        <div className="widget-container">
          {sortedWidgets.map((w) => (
            <Widget key={w.name} title={w.name} size={w.size}>
              {w.component}
            </Widget>
          ))}
        </div>
      )}
    </div>
  );
}
