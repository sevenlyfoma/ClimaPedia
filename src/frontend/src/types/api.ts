// Includes types for all the backend api calls

import {
  BasePointData,
  Bounds,
  ChartEntry,
  ContinuousLegend,
  CustomWidget,
  Focus,
  Group,
  Series,
  TimelineEntry,
} from "./common";

// Manifest Protocol
export type GroupsManifest<F extends Focus> = Record<string, Group<F>>;

// Data Protocol

// Generic batch time data
export type TimeData<T> = Record<string, T>;

export type GetPartFn<T> = (
  id: string,
  extra?: Record<string, string>,
) => Promise<T | null>;

// Query params that can be passed to data endpoint
export interface GetDataParams {
  bounds?: Bounds;
  time?: {
    start: string;
    end?: string;
  };
  country?: string;
}

// Generic Part Data
export interface PartData {
  widget: CustomWidget;
}

// For Map + Point data
export interface MapPointsData extends BasePointData {
  coords: [number, number][];
  ids?: string[];
  series?: number[] | null;
  seriesLegend?: Series[] | null;
  values?: number[] | null;
  valuesLegend?: ContinuousLegend | null;
  labels?: string[] | null;
  labelsOnHover?: boolean;
  sizes?: number[];
  sizeRange?: [number, number];
  clustering?: boolean;
  defaultColour?: string;
  clickable?: boolean;
  shapes?: string[];
}

// For Map + Point-Heat
export interface MapPointHeatData {
  coords: [number, number][];
  ids?: string[];
  values: number[];
  valuesLegend: ContinuousLegend;
  heatStyle?: {
    radius?: number;
    blur?: number;
    minOpacity?: number;
    maxZoom?: number;
  };
}

// For Map + Voronoi-Heat
export interface MapVoronoiHeatData {
  polygons: [number, number][][];
  ids: string[];
  values?: number[] | null;
  valuesLegend?: ContinuousLegend | null;
  heatStyle?: {
    opacity?: number;
    edgeOpacity?: number;
    edgeColour?: string | null;
    edgeThickness?: number;
  };
  clickable?: boolean;
}

// For Map + Point-Tree
export interface MapPointTreeData extends BasePointData {
  coords: [number, number][];
  ids: string[];
  series?: number[] | null;
  seriesLegend?: Series[] | null;
  values?: number[] | null;
  valuesLegend?: ContinuousLegend | null;
  labels?: string[] | null;
  labelsOnHover?: boolean;
  sizes?: number[];
  sizeRange?: [number, number];
  defaultColour?: string;
  edgeThicknesses?: number[];
  shapes?: string[];
}

// --- Chart Types ---

// For Chart + Pie
export interface ChartPieData {
  data: ChartEntry[];
  clickable?: boolean;
  hover?: {
    showValue?: boolean;
    showPercent?: boolean;
    showLabel?: boolean;
    unit?: string;
  };
  title?: string | null;
}

// For Chart + Line
export interface ChartLineData {
  lines: [number | string, number | string][][];
  ids: string[];
  labels?: string[];
  styles?: {
    colour?: string;
    line?: "solid" | "dash" | "dot";
    width?: number;
    showMarkers?: boolean;
    shape?: "linear" | "spline" | "hv" | "vh" | "hvh" | "vhv";
  }[];
  clickable?: boolean;
  xAxis?: {
    title: string;
    type?: "linear" | "log" | null;
  };
  yAxis?: {
    title: string;
    type?: "linear" | "log" | null;
  };
  title?: string | null;
}

// For Chart + Scatter
export interface ChartScatterData {
  coords: [number | string, number | string][];
  ids?: string[];
  series?: number[] | null;
  seriesLegend?: Series[] | null;
  values?: number[] | null;
  valuesLegend?: ContinuousLegend | null;
  labels?: string[] | null;
  sizes?: number[];
  sizeRange?: [number, number];
  defaultColour?: string;
  clickable: boolean;
  xAxis?: {
    title: string;
    type?: "linear" | "log" | null;
  };
  yAxis?: {
    title: string;
    type?: "linear" | "log" | null;
  };
  title?: string | null;
}

// Timeline types

// For Timeline + LayeredTimeline
export interface TimelineLayeredTimelineData {
  entries: TimelineEntry[];
  range: [string, string];
  clickable?: boolean;
}
