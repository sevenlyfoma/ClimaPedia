import { useContext, useEffect } from "react";
import { useData } from "./useData";
import { MapPointHeatData } from "../../types/api";
import { OverlayContext } from "./OverlayContext";
import { useMap } from "react-leaflet";
import ContinuousLegend from "../widgets/ContinuousLegend";
import L from "leaflet";
import "leaflet.heat";
import { normalise, paneKey } from "../../utils/common";
import {
  colourArrayToMagnitude,
  magnitudesToColourArray,
} from "../../utils/colour";

// The Map + Point-Heat visualisation
export function PointHeat() {
  const { updateWidget, group, view } = useContext(OverlayContext);
  const { data } = useData<MapPointHeatData>();
  const map = useMap();

  // Imperatively defining the heat map
  useEffect(() => {
    if (data == null) {
      return;
    }

    const heat = L.heatLayer(
      data.coords.map((c, i) => [
        ...c,
        normalise(data.values[i], data.valuesLegend.valueRange),
      ]),
      {
        minOpacity: data.heatStyle?.minOpacity,
        maxZoom: data.heatStyle?.maxZoom,
        radius: data.heatStyle?.radius,
        blur: data.heatStyle?.blur,
        gradient: data.valuesLegend.colourRange
          ? colourArrayToMagnitude(data.valuesLegend.colourRange)
          : undefined,
        // @ts-expect-error Types not up to date with library
        pane: paneKey(group, view),
      },
    ).addTo(map);

    return () => {
      map.removeLayer(heat);
    };
  }, [data, map, group, view]);

  // Add value legend widget if necessary
  useEffect(() => {
    if (data?.valuesLegend != undefined) {
      // If colour range not defined, use default for leaflet.heat instead of black and white
      updateWidget("point-heat-legend", {
        name: "Heat Legend",
        component: (
          <ContinuousLegend
            legend={{
              ...data.valuesLegend,
              colourRange:
                data.valuesLegend.colourRange ??
                magnitudesToColourArray({
                  0.0: "blue",
                  0.4: "blue",
                  0.65: "green",
                  1: "red",
                }),
            }}
          />
        ),
      });
      return () => updateWidget("point-heat-legend", null);
    }
  }, [updateWidget, data?.valuesLegend]);

  return null;
}
