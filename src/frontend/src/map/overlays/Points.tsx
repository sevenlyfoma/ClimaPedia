import { LayerGroup, useMap } from "react-leaflet";
import { useContext, useEffect, useMemo, useState } from "react";
import SeriesLegend from "../widgets/SeriesLegend";
import { InteractiveSeries } from "../../types/common";
import _ from "lodash";
import { OverlayContext } from "./OverlayContext";
import ContinuousLegend from "../widgets/ContinuousLegend";
import { useData } from "./useData";
import { MapPointsData, PartData } from "../../types/api";
import { normalise, paneKey } from "../../utils/common";
import { defaultMapPointsData } from "../../utils/default";
import { usePart } from "./usePart";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";
import "leaflet.markercluster";
import * as L from "leaflet";
import { Square } from "./Points/Square";
import { Circle } from "./Points/Circle";
import { Triangle } from "./Points/Triangle";
import { Star } from "./Points/Star";
import { getContinuousColour } from "../../utils/colour";
import { colourMapPointsData } from "../../utils/colourmap";

// Map + Points visualisation
export function Points() {
  const { updateWidget, group, view } = useContext(OverlayContext);
  const { data, getPart } = useData<MapPointsData, PartData>(
    defaultMapPointsData,
    colourMapPointsData,
  );
  const { handleClick, id: selectedId } = usePart(
    getPart,
    data?.ids ?? [],
    setPartStyle,
  );
  const [series, setSeries] = useState<InteractiveSeries[] | null>(null);
  const map = useMap();

  // Formatting the point data into passable props
  const pointData = useMemo(
    () =>
      data?.coords
        .map((coord, i) => {
          // If series legend exists, use that colour, else use defaultColour
          let colour = data.defaultColour;
          if (data.seriesLegend !== null && data.series !== null) {
            colour =
              data.seriesLegend[data.series[i]].colour ?? data.defaultColour;
          } else if (data.valuesLegend !== null && data.values !== null) {
            // Colour from normalised value
            const { valueRange, colourRange } = data.valuesLegend;
            colour = getContinuousColour(
              data.values[i],
              valueRange,
              colourRange,
            );
          }

          // Handling sized points
          const radius = normalise(data.sizes[i], data.sizeRange) * 20 + 5;
          const shape = data.shapes?.[i] ?? null;
          const series = data.series?.[i] ?? null;

          return {
            coord,
            colour,
            radius,
            shape,
            series,
          };
        })
        .map((d) => ({
          center: d.coord,
          className: data.clickable ? "click" : "no-click",
          radius: d.radius,
          fill: true,
          fillColor: d.colour,
          color: "black",
          stroke: true,
          weight: 1,
          pane: paneKey(group, view),
          fillOpacity: 1,
        })),
    [data, group, view],
  );

  // Hook for imperatively adding clustering
  useEffect(() => {
    if (pointData == null || data == null || !data.clustering) {
      return;
    }

    const cluster = L.markerClusterGroup({
      polygonOptions: {
        fillColor: "var(--replace-white)",
        color: "var(--replace-black)",
        opacity: 0.5,
      },
      pane: paneKey(group, view),
      clusterPane: paneKey(group, view),
    });

    let points = pointData?.map((d, i) => {
      const c = L.circleMarker(d.center, d);

      // Point recreated every use effect call
      // Therefore must set active part style every time
      if (data.ids[i] === selectedId) {
        setPartStyle(c, true);
      }
      return c;
    });

    if (data?.labels != null) {
      points.forEach((p, i) => {
        p.bindTooltip(
          L.tooltip({
            content: data.labels![i],
            permanent: !data.labelsOnHover,
            direction: "bottom",
            offset: [0, 10],
            opacity: 0.9,
          }),
        );
      });
    }

    if (data.clickable) {
      points.forEach((p, i) => {
        p.addEventListener("click", handleClick(data.ids[i]));
      });
    }

    if (series != null) {
      points = points.filter((_p, i) => series[data.series![i]].active);
    }

    cluster.addLayers(points);
    map.addLayer(cluster);
    return () => {
      map.removeLayer(cluster);
    };
  }, [data, group, handleClick, map, pointData, selectedId, series, view]);

  // Updating series state if series legend exists
  useEffect(() => {
    if (data?.seriesLegend) {
      setSeries(
        data.seriesLegend.map((s) => ({
          ...s,
          active: true,
        })),
      );
    }
  }, [data?.seriesLegend]);

  // Adding series legend widget if series legend exists
  useEffect(() => {
    series !== null &&
      updateWidget("series-legend", {
        name: "Legend",
        component: <SeriesLegend series={series} toggle={toggleSeries} />,
        order: 10,
      });

    // Removing widget on unmount
    return () => updateWidget("series-legend", null);
  }, [series, updateWidget]);

  // Adding continuous legend if exists
  useEffect(() => {
    data?.valuesLegend != null &&
      updateWidget("continuous-legend", {
        name: "Legend",
        component: <ContinuousLegend legend={data.valuesLegend} />,
        order: 10,
      });

    // Removing widget on unmount
    return () => updateWidget("continuous-legend", null);
  }, [data, updateWidget]);

  // Don't render anything if the data hasn't loaded
  if (data == null) {
    return;
  }

  // For the usePart hook
  function setPartStyle(el: L.CircleMarker, enable: boolean) {
    if (enable) {
      el.setStyle({ weight: 3 });
    } else {
      el.setStyle({ weight: 1 });
    }
  }

  // For toggling series interactively
  function toggleSeries(id: number) {
    setSeries((sx) => {
      if (sx == null) {
        return sx;
      }
      const out = _.cloneDeep(sx);
      out[id].active = !out[id].active;
      return out;
    });
  }

  // We render clustering imperatively instead of through react
  if (data.clustering) {
    return null;
  }

  // The points to be rendered
  const points =
    pointData?.map((d, i) => {
      const shape = series ? series[data.series![i]].shape : data.shapes[i];

      const props = {
        handleClick,
        index: i,
        data,
        pointProps: d,
        key: data.ids[i],
      };

      switch (shape) {
        case "square":
          return <Square {...props} />;
        case "triangle":
          return <Triangle {...props} />;
        case "star":
          return <Star {...props} points={5} />;
        case "star10":
          return <Star {...props} points={10} />;
        default:
          return <Circle {...props} />;
      }
    }) ?? [];

  // Whether to render in series or not
  if (series !== null) {
    // Only active series get rendered
    return series.map((_, i) =>
      series[i].active ? (
        <LayerGroup key={i}>
          {points.filter((_, j) => data.series![j] === i)}
        </LayerGroup>
      ) : null,
    );
  } else {
    return points;
  }
}
