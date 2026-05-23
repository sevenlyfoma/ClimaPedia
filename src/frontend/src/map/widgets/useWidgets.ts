import { createContext, useCallback, useContext } from "react";
import { OverlayWidgetData } from "../../types/map";

export interface WidgetContextProps {
  updateWidget: (
    group: string,
    view: string,
    widgetId: string,
    data: OverlayWidgetData | null,
  ) => void;
}

export const WidgetContext = createContext<WidgetContextProps>({
  updateWidget: () => undefined,
});

// Should be called within widget context
export default function useWidgets(group: string, view: string) {
  const { updateWidget: fullUpdateWidget } = useContext(WidgetContext);

  // Binding view and group name to updateWidget callback
  const updateWidget = useCallback(
    (id: string, data: OverlayWidgetData | null) =>
      fullUpdateWidget(group, view, id, data),
    [group, view, fullUpdateWidget],
  );

  return {
    updateWidget,
  };
}
