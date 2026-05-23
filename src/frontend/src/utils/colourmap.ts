import { DeepRequired } from "ts-essentials";
import _ from "lodash";
import {
  ChartLineData,
  ChartPieData,
  ChartScatterData,
  MapPointTreeData,
  MapPointsData,
  MapVoronoiHeatData,
  TimelineLayeredTimelineData,
} from "../types/api";
import { mappedColour } from "./colour";

type ColourMap<T> = (data: DeepRequired<T>) => DeepRequired<T>;

// Applys a colour mapping to defaulted data
function applyColourMap<T>(
  colourMap: ColourMap<T>,
  data: DeepRequired<T>,
): DeepRequired<T> {
  // throw new Error("temporary");
  return colourMap(data);
}

// Colour mapping for map-points
const colourMapPointsData: ColourMap<MapPointsData> = (data) => {
  data = _.cloneDeep(data);

  data.seriesLegend?.map((s) => {
    s.colour = mappedColour(s.colour);
  });
  if (data.valuesLegend)
    data.valuesLegend.colourRange =
      data.valuesLegend.colourRange.map(mappedColour);
  data.defaultColour = mappedColour(data.defaultColour);

  return data;
};

// Colour mapping for map-voronoi-heat
const colourMapVoronoiHeat: ColourMap<MapVoronoiHeatData> = (data) => {
  data = _.cloneDeep(data);

  if (data.valuesLegend)
    data.valuesLegend.colourRange =
      data.valuesLegend.colourRange.map(mappedColour);

  return data;
};

// Colour mapping for map-point-tree
const colourMapPointTreeData: ColourMap<MapPointTreeData> = (data) => {
  data = _.cloneDeep(data);

  data.seriesLegend?.map((s) => {
    s.colour = mappedColour(s.colour);
  });
  if (data.valuesLegend)
    data.valuesLegend.colourRange =
      data.valuesLegend.colourRange.map(mappedColour);
  data.defaultColour = mappedColour(data.defaultColour);

  return data;
};

// Colour mapping for chart-pie
const colourChartPieData: ColourMap<ChartPieData> = (data) => {
  data = _.cloneDeep(data);

  data.data.map((d) => {
    d.defaultColour = mappedColour(d.defaultColour);
  });

  return data;
};

// Colour mapping for chart-line
const colourChartLineData: ColourMap<ChartLineData> = (data) => {
  data = _.cloneDeep(data);

  data.styles.map((s) => {
    s.colour = mappedColour(s.colour);
  });

  return data;
};

// Colour mapping for chart-scatter
const colourChartScatterData: ColourMap<ChartScatterData> = (data) => {
  data = _.cloneDeep(data);

  data.seriesLegend?.map((s) => {
    s.colour = mappedColour(s.colour);
  });
  if (data.valuesLegend)
    data.valuesLegend.colourRange =
      data.valuesLegend.colourRange.map(mappedColour);
  data.defaultColour = mappedColour(data.defaultColour);

  return data;
};

// Colour mapping for timeline
const colourTimelineData: ColourMap<TimelineLayeredTimelineData> = (data) => {
  data = _.cloneDeep(data);

  data.entries?.map((e) => {
    e.defaultColour = mappedColour(e.defaultColour);
    e.subentries.map((se) => {
      se.defaultColour = mappedColour(se.defaultColour);
    });
  });

  return data;
};

export {
  applyColourMap,
  colourMapVoronoiHeat,
  colourMapPointsData,
  colourMapPointTreeData,
  colourChartPieData,
  colourChartLineData,
  colourChartScatterData,
  colourTimelineData,
};

export type { ColourMap };
