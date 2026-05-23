import { ReactNode, useContext } from "react";
import { TimelineInfo, TimelineType } from "../../types/timeline";
import { ManifestContext } from "../../common/contexts/ManifestContext";
import { LayeredTimeline } from "./LayeredTimeline";
import { TimelineContext, TimelineContextProps } from "./TimelineContext";
import useWidgets from "../../map/widgets/useWidgets";

interface TimelineProps {
  timelineInfo: TimelineInfo;
}

const components: Record<TimelineType, ReactNode> = {
  layeredTimeline: <LayeredTimeline />,
};

export function Timeline({ timelineInfo }: TimelineProps) {
  const manifest = useContext(ManifestContext);
  const timelineType = manifest[timelineInfo.group].views[timelineInfo.view]
    .type as TimelineType;
  const { updateWidget } = useWidgets(timelineInfo.group, timelineInfo.view);

  const contextValue: TimelineContextProps = {
    group: timelineInfo.group,
    view: timelineInfo.view,
    updateWidget,
  };

  return (
    <TimelineContext.Provider value={contextValue}>
      {components[timelineType]}
    </TimelineContext.Provider>
  );
}
