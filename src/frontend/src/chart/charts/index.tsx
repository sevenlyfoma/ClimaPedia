import { ReactElement, useContext } from "react";
import { ChartInfo, ChartType } from "../../types/chart";
import { ChartContext } from "./ChartContext";
import { ManifestContext } from "../../common/contexts/ManifestContext";
import { Pie } from "./Pie";
import { Line } from "./Line";
import { Scatter } from "./Scatter";

interface ChartProps {
  chartInfo: ChartInfo;
  staticChart?: boolean;
}

// Chart type component dictionary
const components: Record<ChartType, ReactElement<Record<string, never>>> = {
  pie: <Pie />,
  line: <Line />,
  scatter: <Scatter />,
};

export function Chart({ chartInfo, staticChart }: ChartProps) {
  const manifest = useContext(ManifestContext);
  const chartType = manifest[chartInfo.group].views[chartInfo.view]
    .type as ChartType;

  return (
    <ChartContext.Provider
      value={{ ...chartInfo, staticChart: staticChart ?? false }}
    >
      {components[chartType]}
    </ChartContext.Provider>
  );
}
