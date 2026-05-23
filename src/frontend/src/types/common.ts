import { DeepRequired } from "ts-essentials";
import { ChartType } from "./chart";
import { MapType } from "./map";
import { TimelineType } from "./timeline";

export type Focus = "map" | "chart" | "timeline";

// Base class for point-related visualisations
export interface BasePointData {
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
  defaultColour?: string;
  shapes?: string[];
  clickable?: boolean;
}

export interface TimeMetaData {
  times: string[];
  defaultStartTime?: string;
  defaultEndTime?: string;
  period?: {
    unit: string;
    value?: number;
  };
  range?: [string, string];
  batchLoad?: boolean;
  persistent?: boolean;
  partRefetch?: boolean;
  fetchDelay?: number;
}

export interface InteractiveTimeMetaData extends DeepRequired<TimeMetaData> {
  startTime: string;
  endTime?: string;
  setTime: (start: string, end?: string) => void;
}

export interface RawMapMeta {
  dynamicMeta?: boolean;
  timeData?: TimeMetaData;
  reloadForBounds?: boolean;
  viewCountries?: string[];
}

export interface MapMeta {
  dynamicMeta: boolean;
  timeData: Required<TimeMetaData> | null;
  reloadForBounds: boolean;
  viewCountries: string[];
}

export interface RawChartMeta {
  dynamicMeta?: boolean;
}

export interface ChartMeta {
  dynamicMeta: boolean;
}

export type View<F extends Focus> = F extends "map"
  ? MapView
  : F extends "timeline"
    ? TimelineView
    : ChartView;
export interface MapView {
  name: string;
  description?: string;
  focus: "map";
  type: MapType;
  version?: number;
  meta?: RawMapMeta;
}

export interface ChartView {
  name: string;
  description?: string;
  focus: "chart";
  type: ChartType;
  version?: number;
  meta?: RawChartMeta;
}

export interface ViewInfo {
  group: string;
  view: string;
  index?: number;
}

export interface Group<F extends Focus> {
  name: string;
  views: Record<string, View<F>>;
}

export interface Series {
  name: string;
  colour?: string;
  shape?: string;
}
export interface ContinuousLegend {
  valueRange: [number, number];
  colourRange?: string[];
  unit?: string;
  ticks?: number;
}

export interface InteractiveSeries extends Series {
  active: boolean;
}

export interface Bounds {
  latMin: number;
  latMax: number;
  longMin: number;
  longMax: number;
}

export interface CustomWidget {
  title: string;
  markup: string;
  size: 0 | 1;
}

export interface ChartEntry {
  label: string;
  id: string;
  value: number;
  defaultColour?: string;
}

export interface TimeLineSubentry {
  label: string;
  id: string;
  point: string;
  defaultColour?: string;
}

export interface TimelineEntry {
  label: string;
  id: string;
  range: [string, string];
  subentries: TimeLineSubentry[];
  defaultColour?: string;
}

// timelines

export interface RawTimelineMeta {
  dynamicMeta?: boolean;
}

export interface TimelineView {
  name: string;
  description: string;
  focus: "timeline";
  type: TimelineType;
  version?: number;
  meta?: RawTimelineMeta;
}
