import Legend from "../common/Legend/Legend";
import "./Timeline.css";
import { useToggledParams } from "../common/hooks/useQueryParams";
import { useManifest } from "../common/hooks/useManifest";

import ToggledTimelines from "./ToggledTimeline";

export function TimelinePage() {
  const manifest = useManifest("timeline");
  const [toggled, setToggled] = useToggledParams(manifest, false);

  const flexToggled = toggled === null ? [] : [toggled];
  return (
    <>
      <Legend
        manifest={manifest}
        multiple={false}
        toggledView={toggled}
        setToggledView={setToggled}
      />

      <ToggledTimelines toggledTimelines={flexToggled} />
    </>
  );
}
