import { MapContainer, TileLayer } from "react-leaflet";
import "./Map.css";
import ToggledOverlays from "./ToggledOverlays";
import Legend from "../common/Legend/Legend";
import { useToggledParams } from "../common/hooks/useQueryParams";
import { useManifest } from "../common/hooks/useManifest";
import { useRef } from "react";
import { Map } from "leaflet";

export function MapPage() {
  const manifest = useManifest("map");
  const [toggled, setToggled] = useToggledParams(manifest, true);

  const ref = useRef<Map | null>(null);

  const largeFont = document.documentElement.classList.contains("large-font");

  // Using leaflet for rendering the map
  // Using react-leaflet for React bindings
  return (
    <MapContainer
      id="map"
      center={[50, 0]}
      zoom={4}
      scrollWheelZoom={true}
      minZoom={2}
      maxBounds={[
        [-90, -600],
        [90, 600],
      ]}
      doubleClickZoom={false}
      ref={ref}
    >
      <TileLayer
        attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        noWrap={true}
        tileSize={256 * (largeFont ? 2 : 1)}
        zoomOffset={largeFont ? -1 : 0}
      />
      <Legend
        manifest={manifest}
        multiple={true}
        toggledView={toggled}
        setToggledView={setToggled}
        map={ref.current ?? undefined}
      />
      <ToggledOverlays
        toggledOverlays={toggled}
        setToggledOverlays={setToggled}
      />
    </MapContainer>
  );
}
