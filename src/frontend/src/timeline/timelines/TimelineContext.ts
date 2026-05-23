import { createContext } from "react";
import { OverlayWidgetData } from "../../types/map";

export interface TimelineContextProps {
  group: string;
  view: string;
  updateWidget: (id: string, data: OverlayWidgetData | null) => void;
}

export const TimelineContext = createContext<TimelineContextProps>({
  group: "",
  view: "",
  updateWidget: () => undefined,
});
