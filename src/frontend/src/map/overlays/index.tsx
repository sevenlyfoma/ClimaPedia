import {
  ReactElement,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { MapType } from "../../types/map";
import { Points } from "./Points";
import { OverlayContext, OverlayContextProps } from "./OverlayContext";
import { ManifestContext } from "../../common/contexts/ManifestContext";
import {
  Bounds,
  InteractiveTimeMetaData,
  TimeMetaData,
  ViewInfo,
} from "../../types/common";
import TimeSlider from "../widgets/TimeSlider";
import useWidgets from "../widgets/useWidgets";
import _ from "lodash";
import useMeta from "./useMeta";
import { useMap, useMapEvent } from "react-leaflet";
import { VoronoiHeat } from "./VoronoiHeat";
import { PointHeat } from "./PointHeat";
import CountrySelection from "./CountrySelection";
import CountrySelectionWidget from "../widgets/CountrySelection";
import L from "leaflet";
import { CountriesContext } from "../../common/contexts/CountriesContext";
import { PointTree } from "./PointTree";
import { paneKey } from "../../utils/common";

interface OverlayProps {
  overlay: ViewInfo;
}

// Populating the interactive elements of the time meta data
function createInteractiveMetaData(
  data: Required<TimeMetaData> | undefined,
  iData: InteractiveTimeMetaData | null,
  setTime?: (start: string, end: string) => void,
) {
  if (data === undefined) {
    return null;
  }

  return {
    ...data,
    startTime: iData?.startTime ?? data.defaultStartTime,
    endTime:
      iData?.endTime ?? (data.persistent ? undefined : data.defaultEndTime),
    setTime: setTime ?? (() => undefined),
  } as InteractiveTimeMetaData;
}

// Handling selection of overlay type based map type
// Handling meta data stuff here
export function Overlay({ overlay }: OverlayProps) {
  const manifest = useContext(ManifestContext);
  const countries = useContext(CountriesContext);
  const { updateWidget } = useWidgets(overlay.group, overlay.view);
  const map = useMap();

  const mapType = manifest[overlay.group].views[overlay.view].type as MapType;

  // Getting the final metadata over the overlay
  const meta = useMeta(overlay.group, overlay.view, manifest);

  const [bounds, setBounds] = useState<Bounds | null>(() => {
    // Initial bounds
    const b = map.getBounds();

    return {
      latMax: b.getNorth(),
      latMin: b.getSouth(),
      longMax: b.getEast(),
      longMin: b.getWest(),
    };
  });
  const [country, setCountry] = useState<string | null>(null);

  const selectCountry = useCallback((c: string) => setCountry(c), []);

  // Changing the bounds one country selection
  useEffect(() => {
    if (country !== null) {
      const countryFeature = countries?.features.find(
        (f) => f.properties.ISO_A3 === country,
      );
      if (countryFeature === undefined) {
        return;
      }

      // Get the bounds of the country and pan to bounds
      const b = L.geoJSON(countryFeature).getBounds();
      setBounds({
        latMax: b.getNorth(),
        latMin: b.getSouth(),
        longMax: b.getEast(),
        longMin: b.getWest(),
      });
      map.fitBounds(b);
    }
  }, [country, map, countries]);

  // Update the bounds after the end of every movement
  useMapEvent("moveend", () => {
    if (meta?.reloadForBounds) {
      const b = map.getBounds();

      setBounds({
        latMax: b.getNorth(),
        latMin: b.getSouth(),
        longMax: b.getEast(),
        longMin: b.getWest(),
      });
    } else {
      // Don't bother keeping bounds up to date if we don't have to
      setBounds(null);
    }
  });

  const [timeData, setTimeData] = useState<InteractiveTimeMetaData | null>(
    createInteractiveMetaData(meta?.timeData ?? undefined, null),
  );

  // Updating time data
  useEffect(() => {
    setTimeData((t) =>
      createInteractiveMetaData(meta?.timeData ?? undefined, t, (start, end) =>
        setTimeData((t) => {
          if (t === null) {
            return null;
          }
          const copy = _.cloneDeep(t);
          copy.startTime = start;
          if (end !== undefined) {
            copy.endTime = end;
          }

          return copy;
        }),
      ),
    );
  }, [meta]);

  // Adding timeline widget
  useEffect(() => {
    if (timeData != null) {
      updateWidget("timeline", {
        name: "Timeline",
        component: <TimeSlider timeData={timeData} />,
        size: "big",
        order: 50,
      });

      return () => updateWidget("timeline", null);
    }
  }, [timeData, updateWidget, country]);

  // Adding generic description to widgets from manifest
  useEffect(() => {
    if (manifest[overlay.group].views[overlay.view].description !== undefined) {
      updateWidget("description", {
        name: "Description",
        component: (
          <p>{manifest[overlay.group].views[overlay.view].description}</p>
        ),
        order: 0,
      });

      // Removing widget on unmount
      return () => updateWidget("description", null);
    }
  }, [manifest, overlay.group, overlay.view, updateWidget, country]);

  // Displaying widget for how to select countries
  useEffect(() => {
    if ((meta?.viewCountries.length ?? 0) > 0 && country === null) {
      // Clear all widgets before rending country selection
      updateWidget("*", null);

      updateWidget("country-selection", {
        name: "Country Selection",
        component: <p>Select a country to view data for</p>,
        size: "small",
        order: 0,
      });

      return () => updateWidget("country-selection", null);
    } else if (country !== null) {
      const countryName =
        countries?.features.find((f) => f.properties.ISO_A3 === country)
          ?.properties.ADMIN ?? "???";

      updateWidget("country-selection", {
        name: "Country Selection",
        component: (
          <CountrySelectionWidget
            onReselect={() => setCountry(null)}
            countryName={countryName}
          />
        ),
        size: "small",
        order: 100,
      });

      return () => updateWidget("country-selection", null);
    }
  }, [country, meta?.viewCountries, updateWidget, countries]);

  // Creating pane for each overlay for reordering logic
  let pane = map.getPane(paneKey(overlay.group, overlay.view));
  if (pane === undefined) {
    map.createPane(paneKey(overlay.group, overlay.view));
    pane = map.getPane(paneKey(overlay.group, overlay.view));
    if (pane) {
      const zIndex = 460 - (overlay.index ?? 0);
      pane.style.zIndex = String(zIndex);
    }
  }

  // Meta must be defined before we render overlay
  // TimeData must be ready if exists
  if (meta === null || (meta.timeData !== null && timeData === null)) {
    return;
  }

  // Providing overlays with contextual data
  const contextValue: OverlayContextProps = {
    group: overlay.group,
    view: overlay.view,
    updateWidget,
    timeData,
    reloadForBounds: meta.reloadForBounds ? bounds : null,
    country,
  };

  // Dictionary of all overlay types
  const components: Record<MapType, ReactElement<Record<string, never>>> = {
    points: <Points />,
    "voronoi-heat": <VoronoiHeat />,
    "point-heat": <PointHeat />,
    "point-tree": <PointTree />,
  };

  if (components[mapType] === undefined) {
    console.error("There does not exist a visualisation type:", mapType);
    return null;
  }

  return (
    <OverlayContext.Provider value={contextValue}>
      {meta.viewCountries.length > 0 && country == null ? (
        <CountrySelection
          countries={meta.viewCountries}
          selectCountry={selectCountry}
        />
      ) : (
        components[mapType]
      )}
    </OverlayContext.Provider>
  );
}
