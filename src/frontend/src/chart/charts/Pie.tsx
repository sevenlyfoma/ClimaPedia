import Plot from "react-plotly.js";
import { defaultChartPieData } from "../../utils/default";
import { useData } from "./useData";
import { useContext, useMemo, useState } from "react";
import { InfoBox, InfoBoxProps } from "./InfoBox";
import _ from "lodash";
import { PlotDatum } from "plotly.js";
import { ChartPieData, PartData } from "../../types/api";
import { ChartContext } from "./ChartContext";
import { Loading } from "./Loading";
import { useManifest } from "../../common/hooks/useManifest";
import { colourChartPieData } from "../../utils/colourmap";

interface PieDatum extends PlotDatum {
  label: string;
  color: string;
}

interface IdInfoBoxProps extends InfoBoxProps {
  id: number;
}

// Chart + Pie visualisation
export function Pie() {
  const { data, getPart } = useData<ChartPieData, PartData>(
    defaultChartPieData,
    colourChartPieData,
  );
  const { group, view, staticChart = false } = useContext(ChartContext);
  const manifest = useManifest("chart");

  const [infos, setInfos] = useState<IdInfoBoxProps[]>([]);

  async function handleClick(d: Plotly.PlotMouseEvent) {
    if (d.points.length !== 1 || data == null) {
      return;
    }

    const point = d.points[0] as PieDatum;

    // Get the part data
    const partReq = getPart(data.data?.[point.pointNumber].id);

    // Placing the toggled infoboxes just surrounding the pie chart with the power of maths
    const width = 250;
    const height = 250;

    // Determining angle of infobox
    const total = data.data.reduce((acc, red) => acc + red.value, 0);
    let prog = (point.data.values[point.pointNumber] as number) / total / 2;
    for (let i = 0; i < point.pointNumber; i++) {
      prog += (point.data.values[i] as number) / total;
    }

    const angle = prog * 2 * Math.PI;
    const bounds = (
      d.event.target as Node
    ).parentElement!.parentElement!.getBoundingClientRect();
    const disp = bounds.height / 2 + width * 0.75;

    // Getting exact x and y coords of new infobox pos based on segment angle
    const x =
      bounds.left + bounds.width / 2 - Math.sin(angle) * disp - width / 2;
    const y =
      bounds.top + bounds.height / 2 + Math.cos(angle) * disp - height / 2;

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
          colour: point.color,
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

  interface PieData {
    values: number[];
    labels: string[];
    colours: string[];
  }

  // Formatting data to be read by plotly
  const formatted =
    useMemo(
      () =>
        data?.data.reduce<PieData>(
          (acc, red) => ({
            values: acc.values.concat([red.value]),
            labels: acc.labels.concat([red.label]),
            colours: acc.colours.concat([red.defaultColour]),
          }),
          { values: [], labels: [], colours: [] },
        ),
      [data],
    ) ?? null;

  if (data == null || formatted == null) {
    return staticChart ? <Loading /> : null;
  }

  // Format info of text on segment hover
  const hoverTemplate = `${data.hover.showLabel ? "%{label}" : ""}<br>${data.hover.showPercent ? "%{percent}" : ""}<br>${data.hover.showValue ? `%{value}${data.hover.unit}` : ""}<extra></extra>`;

  return (
    <>
      {infos.map((s) => (
        <InfoBox {...s} key={s.id} />
      ))}
      <Plot
        data={[
          {
            type: "pie",
            labels: formatted.labels,
            values: formatted.values,
            marker: {
              colors: formatted.colours,
            },
            hovertemplate: hoverTemplate,
            textinfo: "label",
            hoverlabel: {
              bgcolor: "white",
            },
          },
        ]}
        layout={
          staticChart
            ? {
                autosize: true,
                width: 200,
                height: 200,
                showlegend: false,
                margin: { t: 0, b: 0, l: 0, r: 0 },
                plot_bgcolor: "rgba(0,0,0,0)",
                paper_bgcolor: "rgba(0,0,0,0)",
              }
            : {
                plot_bgcolor: "rgba(0,0,0,0)",
                paper_bgcolor: "rgba(0,0,0,0)",
                title: data.title ?? manifest[group].views[view].name,
              }
        }
        onClick={data.clickable ? handleClick : undefined}
        config={{
          staticPlot: staticChart,
        }}
      />
    </>
  );
}
