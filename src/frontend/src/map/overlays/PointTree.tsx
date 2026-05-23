import { useContext, useEffect, useState, useMemo } from "react";
import { Polyline, useMap } from "react-leaflet";
import { GetPartFn, MapPointTreeData, PartData } from "../../types/api";
import { OverlayContext } from "./OverlayContext";
import { useData } from "./useData";
import _ from "lodash";
import ContinuousLegend from "../widgets/ContinuousLegend";
import { getContinuousColour } from "../../utils/colour";
import { InteractiveSeries } from "../../types/common";
import SeriesLegend from "../widgets/SeriesLegend";
import { applyDefault, defaultMapPointTreeData } from "../../utils/default";
import { DeepRequired } from "ts-essentials";
import { usePart } from "./usePart";
import * as L from "leaflet";
import { Circle } from "./Points/Circle";
import { normalise, paneKey } from "../../utils/common";
import { Square } from "./Points/Square";
import { Star } from "./Points/Star";
import { Triangle } from "./Points/Triangle";

// Given an id and a map of all nodes, return a list of all nodes to remove
function removeNode(
  nodes: Record<string | symbol, MapPointTreeNode>,
  id: string,
): string[] {
  const p = nodes[id];

  if (p === undefined) {
    return [];
  }

  const out = p.ids.flatMap((i) => removeNode(nodes, i));
  out.push(id);
  return out;
}

export interface MapPointTreeNode extends DeepRequired<MapPointTreeData> {
  root?: [number, number];
}

// Map + Point-Tree visualisation
export function PointTree() {
  const { updateWidget, group, view } = useContext(OverlayContext);
  const { data, getPart } = useData<
    MapPointTreeData,
    MapPointTreeData | PartData
  >(defaultMapPointTreeData);
  const map = useMap();

  const [nodes, setNodes] = useState<Record<string | symbol, MapPointTreeNode>>(
    {},
  );

  // Calculating the ids currently on screen
  const validIds = useMemo(
    () => Object.values(nodes).flatMap((n) => n.ids),
    [nodes],
  );

  const [series, setSeries] = useState<InteractiveSeries[] | null>(null);
  const { handleClick } = usePart(
    getPart as GetPartFn<PartData>,
    validIds,
    setPartStyle,
    { info: "1" },
  );

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
  }, [data]);

  // Creating new pane to ensure lines are below points
  useEffect(() => {
    const line = map.createPane("line");
    line.style.zIndex = "399";
  }, [map]);

  // Setting the root node
  useEffect(() => {
    if (data == null) {
      return;
    }

    setNodes((n) => {
      if (n.root === undefined) {
        return { root: data };
      }

      // Ensuring we don't remove the expanded nodes if they are still there
      const notIncluded = _.difference(n.root.ids, data.ids);
      const toRemove = notIncluded.flatMap((k) => removeNode(n, k));
      const newN = _.omit(n, toRemove) as Record<
        string | symbol,
        MapPointTreeNode
      >;
      newN.root = data;
      return newN;
    });
  }, [data]);

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
    data?.valuesLegend &&
      updateWidget("continuous-legend", {
        name: "Legend",
        component: <ContinuousLegend legend={data.valuesLegend} />,
        order: 10,
      });

    // Removing widget on unmount
    return () => updateWidget("continuous-legend", null);
  }, [data, updateWidget]);

  // Create the inactive pane if it doesn't exist
  useEffect(() => {
    let p = map.getPane("inactive");
    if (p == null) {
      p = map.createPane("inactive");
      p.style.zIndex = "350";
    }
  }, [map]);

  if (data === null) {
    return null;
  }

  // Rendering points with their corresponding lines to form a tree
  return Object.values(nodes).flatMap((d) =>
    d.coords.flatMap((c, i) => {
      function clickHandler(id: string): L.LeafletEventHandlerFn {
        // Toggling children nodes
        return (e) => {
          if (nodes[id] === undefined) {
            getPart(id)
              .then((parts) => {
                if (parts === null) {
                  return;
                }
                const outParts = applyDefault(
                  defaultMapPointTreeData,
                  parts as MapPointTreeData,
                );
                setNodes((p) => {
                  const newP = _.cloneDeep(p);
                  newP[id] = { ...outParts, root: c };
                  return newP;
                });
              })
              .catch((err) => console.error(err));
          } else {
            // Remove nodes children and grandchildren and so on
            setNodes((p) => {
              const toRemove = removeNode(nodes, id);

              // Omit creates a new object so no need to clone
              return _.omit(p, toRemove);
            });
          }

          handleClick(id)(e);
        };
      }

      const fillColour = d.valuesLegend
        ? getContinuousColour(
            d.values![i],
            d.valuesLegend.valueRange,
            d.valuesLegend.colourRange,
          )
        : series
          ? series[d.series![i]].colour ?? "blue"
          : d.defaultColour ?? "cyan";

      const radius = normalise(d.sizes[i], d.sizeRange) * 20 + 5;

      const pointProps = {
        center: c,
        className: "click",
        radius,
        fill: true,
        fillColor: fillColour,
        color: "black",
        stroke: true,
        weight: 1,
        pane: paneKey(group, view),
        fillOpacity: 1,
      };

      const shape = series ? series[d.series![i]].shape : d.shapes[i];
      const active = !series || series[d.series![i]].active;
      const props = {
        data: { ...d, clickable: true },
        handleClick: clickHandler,
        pointProps,
        index: i,
        active,
        key: `point-${d.ids[i]}`,
      };

      let point = <Circle {...props} />;
      if (shape === "square") {
        point = <Square {...props} />;
      } else if (shape === "star") {
        point = <Star {...props} points={5} />;
      } else if (shape === "star10") {
        point = <Star {...props} points={10} />;
      } else if (shape === "triangle") {
        point = <Triangle {...props} />;
      }

      return [
        d.root ? (
          <Polyline
            key={"line-" + d.ids[i]}
            weight={d.edgeThicknesses?.[i] ? d.edgeThicknesses[i] : 2}
            opacity={0.5}
            color={"#000"}
            pane={"line"}
            interactive={false}
            positions={[c, d.root]}
          />
        ) : null,
        point,
      ];
    }),
  );
}
