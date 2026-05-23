import { InteractiveSeries } from "../../types/common";

interface SeriesLegendProps {
  series: InteractiveSeries[];
  toggle: (id: number) => void;
}

export default function SeriesLegend({ series, toggle }: SeriesLegendProps) {
  return series.map((s, i) => {
    const c = s.colour ?? "blue";
    return (
      <div
        key={i}
        className="series-field"
        style={{ "--series-colour": c } as React.CSSProperties}
        data-colour={c}
      >
        <button
          role="checkbox"
          onClick={toggle.bind(null, i)}
          className={`series-toggle ${s.active ? "" : "series-inactive"}`}
        />
        <p className="series-name">{s.name}</p>
      </div>
    );
  });
}
