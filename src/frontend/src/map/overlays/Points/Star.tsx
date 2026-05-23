import { Polygon, Tooltip, useMap } from "react-leaflet";
import { useEffect, useState } from "react";
import { DeepRequired } from "ts-essentials";
import { BasePointData } from "../../../types/common";
import * as L from "leaflet";

interface StarProps<T extends DeepRequired<BasePointData>> {
  data: T;
  index: number;
  handleClick: (id: string) => L.LeafletEventHandlerFn;
  pointProps: L.PolylineOptions & { radius: number };
  points: number;
  active?: boolean;
}

// Star points, to appear the same size on screen regardless of zoom
export function Star<T extends DeepRequired<BasePointData>>({
  data,
  index: i,
  handleClick,
  pointProps,
  points,
  active = true,
}: StarProps<T>) {
  const map = useMap();
  const [zoom, setZoomLevel] = useState(Math.pow(2, map.getZoom()));

  useEffect(() => {
    const handleZoom = () => {
      const newZoomLevel = map.getZoom();
      if (newZoomLevel !== undefined) {
        setZoomLevel(Math.pow(2, newZoomLevel));
      }
    };

    if (map) {
      map.on("zoom", handleZoom);
    }

    return () => {
      if (map) {
        map.off("zoom", handleZoom);
      }
    };
  }, [map]);

  const latlngs: L.LatLngExpression[] = [];
  const innerRadius = pointProps.radius * 0.5;

  for (let j = 0; j < points * 2; j++) {
    const angle = (j * Math.PI) / points;
    const r = j % 2 === 0 ? pointProps.radius : innerRadius;
    const x = data.coords[i][0] + (r * Math.cos(angle)) / (zoom / 2);
    const y = data.coords[i][1] + (r * Math.sin(angle)) / (zoom / 2);
    latlngs.push([x, y]);
  }

  const activity = active ? {} : { fillOpacity: 0.2, opacity: 0.2 };

  return (
    <Polygon
      key={active ? `point-${i}-active` : `point-${i}-inactive`}
      positions={latlngs}
      {...pointProps}
      {...activity}
      data-colour={pointProps.fillColor}
      pane={active ? pointProps.pane : "inactive"}
      eventHandlers={
        active && data.clickable
          ? {
              click: handleClick(data.ids[i]),
            }
          : undefined
      }
    >
      {
        // Adding labels if they exist
        active && data.labels?.[i] && (
          <Tooltip
            permanent={!data.labelsOnHover}
            offset={[0, 10]}
            direction="bottom"
            opacity={0.9}
          >
            {data.labels[i]}
          </Tooltip>
        )
      }
    </Polygon>
  );
}
