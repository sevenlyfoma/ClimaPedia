import { AxisType, PlotDatum } from "plotly.js";
import { useContext, useMemo, useState } from "react";
import Plot from "react-plotly.js";
import { defaultChartScatterData } from "../../utils/default";
import { ChartContext } from "./ChartContext";
import { useData } from "./useData";
import { normalise } from "../../utils/common";
import { ChartScatterData, PartData } from "../../types/api";
import { InfoBox, InfoBoxProps } from "./InfoBox";
import _ from "lodash";
import { getContinuousColour } from "../../utils/colour";
import { Loading } from "./Loading";
import { useManifest } from "../../common/hooks/useManifest";
import { colourChartScatterData } from "../../utils/colourmap";

interface IdInfoBoxProps extends InfoBoxProps {
  id: number;
}

// Chart + Scatter visualisation
export function Scatter() {
  const { data, getPart } = useData<ChartScatterData, PartData>(
    defaultChartScatterData,
    colourChartScatterData,
  );
  const { view, group, staticChart = false } = useContext(ChartContext);
  const manifest = useManifest("chart");

  const [infos, setInfos] = useState<IdInfoBoxProps[]>([]);

  interface ScatterDatum extends PlotDatum {
    bbox: {
      x0: number;
      x1: number;
      y0: number;
      y1: number;
    };
  }

  async function handleClick(d: Plotly.PlotMouseEvent) {
    if (d.points.length !== 1 || data == null) {
      return;
    }

    const point = d.points[0] as ScatterDatum;

    // Get the part data
    const id =
      (point.data as unknown as { pointId: string }).pointId ??
      data.ids[point.pointIndex];
    const partReq = getPart(id);

    // Placing the toggled infoboxes just surrounding the pie chart with the power of maths
    const width = 250;
    const height = 250;

    const x = point.bbox.x0 + (point.bbox.x1 - point.bbox.x0) / 2 - width / 2;
    const y = point.bbox.y1 + 10;

    const partData = await partReq;
    if (partData?.widget == null) {
      return partData;
    }

    setInfos((s) => {
      const newS = _.cloneDeep(s);
      if (newS.find((f) => f.id === point.pointNumber) !== undefined) {
        const i = newS.findIndex((f) => f?.id === point.pointNumber);
        if (i === -1) {
          return s;
        }
        newS.splice(i, 1);
      } else {
        newS.push({
          id: point.pointNumber,
          x,
          y,
          width,
          height,
          name: partData.widget.title,
          colour: data.seriesLegend
            ? data.seriesLegend[data.series![point.pointIndex]].colour
            : data.valuesLegend
              ? getContinuousColour(
                  data.values![point.pointIndex],
                  data.valuesLegend.valueRange,
                  data.valuesLegend.colourRange,
                )
              : data.defaultColour,
          onDrag: () =>
            setInfos((ss) => {
              const newSS = _.cloneDeep(ss);
              newSS.push(
                newSS.splice(
                  newSS.findIndex((f) => f.id === point.pointNumber),
                  1,
                )[0],
              );
              return newSS;
            }),
          onClose: () =>
            setInfos((s) => {
              const newS = _.cloneDeep(s);
              const i = newS.findIndex((f) => f?.id === point.pointNumber);
              if (i === -1) {
                return s;
              }
              newS.splice(i, 1);
              return newS;
            }),
          html: partData.widget.markup,
        });
      }
      return newS;
    });
  }

  interface ScatterData {
    x: (number | string)[];
    y: (number | string)[];
    text?: string[];
    type: "scatter";
    mode: "markers";
    name: string;
    marker: {
      size: number[];
      color?: number[] | string;
      colorscale?: [number, string][];
      showscale?: boolean;
      cmin?: number;
      cmax?: number;
      colorbar?: {
        nticks?: number;
        ticksuffix?: string;
      };
    };
    pointId?: string;
  }

  // Formatting data to be read by plotly
  const formatted =
    useMemo<ScatterData[]>(() => {
      if (data?.seriesLegend) {
        return Object.values(
          data.coords.reduce<Record<string, ScatterData>>((acc, red, i) => {
            if (acc[data.series![i]] == undefined) {
              acc[data.series![i]] = {
                x: [],
                y: [],
                text: [],
                type: "scatter",
                mode: "markers",
                name: data.seriesLegend![data.series![i]].name,
                marker: {
                  size: [],
                  color: data.seriesLegend![i].colour,
                },
                pointId: data.ids[i],
              };
            }
            acc[data.series![i]].x.push(red[0]);
            acc[data.series![i]].y.push(red[1]);
            data.labels && acc[data.series![i]].text!.push(data.labels[i]);
            acc[data.series![i]].marker.size.push(
              normalise(data.sizes[i], data.sizeRange) * 150 + 6,
            );

            return acc;
          }, {}),
        );
      } else if (data?.valuesLegend) {
        const leg = data.valuesLegend;

        return [
          {
            x: data.coords.map(([x]) => x),
            y: data.coords.map(([, y]) => y),
            text: data.labels ?? undefined,
            type: "scatter",
            mode: "markers",
            name: "data",
            marker: {
              size: data.sizes.map((s) =>
                Math.round(normalise(s, data.sizeRange) * 150 + 6),
              ),
              color: data.values ?? undefined,
              colorscale: data.valuesLegend.colourRange.map((c, i) => [
                normalise(
                  ((leg.valueRange[1] - leg.valueRange[0]) /
                    (leg.colourRange.length - 1)) *
                    i +
                    leg.valueRange[0],
                  leg.valueRange,
                ),
                c,
              ]),
              cmin: leg.valueRange[0],
              cmax: leg.valueRange[1],
              showscale: !staticChart,
              colorbar: {
                nticks: data.valuesLegend.ticks,
                ticksuffix: data.valuesLegend.unit,
              },
            },
          },
        ];
      } else if (data != null) {
        return [
          {
            x: data.coords.map(([x]) => x) ?? [],
            y: data.coords.map(([, y]) => y) ?? [],
            text: data.labels ?? undefined,
            type: "scatter",
            mode: "markers",
            name: "data",
            marker: {
              size: data.sizes.map((s) =>
                Math.round(normalise(s, data.sizeRange) * 150 + 6),
              ),
              color: data?.defaultColour,
            },
          },
        ];
      } else {
        return [];
      }
    }, [data, staticChart]) ?? null;

  // Formatting data to pass to chart layout
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

  if (formatted == null || layout == null || data == null) {
    return staticChart ? <Loading /> : null;
  }

  return (
    <>
      {infos.map((s) => (
        <InfoBox {...s} key={s.id} />
      ))}
      <Plot
        data={formatted}
        layout={layout}
        onClick={data.clickable ? handleClick : undefined}
        config={{ staticPlot: staticChart }}
      />
    </>
  );
}
