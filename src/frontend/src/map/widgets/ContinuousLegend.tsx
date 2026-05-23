import { ContinuousLegend } from "../../types/common";

interface ContinuousLegendProps {
  legend: ContinuousLegend;
}

export default function ContinuousLegend({ legend }: ContinuousLegendProps) {
  const {
    valueRange,
    colourRange = ["#000", "#fff"],
    ticks = 3,
    unit = "",
  } = legend;
  const range = valueRange[1] - valueRange[0];
  return (
    <div className="continuous-legend">
      <div
        className="colour-scale"
        style={{
          background: `linear-gradient(0deg, ${colourRange.join(",")})`,
        }}
      />
      {/* https://stackoverflow.com/questions/34189370/how-to-repeat-an-element-n-times-using-jsx-and-lodash */}
      <div className="colour-ticks">
        {[...(Array(ticks) as number[])].map((_, i) => (
          <span key={i}>
            <p>
              {(valueRange[1] - range * (i / (ticks - 1))).toPrecision(3)}{" "}
              {unit}
            </p>
          </span>
        ))}
      </div>
    </div>
  );
}
