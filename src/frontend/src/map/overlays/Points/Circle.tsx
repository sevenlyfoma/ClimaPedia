import { Tooltip, CircleMarker } from "react-leaflet";
import * as L from "leaflet";
import { DeepRequired } from "ts-essentials";
import { BasePointData } from "../../../types/common";

interface CircleProps<T extends DeepRequired<BasePointData>> {
  index: number;
  data: T;
  handleClick: (id: string) => L.LeafletEventHandlerFn;
  pointProps: L.CircleMarkerOptions;
  active?: boolean;
}

// Circluar points, to appear the same size on screen regardless of zoom
export function Circle<T extends DeepRequired<BasePointData>>({
  index: i,
  data,
  handleClick,
  pointProps,
  active = true,
}: CircleProps<T>) {
  const activity = active ? {} : { fillOpacity: 0.2, opacity: 0.2 };
  return (
    <CircleMarker
      key={active ? `point-${i}-active` : `point-${i}-inactive`}
      center={data.coords[i]}
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
            {data.labels?.[i]}
          </Tooltip>
        )
      }
    </CircleMarker>
  );
}
