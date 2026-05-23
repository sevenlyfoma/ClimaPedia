import chroma from "chroma-js";
import {
  ChartLineData,
  ChartPieData,
  ChartScatterData,
  TimelineLayeredTimelineData,
  MapPointTreeData,
  MapPointsData,
  MapVoronoiHeatData,
} from "../types/api";
import { DeepRequired } from "ts-essentials";
import _ from "lodash";

// The default object for various types
type DataDefault<T> = (data: T) => DeepRequired<T>;

// Default Colour range
const colourRange = ["#000", "#fff"];

// For Map + Point data
const defaultMapPointsData: DataDefault<MapPointsData> = (data) => ({
  coords: data.coords,
  ids: data.coords.map((_, i) => i.toString()),
  series: null,
  seriesLegend:
    data.seriesLegend?.map((s, i, sx) => ({
      name: s.name,
      colour: chroma.scale(colourRange).domain([0, sx.length])(i).hex(),
      shape: "circle",
    })) ?? null,
  values: null,
  valuesLegend: data.valuesLegend
    ? {
        valueRange: data.valuesLegend.valueRange,
        colourRange: colourRange,
        ticks: 3,
        unit: "",
      }
    : null,
  labels: null,
  labelsOnHover: true,
  sizes: data.coords.map(() => 0),
  sizeRange: [0, 1],
  clustering: false,
  defaultColour: "#000",
  clickable: false,
  shapes: data.coords.map(() => "circle"),
});

// For Map + voronoi data
const defaultMapVoronoiHeatData: DataDefault<MapVoronoiHeatData> = (data) => ({
  polygons: data.polygons,
  ids: data.ids,
  values: null,
  valuesLegend: data.valuesLegend
    ? {
        valueRange: data.valuesLegend.valueRange,
        colourRange: colourRange,
        ticks: 3,
        unit: "",
      }
    : null,
  heatStyle: {
    opacity: 0.2,
    edgeOpacity: 0.5,
    edgeColour: null,
    edgeThickness: 2,
  },
  clickable: false,
});

// For Map + PointTree data
const defaultMapPointTreeData: DataDefault<MapPointTreeData> = (data) => ({
  coords: data.coords,
  ids: data.coords.map((_, i) => i.toString()),
  series: null,
  seriesLegend:
    data.seriesLegend?.map((s, i, sx) => ({
      name: s.name,
      colour: chroma.scale(colourRange).domain([0, sx.length])(i).hex(),
      shape: "circle",
    })) ?? null,
  values: null,
  valuesLegend: data.valuesLegend
    ? {
        valueRange: data.valuesLegend.valueRange,
        colourRange: colourRange,
        ticks: 3,
        unit: "",
      }
    : null,
  labels: null,
  labelsOnHover: true,
  sizes: data.coords.map(() => 0),
  sizeRange: [0, 1],
  defaultColour: "#000",
  edgeThicknesses: [],
  shapes: data.coords.map(() => "circle"),
  clickable: true,
});

// For Chart + Pie data
const defaultChartPieData: DataDefault<ChartPieData> = (data) => ({
  data: data.data.map((d, i, dx) => ({
    label: d.label,
    value: d.value,
    id: d.id,
    defaultColour: chroma.scale(colourRange).domain([0, dx.length])(i).hex(),
  })),
  clickable: false,
  hover: {
    showLabel: false,
    showPercent: true,
    showValue: false,
    unit: "",
  },
  title: null,
});

// For Timeline + LayeredTimeline
const defaultTimelineData: DataDefault<TimelineLayeredTimelineData> = (
  data,
) => ({
  entries: data.entries.map((d, i, dx) => ({
    label: d.label,
    id: d.id,
    range: d.range,
    subentries: d.subentries.map((d, i, dx) => ({
      label: d.label,
      id: d.id,
      point: d.point,
      defaultColour: chroma.scale(colourRange).domain([0, dx.length])(i).hex(),
    })),
    defaultColour: chroma.scale(colourRange).domain([0, dx.length])(i).hex(),
  })),
  clickable: false,
  range: data.range,
});

// For Chart + Line data
const defaultChartLineData: DataDefault<ChartLineData> = (data) => ({
  lines: data.lines,
  ids: data.ids,
  labels: data.lines.map(() => ""),
  styles: data.lines.map((_d, i, dx) => ({
    colour: chroma.scale(colourRange).domain([0, dx.length])(i).hex(),
    line: "solid",
    width: 1,
    showMarkers: false,
    shape: "linear",
  })),
  clickable: true,
  xAxis: {
    title: "",
    type: null,
  },
  yAxis: {
    title: "",
    type: null,
  },
  title: null,
});

// For Chart + Scatter data
const defaultChartScatterData: DataDefault<ChartScatterData> = (data) => ({
  coords: data.coords,
  ids: data.coords.map((_c, i) => i.toString()),
  series: null,
  seriesLegend:
    data.seriesLegend?.map((s, i, sx) => ({
      name: s.name,
      colour: chroma.scale(colourRange).domain([0, sx.length])(i).hex(),
      shape: "circle",
    })) ?? null,
  values: null,
  valuesLegend: data.valuesLegend
    ? {
        valueRange: data.valuesLegend.valueRange,
        colourRange: colourRange,
        ticks: 3,
        unit: "",
      }
    : null,
  labels: null,
  sizes: data.coords.map(() => 0.05),
  sizeRange: [0, 1],
  defaultColour: "#000",
  clickable: false,
  xAxis: {
    title: "",
    type: null,
  },
  yAxis: {
    title: "",
    type: null,
  },
  title: null,
});

// Apply defaults to data fields if they are left undefined
function applyDefault<T>(
  dataDefault: DataDefault<T>,
  data: T,
): DeepRequired<T> {
  return _.merge(dataDefault(data), data);
}

export {
  defaultMapPointsData,
  defaultMapVoronoiHeatData,
  defaultMapPointTreeData,
  defaultChartPieData,
  defaultChartLineData,
  defaultChartScatterData,
  defaultTimelineData,
  applyDefault,
};

export type { DataDefault };
