import L from "leaflet";
import "./ActiveControl.css";
import { ReactElement, useEffect, useRef, useState } from "react";

// Classes used by Leaflet to position controls
const POSITION_CLASSES = {
  bottomleft: "leaflet-bottom leaflet-left",
  bottomright: "leaflet-bottom leaflet-right",
  topleft: "leaflet-top leaflet-left",
  topright: "leaflet-top leaflet-right",
};

interface ActiveOverlayControlProps extends L.ControlOptions {
  children: ReactElement[];
  topPadding?: number;
}

// For displaying additional info related to toggled overlays
export default function ActiveOverlayControl(props: ActiveOverlayControlProps) {
  const [expanded, setExpanded] = useState<boolean>(true);
  // Hep with defining custom control positioning from https://react-leaflet.js.org/docs/example-react-control/
  const controlRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    controlRef.current !== null &&
      L.DomEvent.disableScrollPropagation(controlRef.current);
  });

  const positionClass =
    props.position !== undefined
      ? POSITION_CLASSES[props.position]
      : POSITION_CLASSES.topright;
  function toggleExpand() {
    setExpanded((b) => !b);
  }
  return (
    <div
      id="activeContainerSpacer"
      className={`w-100 ${positionClass}`}
      ref={controlRef}
    >
      <div
        className={`leaflet-control leaflet-bar active-container c-shadow p-1 m-0 p-fixed ${
          !expanded ? "control-hidden" : ""
        }`}
        style={props.topPadding ? { top: `${props.topPadding}px` } : {}}
      >
        <h2 className="active-header ms-1">Toggled Overlays</h2>
        <button
          className="active-button leaflet-bar bg-transparent border-0"
          onClick={toggleExpand}
        >
          {expanded ? (
            <span className="material-symbols-outlined">close</span>
          ) : (
            <span className="material-symbols-outlined">add</span>
          )}
        </button>
        <div className="active-body">
          {props.children.length === 0 ? (
            <p>
              <i>No toggled overlays</i>
            </p>
          ) : (
            props.children
          )}
        </div>
      </div>
    </div>
  );
}
