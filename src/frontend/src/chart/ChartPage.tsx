import { Chart } from "./charts";
import "./Chart.css";
import { useToggledParams } from "../common/hooks/useQueryParams";
import { useManifest } from "../common/hooks/useManifest";
import { ChartPreview } from "./ChartPreview";
import Legend from "../common/Legend/Legend";

export function ChartPage() {
  const manifest = useManifest("chart");
  const [toggled, setToggled] = useToggledParams(manifest, false);

  // Show a preview of all the cahrts if none selected
  return toggled === null ? (
    <ChartPreview handleClick={setToggled} />
  ) : (
    <>
      <Chart chartInfo={toggled}></Chart>
      <Legend
        manifest={manifest}
        setToggledView={setToggled}
        toggledView={toggled}
        multiple={false}
      />
    </>
  );
}
