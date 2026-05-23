import { createContext } from "react";
import { OverlayWidgetData } from "../../types/map";
import { Bounds, InteractiveTimeMetaData } from "../../types/common";

export interface OverlayContextProps {
  group: string;
  view: string;
  updateWidget: (id: string, data: OverlayWidgetData | null) => void;
  timeData: InteractiveTimeMetaData | null;
  reloadForBounds: Bounds | null;
  country: string | null;
}

// Basically the props to be passed to the overlays
// Includes meta info and function to add or remove related widgets
export const OverlayContext = createContext<OverlayContextProps>({
  group: "",
  view: "",
  updateWidget: () => undefined,
  timeData: null,
  reloadForBounds: null,
  country: null,
});
