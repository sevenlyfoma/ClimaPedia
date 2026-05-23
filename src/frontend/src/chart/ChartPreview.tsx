import { useManifest } from "../common/hooks/useManifest";
import { Chart } from "./charts";
import { ViewInfo } from "../types/common";

interface ChartPreviewProps {
  handleClick: (clicked: ViewInfo) => void;
}

export function ChartPreview(props: ChartPreviewProps) {
  const manifest = useManifest("chart");

  // Nearly displaying all the possible charts
  return (
    <div className="scroll-container">
      <div id="chart-preview" className="scroll">
        {Object.entries(manifest).flatMap(([group, g]) =>
          Object.keys(g.views).map((view) => (
            <button
              key={`${group}/${view}`}
              className="preview-chart"
              onClick={() => props.handleClick({ group, view })}
            >
              <h1>{manifest[group].views[view].name}</h1>
              <Chart chartInfo={{ group, view }} staticChart={true} />
            </button>
          )),
        )}
      </div>
    </div>
  );
}
