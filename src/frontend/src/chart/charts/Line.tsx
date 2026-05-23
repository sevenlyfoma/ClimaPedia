import Plot from "react-plotly.js";
import { defaultChartLineData } from "../../utils/default";
import { useData } from "./useData";
import { useContext, useMemo } from "react";
import { ChartContext } from "./ChartContext";
import { AxisType } from "plotly.js";
import { Loading } from "./Loading";
import { useManifest } from "../../common/hooks/useManifest";
import { colourChartLineData } from "../../utils/colourmap";

// Chart + Line visualisation
export function Line() {
  const { data } = useData(defaultChartLineData, colourChartLineData);
  const { view, group, staticChart = false } = useContext(ChartContext);
  const manifest = useManifest("chart");

  interface LineData {
    x: (number | string)[];
    y: (number | string)[];
    type: "scatter";
    mode: "lines" | "lines+markers";
    name: string;
    line: {
      color: string;
      width: number;
      dash: "dot" | "solid" | "dash";
      shape: "linear" | "spline" | "hv" | "vh" | "hvh" | "vhv";
    };
  }

  // Formatting data to be read by plotly
  const formatted =
    data?.lines.map<LineData>((l, i) => ({
      x: l.map(([x]) => x),
      y: l.map(([, y]) => y),
      type: "scatter",
      mode: data.styles[i].showMarkers ? "lines+markers" : "lines",
      name: data.labels[i],
      line: {
        color: data.styles[i].colour,
        dash: data.styles[i].line,
        width: data.styles[i].width,
        shape: data.styles[i].shape,
      },
    })) ?? null;

  // Formatting data to pass to chart layout
  // Layout for static (when shown in preview) and interactive
  const layout = useMemo(
    () =>
      data == null
        ? null
        : staticChart
          ? {
              autosize: true,
              width: 200,
              height: 200,
              showlegend: false,
              margin: {
                t: 0,
                b: 0,
                l: 0,
                r: 0,
              },
              plot_bgcolor: "rgba(0,0,0,0)",
              paper_bgcolor: "rgba(0,0,0,0)",
            }
          : {
              title: data.title ?? manifest[group].views[view].name,
              xaxis: {
                title: data.xAxis.title,
                type: (data.xAxis.type ?? "-") as AxisType,
              },
              yaxis: {
                title: data.yAxis.title,
                type: (data.yAxis.type ?? "-") as AxisType,
              },
              plot_bgcolor: "rgba(0,0,0,0)",
              paper_bgcolor: "rgba(0,0,0,0)",
            },
    [data, view, staticChart, group, manifest],
  );

  if (formatted == null || layout == null) {
    return staticChart ? <Loading /> : null;
  }

  return (
    <Plot
      data={formatted}
      layout={layout}
      config={{ staticPlot: staticChart }}
    />
  );
}
