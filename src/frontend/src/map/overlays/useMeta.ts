import { useEffect, useMemo, useState } from "react";
import { MapMeta, RawMapMeta } from "../../types/common";
import { getMetaData } from "../../utils/api";
import _ from "lodash";
import { GroupsManifest } from "../../types/api";
import { getMaxTime, getMinTime, getTimeRange } from "../../utils/time";

// Defines all the defaults of the meta
const fillMeta = ({
  dynamicMeta = false,
  timeData: {
    times,
    range = getTimeRange(times),
    period = {
      unit: "data",
      value: 1,
    },
    persistent = true,
    batchLoad = false,
    partRefetch = false,
    fetchDelay = 500,
    defaultStartTime = persistent ? getMaxTime(times) : getMinTime(times),
    defaultEndTime = getMaxTime(times),
  } = { times: [] },
  reloadForBounds = false,
  viewCountries = [],
}: RawMapMeta): MapMeta => ({
  dynamicMeta,
  timeData:
    times.length > 0
      ? {
          times,
          defaultStartTime,
          defaultEndTime,
          range,
          period,
          persistent,
          batchLoad,
          partRefetch,
          fetchDelay,
        }
      : null,
  reloadForBounds,
  viewCountries,
});

// Returning the final meta of an overlay
export default function useMeta(
  group: string,
  view: string,
  manifest: GroupsManifest<"map">,
): MapMeta | null {
  // Static and dynamic meta
  // We save dynamic meta so that we don't refetch
  const staticMeta = useMemo(
    () => manifest[group].views[view].meta ?? {},
    [manifest, group, view],
  );
  const [dynamicMeta, setDynamicMeta] = useState<RawMapMeta | null>(null);

  const [meta, setMeta] = useState<MapMeta | null>(
    staticMeta.dynamicMeta ? null : fillMeta(staticMeta),
  );

  // Update dynamic meta if relevant
  useEffect(() => {
    if (staticMeta.dynamicMeta) {
      // Reset meta
      setDynamicMeta(null);
      setMeta(null);

      // Fetch dynamic meta
      getMetaData(group, view)
        .then((m) => {
          setDynamicMeta(m);
        })
        .catch((e) => console.error(e));
    }
  }, [group, view, staticMeta]);

  // Update final meta data
  useEffect(() => {
    // Either merge static with dynamic, update static, or don't update
    if (staticMeta.dynamicMeta && dynamicMeta !== null) {
      const newMeta = _.cloneDeep(staticMeta);
      _.merge(newMeta, dynamicMeta);
      setMeta(fillMeta(newMeta));
    } else if (!staticMeta.dynamicMeta) {
      setMeta(fillMeta(staticMeta));
    }
  }, [dynamicMeta, staticMeta]);

  return meta;
}
