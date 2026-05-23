import { GetDataParams, GroupsManifest, TimeData } from "../types/api";
import { ChartMeta, Focus, RawMapMeta } from "../types/common";
import { API_PATH, TEST } from "./config";

// Fetches the data manifest and parses it from JSON
export function getManifest() {
  if (TEST) {
    return fetch("manifest.json").then((r) => r.json()) as Promise<
      GroupsManifest<Focus>
    >;
  }

  return fetch(`${API_PATH}/groups`).then((r) => r.json()) as Promise<
    GroupsManifest<Focus>
  >;
}

// Send a fetch request with the specified query parameters
function fetchWithParams(
  path: string,
  params?: GetDataParams,
  extra?: Record<string, string>,
) {
  const queryParams: [string, string][] = [];
  const { time, bounds, country } = params ?? {};

  // Adding predefined query parameters
  if (time !== undefined) {
    if (time.end === undefined) {
      queryParams.push(["time", time.start]);
    } else {
      queryParams.push(["starttime", time.start]);
      queryParams.push(["endtime", time.end]);
    }
  }
  if (bounds !== undefined) {
    queryParams.push(["maxlatitude", bounds.latMax.toString()]);
    queryParams.push(["minlongitude", bounds.longMin.toString()]);
    queryParams.push(["minlatitude", bounds.latMin.toString()]);
    queryParams.push(["maxlongitude", bounds.longMax.toString()]);
  }
  if (country !== undefined) {
    queryParams.push(["country", country]);
  }

  // Adding remaining custom query parameters
  if (extra !== undefined) {
    Object.entries(extra).forEach((e) => queryParams.push(e));
  }

  // Formatting params in query
  if (queryParams.length > 0) {
    return fetch(
      `${path}?${queryParams.map(([k, v]) => `${k}=${v}`).join("&")}`,
    );
  } else {
    return fetch(path);
  }
}

// Fetching all time data in a single request
export function getBatchTimeData<T>(
  group: string,
  view: string,
  params?: GetDataParams,
): Promise<TimeData<T>> {
  // Test data
  if (TEST) {
    return fetch("time-points.json").then((r) => r.json()) as Promise<
      TimeData<T>
    >;
  }

  const path = `${API_PATH}/data/${group}/${view}`;
  return fetchWithParams(path, params).then((r) => r.json()) as Promise<
    TimeData<T>
  >;
}

// Fetching the data from the backend
export function getData<T>(
  group: string,
  view: string,
  params?: GetDataParams,
): Promise<T> {
  if (TEST) {
    switch (view) {
      case "clustered-series":
        return fetch("/clustered-series.json").then((r) =>
          r.json(),
        ) as Promise<T>;
      case "clustered":
        return fetch("/clustered.json").then((r) => r.json()) as Promise<T>;
      case "line-time":
        return fetch("/line-time.json").then((r) => r.json()) as Promise<T>;
      case "timeline":
        return fetch("/timeline.json").then((r) => r.json()) as Promise<T>;
      case "scatter":
        return fetch("/scatter.json").then((r) => r.json()) as Promise<T>;
      case "scatter-series":
        return fetch("/scatter-series.json").then((r) =>
          r.json(),
        ) as Promise<T>;
      case "scatter-continuous":
        return fetch("/scatter-continuous.json").then((r) =>
          r.json(),
        ) as Promise<T>;
      case "line":
        return fetch("/line.json").then((r) => r.json()) as Promise<T>;
      case "pie":
        return fetch("/pie.json").then((r) => r.json()) as Promise<T>;
      case "point-heat":
        return fetch("/point-heat.json").then((r) => r.json()) as Promise<T>;
      case "voronoi-heat":
        return fetch("/voronoi-heat.json").then((r) => r.json()) as Promise<T>;
      case "point-tree":
        return fetch("/point-tree-0.json").then((r) => r.json()) as Promise<T>;
      case "series":
        return fetch("/series-points.json").then((r) => r.json()) as Promise<T>;
      case "continuous":
        return fetch("/continuous-points.json").then((r) =>
          r.json(),
        ) as Promise<T>;
      case "time-no-persistent": {
        const { start, end } = params?.time ?? {};
        if (!start || !end) {
          console.error(
            "time-no-persistent requires time params to be defined",
          );
          return Promise.resolve({ coords: [] }) as Promise<T>;
        }

        // Simulating getting data at different time ranges

        let p0 = false;
        let p1 = false;
        if (
          new Date(start).getTime() <= 1698015600000 &&
          new Date(end).getTime() >= 1698015600000
        ) {
          p0 = true;
        }
        if (
          new Date(start).getTime() <= 1698447600000 &&
          new Date(end).getTime() >= 1698447600000
        ) {
          p1 = true;
        }

        if (p0 && !p1) {
          return fetch("time-points-range-0.json").then((d) =>
            d.json(),
          ) as Promise<T>;
        }
        if (!p0 && p1) {
          return fetch("time-points-range-1.json").then((d) =>
            d.json(),
          ) as Promise<T>;
        }
        if (p0 && p1) {
          return fetch("time-points-range-2.json").then((d) =>
            d.json(),
          ) as Promise<T>;
        }
        if (!p0 && !p1) {
          return fetch("time-points-range-3.json").then((d) =>
            d.json(),
          ) as Promise<T>;
        }
        return Promise.resolve({ coords: [] } as T);
      }
      default:
        console.error("Unrecognised test view name", view);
        return Promise.resolve({ coords: [] } as T);
    }
  }

  // Production
  const path = `${API_PATH}/data/${group}/${view}`;
  return fetchWithParams(path, params).then((r) => r.json()) as Promise<T>;
}

// Fetching the view meta data when dynamicMeta is set to true
export function getMetaData<T extends ChartMeta | RawMapMeta>(
  group: string,
  view: string,
) {
  if (TEST) {
    if (view === "time-persistent") {
      return fetch("/time-meta.json").then((r) => r.json()) as Promise<T>;
    } else {
      return Promise.resolve({} as T);
    }
  }

  return fetch(`${API_PATH}/data/${group}/${view}?meta=1`).then((r) =>
    r.json(),
  ) as Promise<T>;
}

// Fetching part data from the backend
export function getPart<T>(
  group: string,
  view: string,
  id: string,
  params?: GetDataParams,
  extra?: Record<string, string>,
): Promise<T | null> {
  if (TEST) {
    switch (view) {
      case "clustered":
        if (!isNaN(+id)) {
          return fetch("/points-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "time-no-persistent":
        if (!isNaN(+id)) {
          return fetch("/points-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "time-persistent":
        if (id === "0") {
          return fetch("/points-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "1") {
          return fetch("/points-part-1.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "2") {
          return fetch("/points-part-2.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "3") {
          return fetch("/points-part-3.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "scatter-continuous":
        if (id === "0") {
          return fetch("/scatter-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "1") {
          return fetch("/scatter-part-1.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "2") {
          return fetch("/scatter-part-2.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "3") {
          return fetch("/scatter-part-3.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "pie":
        if (id === "0") {
          return fetch("/pie-part-0.json").then((r) => r.json()) as Promise<T>;
        }
        if (id === "1") {
          return fetch("/pie-part-1.json").then((r) => r.json()) as Promise<T>;
        }
        if (id === "2") {
          return fetch("/pie-part-2.json").then((r) => r.json()) as Promise<T>;
        }

        return Promise.resolve(null);
      case "point-tree":
        if (id === "1" && extra?.info !== "1") {
          return fetch("/point-tree-1.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "2" && extra?.info !== "1") {
          return fetch("/point-tree-2.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "3" && extra?.info !== "1") {
          return fetch("/point-tree-3.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "4" && extra?.info === "1") {
          return fetch("/point-tree-4.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "voronoi-heat":
        if (id === "0") {
          return fetch("/voronoi-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "1") {
          return fetch("/voronoi-part-1.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "2") {
          return fetch("/voronoi-part-2.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      case "continuous":
        if (id === "0") {
          return fetch("/points-part-0.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "1") {
          return fetch("/points-part-1.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "2") {
          return fetch("/points-part-2.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "3") {
          return fetch("/points-part-3.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }
        if (id === "4") {
          return fetch("/points-part-4.json").then((r) =>
            r.json(),
          ) as Promise<T>;
        }

        return Promise.resolve(null);
      default:
        return Promise.resolve(null);
    }
  }

  const path = `${API_PATH}/data/${group}/${view}/${id}`;
  return fetchWithParams(path, params, extra).then((r) =>
    r.json(),
  ) as Promise<T>;
}
