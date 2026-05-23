import { Polygon, Tooltip, useMap } from "react-leaflet";
import { useEffect, useState } from "react";
import { DeepRequired } from "ts-essentials";
import { BasePointData } from "../../../types/common";
import * as L from "leaflet";

interface TriangleProps<T extends DeepRequired<BasePointData>> {
  data: T;
  index: number;
  pointProps: L.PolylineOptions & { radius: number };
  handleClick: (id: string) => L.LeafletEventHandlerFn;
  active?: boolean;
}

// Triangle points, to appear the same size on screen regardless of zoom
export function Triangle<T extends DeepRequired<BasePointData>>({
  data,
  index: i,
  pointProps,
  handleClick,
  active = true,
}: TriangleProps<T>) {
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

  const latlngs: L.LatLngExpression[] = [
    [
      data.coords[i][0] - pointProps.radius / zoom,
      data.coords[i][1] - pointProps.radius / zoom,
    ],
    [data.coords[i][0] + pointProps.radius / zoom, data.coords[i][1]],
    [
      data.coords[i][0] - pointProps.radius / zoom,
      data.coords[i][1] + pointProps.radius / zoom,
    ],
  ];

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
