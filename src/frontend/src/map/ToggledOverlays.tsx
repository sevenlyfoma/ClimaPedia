import {
  useCallback,
  useEffect,
  useState,
  Dispatch,
  SetStateAction,
} from "react";
import { OverlayWidgetData } from "../types/map";
import ActiveOverlayControl from "./active-control";
import OverlayContainer from "./active-control/OverlayContainer";
import { Overlay } from "./overlays";
import _ from "lodash";
import { WidgetContext } from "./widgets/useWidgets";
import { ViewInfo } from "../types/common";
import { useMap } from "react-leaflet";
import { paneKey } from "../utils/common";

// group -> view -> widgetId -> widgetData
type OverlayWidgetDataCollection = Record<
  string,
  Record<string, Record<string, OverlayWidgetData>>
>;

export interface ToggledOverlaysProps {
  toggledOverlays: ViewInfo[];
  setToggledOverlays: Dispatch<SetStateAction<ViewInfo[]>>;
}

// Render toggled overlays
//  and display the toggled overlays in a control in the corner
export default function ToggledOverlays({
  toggledOverlays,
  setToggledOverlays,
}: ToggledOverlaysProps) {
  const [widgets, setWidget] = useState<OverlayWidgetDataCollection>({});

  const map = useMap();

  // Updating stored widgets on overlays changes
  useEffect(() => {
    setWidget((w) => {
      const newW = _.cloneDeep(w);

      return _.pick(
        newW,
        toggledOverlays.map((o) => [o.group, o.view]),
      ) as OverlayWidgetDataCollection;
    });
  }, [toggledOverlays]);

  // For adding new widgets for an overlay
  const updateWidget = useCallback(
    (
      group: string,
      view: string,
      widgetId: string,
      data: OverlayWidgetData | null,
    ) => {
      setWidget((w) => {
        const newW = _.cloneDeep(w);
        if (widgetId === "*") {
          _.unset(newW, [group, view]);
        } else if (data === null) {
          _.unset(newW, [group, view, widgetId]);
        } else {
          _.merge(newW, {
            [group]: { [view]: { [widgetId]: data } },
          });
        }

        return newW;
      });
    },
    [],
  );

  // For reording overlays in the active overlay control
  function moveUp(index: number) {
    setToggledOverlays((o) => {
      if (index <= 0) {
        return o;
      }
      const newO = _.cloneDeep(o);

      newO[index].index!--;
      let pane = map.getPane(paneKey(newO[index].group, newO[index].view));
      if (pane) {
        const zIndex = 460 - newO[index].index!;
        pane.style.zIndex = zIndex.toString();
      }

      for (let i = 0; i < newO.length; i++) {
        if (newO[i].index === index - 1 && newO[i] !== newO[index]) {
          newO[i].index!++;
          newO.sort((a, b) => a.index! - b.index!);

          pane = map.getPane(paneKey(newO[i + 1].group, newO[i + 1].view));
          if (pane) {
            const z = 460 - newO[i + 1].index!;
            pane.style.zIndex = String(z);
          }
        }
      }

      return newO;
    });
  }

  function moveDown(index: number) {
    setToggledOverlays((o) => {
      if (index >= o.length - 1) {
        return o;
      }

      const newO = _.cloneDeep(o);

      newO[index].index!++;
      let pane = map.getPane(paneKey(newO[index].group, newO[index].view));
      if (pane) {
        const zIndex = 460 - newO[index].index!;
        pane.style.zIndex = String(zIndex);
      }
      for (let i = 0; i < newO.length; i++) {
        if (newO[i].index === index + 1 && newO[i] !== newO[index]) {
          newO[i].index!--;
          newO.sort((a, b) => a.index! - b.index!);

          pane = map.getPane(paneKey(newO[i - 1].group, newO[i - 1].view));
          if (pane) {
            const z = 460 - newO[i - 1].index!;
            pane.style.zIndex = String(z);
          }
        }
      }

      return newO;
    });
  }

  return (
    <WidgetContext.Provider value={{ updateWidget }}>
      {toggledOverlays.map((o) => (
        <Overlay key={`${o.group}.${o.view}`} overlay={o} />
      ))}
      <ActiveOverlayControl>
        {toggledOverlays.map((o) => (
          <OverlayContainer
            key={`${o.group}.${o.view}`}
            group={o.group}
            view={o.view}
            widgets={widgets[o.group]?.[o.view] ?? {}}
            moveUp={moveUp.bind(null, o.index ?? 0)}
            moveDown={moveDown.bind(null, o.index ?? 0)}
          />
        ))}
      </ActiveOverlayControl>
    </WidgetContext.Provider>
  );
}
