import { useCallback, useEffect, useState } from "react";
import { OverlayWidgetData } from "../types/map"; // same for timelines
import ActiveOverlayControl from "../map/active-control";
import OverlayContainer from "../map/active-control/OverlayContainer";
import { Timeline } from "./timelines";
import _ from "lodash";
import { WidgetContext } from "../map/widgets/useWidgets";
import { ViewInfo } from "../types/common";

// group -> view -> widgetId -> widgetData
type TimelineWidgetDataCollection = Record<
  string,
  Record<string, Record<string, OverlayWidgetData>>
>;

export interface ToggledTimelineProps {
  toggledTimelines: ViewInfo[];
}

// Render toggled timeline
//  and display the toggled overlays in a control in the corner
export default function ToggledTimelines({
  toggledTimelines,
}: ToggledTimelineProps) {
  const [widgets, setWidget] = useState<TimelineWidgetDataCollection>({});

  // Updating stored widgets on overlays changes
  useEffect(() => {
    setWidget((w) => {
      const newW = _.cloneDeep(w);

      return _.pick(
        newW,
        toggledTimelines.map((o) => [o.group, o.view]),
      ) as TimelineWidgetDataCollection;
    });
  }, [toggledTimelines]);

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

  return (
    <WidgetContext.Provider value={{ updateWidget }}>
      <div style={{ overflow: "auto" }}>
        {toggledTimelines.map((o) => (
          <Timeline key={`${o.group}.${o.view}`} timelineInfo={o} />
        ))}
        <ActiveOverlayControl topPadding={62}>
          {toggledTimelines.map((o) => (
            <OverlayContainer
              key={`${o.group}.${o.view}`}
              group={o.group}
              view={o.view}
              widgets={widgets[o.group]?.[o.view] ?? {}}
            />
          ))}
        </ActiveOverlayControl>
      </div>
    </WidgetContext.Provider>
  );
}

//style="position:fixed; top:64px"
