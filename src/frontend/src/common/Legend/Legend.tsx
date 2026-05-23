import { Map } from "leaflet";
import { GroupsManifest } from "../../types/api";
import { Focus, ViewInfo } from "../../types/common";
import { DropDownViews } from "./DropDownViews";

// settings for Legend
// includes booleans and Function to set state of checkboxes

interface LegendProps<T extends boolean> {
  multiple: T;
  toggledView: T extends true ? ViewInfo[] : ViewInfo | null;
  setToggledView: T extends true
    ? (value: ViewInfo[]) => void
    : (value: ViewInfo | null) => void;
  manifest?: GroupsManifest<Focus>;
  map?: Map;
}

// Creates Legend in bottom left hand corner
export default function Legend({
  toggledView,
  setToggledView,
  multiple,
  manifest,
  map,
}: LegendProps<boolean>) {
  return (
    <div id="legendBox" className="leaflet-left leaflet-bottom leaflet-control">
      <DropDownViews
        toggledView={toggledView}
        setToggledView={setToggledView}
        multiple={multiple}
        manifest={manifest}
        map={map}
      />
    </div>
  );
}
