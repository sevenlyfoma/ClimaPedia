import { Rectangle, Tooltip, useMap } from "react-leaflet";
import { LatLngBoundsLiteral, LeafletEventHandlerFn } from "leaflet";
import { useEffect, useState } from "react";
import * as L from "leaflet";
import { DeepRequired } from "ts-essentials";
import { BasePointData } from "../../../types/common";

interface SqaureProps<T extends DeepRequired<BasePointData>> {
  data: T;
  index: number;
  pointProps: L.PolylineOptions & { radius: number };
  handleClick: (id: string) => LeafletEventHandlerFn;
  active?: boolean;
}

// Square points, to appear the same size on screen regardless of zoom
export function Square<T extends DeepRequired<BasePointData>>({
  data,
  index: i,
  pointProps,
  handleClick,
  active = true,
}: SqaureProps<T>) {
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

  const activity = active ? {} : { fillOpacity: 0.2, opacity: 0.2 };

  const bounds = [
    [
      data.coords[i][0] - pointProps.radius / zoom,
      data.coords[i][0] - pointProps.radius / zoom,
    ],
    [
      data.coords[i][0] + pointProps.radius / zoom,
      data.coords[i][0] + pointProps.radius / zoom,
    ],
  ];

  return (
    <Rectangle
      key={active ? `point-${i}-active` : `point-${i}-inactive`}
      data-colour={pointProps.fillColor}
      pane={active ? pointProps.pane : "inactive"}
      bounds={bounds as LatLngBoundsLiteral}
      {...pointProps}
      {...activity}
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
            {data.labels?.[i]}
          </Tooltip>
        )
      }
    </Rectangle>
  );
}
