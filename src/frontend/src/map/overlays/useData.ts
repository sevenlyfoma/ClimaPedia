import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { OverlayContext } from "./OverlayContext";
import { getBatchTimeData, getData, getPart } from "../../utils/api";
import { GetDataParams, GetPartFn, TimeData } from "../../types/api";
import { DataDefault, applyDefault } from "../../utils/default";
import { DeepRequired } from "ts-essentials";
import { ColourMap, applyColourMap } from "../../utils/colourmap";

// This function wraps all data fetching for overlays in single hook
// Returns Data, and a bound getPart function
export function useData<T, R = unknown>(
  dataDefault?: DataDefault<T>,
  colourMap?: ColourMap<T>,
): {
  data: DeepRequired<T> | null;
  getPart: GetPartFn<R>;
} {
  const { timeData, reloadForBounds, group, view, country } =
    useContext(OverlayContext);
  const [data, setData] = useState<TimeData<T> | null>(null);
  const [currentData, setCurrentData] = useState<DeepRequired<T> | null>(null);

  const params: GetDataParams = useMemo(() => {
    const p: GetDataParams = {};

    // React can't compare objects, so only reference members of reloadForBounds, not the object itself
    if (reloadForBounds?.latMax) {
      p.bounds = {
        latMax: reloadForBounds.latMax,
        latMin: reloadForBounds.latMin,
        longMax: reloadForBounds.longMax,
        longMin: reloadForBounds.longMin,
      };
    }

    if (timeData?.startTime) {
      p.time = {
        start: timeData.startTime,
        end: timeData.endTime,
      };
    }

    if (country !== null) {
      p.country = country;
    }

    return p;
  }, [
    country,
    reloadForBounds?.latMax,
    reloadForBounds?.latMin,
    reloadForBounds?.longMax,
    reloadForBounds?.longMin,
    timeData?.startTime,
    timeData?.endTime,
  ]);

  // Binding the other args of getPart here
  const getPartBound = useCallback(
    (id: string, extra?: Record<string, string>) =>
      getPart<R>(group, view, id, params, extra),
    [group, view, params],
  );

  // Fetching batch or continuous data
  useEffect(() => {
    if (timeData?.batchLoad && timeData.persistent) {
      getBatchTimeData<T>(group, view, params)
        .then((d) => setData(d))
        .catch((e) => {
          throw e;
        });
    } else if (!timeData?.batchLoad) {
      getData<T>(group, view, params)
        .then((d) => setData({ now: d }))
        .catch((e) => {
          throw e;
        });
    }
  }, [group, view, timeData?.batchLoad, timeData?.persistent, params]);

  // Replacing undefined fields with defaults for current data
  // Also map colours for accessibility at render time
  useEffect(() => {
    if (data !== null) {
      const current = data.now ?? data[timeData?.startTime ?? "now"];
      const defaultedData = dataDefault
        ? applyDefault(dataDefault, current)
        : (current as DeepRequired<T>);
      const mappedData = colourMap
        ? applyColourMap(colourMap, defaultedData)
        : defaultedData;
      setCurrentData(mappedData);
    }
  }, [data, dataDefault, timeData?.startTime, colourMap]);

  if (data == null) {
    return { data: null, getPart: getPartBound };
  }

  return {
    data: currentData,
    getPart: getPartBound,
  };
}
