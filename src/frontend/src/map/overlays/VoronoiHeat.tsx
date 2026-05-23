import { useContext, useEffect } from "react";
import { useData } from "./useData";
import { MapVoronoiHeatData, PartData } from "../../types/api";
import { OverlayContext } from "./OverlayContext";
import { Polygon } from "react-leaflet";
import ContinuousLegend from "../widgets/ContinuousLegend";
import { getContinuousColour } from "../../utils/colour";
import { defaultMapVoronoiHeatData } from "../../utils/default";
import * as L from "leaflet";
import { usePart } from "./usePart";
import { colourMapVoronoiHeat } from "../../utils/colourmap";
import { paneKey } from "../../utils/common";

// Map + Voronoi-Hear visualisation
export function VoronoiHeat() {
  const { updateWidget, group, view } = useContext(OverlayContext);
  const { data, getPart } = useData<MapVoronoiHeatData, PartData>(
    defaultMapVoronoiHeatData,
    colourMapVoronoiHeat,
  );
  const { handleClick } = usePart(getPart, data?.ids ?? [], setPartStyle);

  // ADding the legend to widgets
  useEffect(() => {
    if (data?.valuesLegend != undefined) {
      updateWidget("voronoi-heat-legend", {
        name: "Heat Legend",
        component: <ContinuousLegend legend={data.valuesLegend} />,
      });
      return () => updateWidget("voronoi-heat-legend", null);
    }
  }, [updateWidget, data?.valuesLegend]);

  if (data == null) {
    return null;
  }

  // For the usePart hook
  function setPartStyle(el: L.Polygon, enable: boolean) {
    if (data == null) {
      return;
    }
    if (enable) {
      el.setStyle({ weight: data.heatStyle.edgeThickness * 2 });
    } else {
      el.setStyle({ weight: data.heatStyle.edgeThickness });
    }
  }

  // path options given part index
  function pathOptions(i: number) {
    if (data == null) {
      return;
    }

    return {
      fillColor:
        data.values !== null && data.valuesLegend !== null
          ? getContinuousColour(
              data.values[i],
              data.valuesLegend.valueRange,
              data.valuesLegend.colourRange,
            )
          : "white",
      fillOpacity: data.heatStyle.opacity,
      opacity: data.heatStyle.edgeOpacity,
      color:
        data.heatStyle.edgeColour ??
        (data.values !== null && data.valuesLegend !== null
          ? getContinuousColour(
              data.values[i],
              data.valuesLegend.valueRange,
              data.valuesLegend.colourRange,
            )
          : "white"),
      stroke: true,
    };
  }

  return data.polygons.map((p, i) => (
    <Polygon
      className={data.clickable ? "click" : "no-click"}
      key={i}
      pathOptions={pathOptions(i)}
      positions={p}
      weight={data.heatStyle.edgeThickness}
      pane={paneKey(group, view)}
      eventHandlers={
        data.clickable
          ? {
              click: handleClick(data.ids[i]),
            }
          : undefined
      }
    />
  ));
}
