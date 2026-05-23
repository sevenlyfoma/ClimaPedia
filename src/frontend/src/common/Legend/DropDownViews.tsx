import { useContext } from "react";
import Dropdown from "react-bootstrap/Dropdown";
import { ManifestContext } from "../contexts/ManifestContext";
import _ from "lodash";
import { Focus, ViewInfo } from "../../types/common";
import { GroupsManifest } from "../../types/api";
import { Map } from "leaflet";
import { paneKey } from "../../utils/common";

interface DropDownViewsProps<T extends boolean> {
  multiple: T;
  toggledView: T extends true ? ViewInfo[] : ViewInfo | null;
  setToggledView: T extends true
    ? (value: ViewInfo[]) => void
    : (value: ViewInfo | null) => void;
  manifest?: GroupsManifest<Focus>;
  map?: Map;
}

function dropdownSingleItemClick(
  group: string,
  view: string,
  toggledView: ViewInfo | null,
  setToggledView: (v: ViewInfo | null) => void,
) {
  if (toggledView == null) {
    setToggledView({ group, view, index: 0 });
  } else if (toggledView.group === group && toggledView.view === view) {
    setToggledView(null);
  } else {
    setToggledView({ group, view, index: toggledView.index });
  }
}

export function DropDownViews<T extends boolean>(props: DropDownViewsProps<T>) {
  // Default to global manifest if no local one provided
  const globalManifest = useContext(ManifestContext);
  const manifest = props.manifest ?? globalManifest;

  const views = Object.entries(manifest).flatMap(([group, groupObj]) => {
    return Object.keys(groupObj.views).map((view) => {
      return [group, view];
    });
  });

  function shiftOverlays(overlays: ViewInfo[]) {
    if (!props.map) {
      return overlays;
    }

    // Reodering logic
    for (let i = overlays.length - 1; i >= 0; i--) {
      overlays[i].index!++;
      const pane = props.map.getPane(
        paneKey(overlays[i].group, overlays[i].view),
      );
      if (pane) {
        const zIndex = 460 - overlays[i].index! + 1;
        pane.style.zIndex = String(zIndex);
      }
    }
    return overlays;
  }

  function dropdownMultipleItemClick(
    group: string,
    view: string,
    toggledView: ViewInfo[],
    setToggledView: (v: ViewInfo[]) => void,
  ) {
    const toggled: ViewInfo[] = _.cloneDeep(toggledView);
    const index = 0;

    // If overlay already toggled, then deactivate, else add to toggled
    const found_overlay = toggled.findIndex(
      (a) => a.group === group && a.view === view,
    );
    if (found_overlay !== -1) {
      toggled.splice(found_overlay, 1);
    } else {
      let reorderedOverlays = shiftOverlays(toggled);
      reorderedOverlays.push({
        group,
        view,
        index,
      });
      reorderedOverlays.sort((a, b) => a.index! - b.index!);
      reorderedOverlays = shiftOverlays(reorderedOverlays);
      setToggledView(reorderedOverlays);
    }

    setToggledView(toggled);
  }

  // This is painful
  function isTrue(
    m: DropDownViewsProps<boolean>,
  ): m is DropDownViewsProps<true> {
    return m.multiple;
  }
  function isFalse(
    m: DropDownViewsProps<boolean>,
  ): m is DropDownViewsProps<false> {
    return !m.multiple;
  }

  return (
    <Dropdown>
      <Dropdown.Toggle
        variant="primary"
        className="leaflet-control overlay-title c-shadow p-2"
      >
        <span className="material-symbols-outlined">layers</span>
      </Dropdown.Toggle>
      <Dropdown.Menu className="leaflet-control dropdownMenu c-shadow ms-0">
        {views.map(([group, view]) => (
          <Dropdown.Item
            className={`dropdownItem ${
              (
                isTrue(props)
                  ? props.toggledView.find(
                      (a) => a.group === group && a.view === view,
                    )
                  : isFalse(props)
                    ? props.toggledView?.group === group &&
                      props.toggledView.view === view
                    : ""
              )
                ? "dropdown-toggled"
                : ""
            }`}
            key={view}
            onClick={() =>
              isTrue(props)
                ? dropdownMultipleItemClick(
                    group,
                    view,
                    props.toggledView,
                    props.setToggledView,
                  )
                : isFalse(props)
                  ? dropdownSingleItemClick(
                      group,
                      view,
                      props.toggledView,
                      props.setToggledView,
                    )
                  : null
            }
          >
            {manifest[group].views[view].name}
          </Dropdown.Item>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
}
