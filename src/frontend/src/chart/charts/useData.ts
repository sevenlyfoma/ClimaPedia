// This function wraps all data fetching for overlays in single hook

import { useContext, useState, useEffect, useCallback } from "react";
import { DeepRequired } from "ts-essentials";
import { getData, getPart } from "../../utils/api";
import { DataDefault, applyDefault } from "../../utils/default";
import { ChartContext } from "./ChartContext";
import { ColourMap, applyColourMap } from "../../utils/colourmap";
import { GetPartFn } from "../../types/api";

// Returns Data, and a bound getPart function
export function useData<T, R = unknown>(
  dataDefault: DataDefault<T>,
  colourMap: ColourMap<T>,
): {
  data: DeepRequired<T> | null;
  getPart: GetPartFn<R>;
} {
  const { group, view } = useContext(ChartContext);
  const [data, setData] = useState<DeepRequired<T> | null>(null);

  const getPartBound = useCallback(
    (id: string, extra?: Record<string, string>) =>
      getPart<R>(group, view, id, {}, extra),
    [group, view],
  );

  // Fetching data
  useEffect(() => {
    getData<T>(group, view)
      .then((d) =>
        setData(applyColourMap(colourMap, applyDefault(dataDefault, d))),
      )
      .catch((e) => console.error("Failed to fetch data", e));
  }, [group, view, dataDefault, colourMap]);

  if (data == null) {
    return { data: null, getPart: () => Promise.resolve(null) };
  }

  return {
    data,
    getPart: getPartBound,
  };
}
