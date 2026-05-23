import { ReactNode } from "react";
import "./Widgets.css";

export default function Widget({
  title,
  children,
  size = "small",
}: {
  title: string;
  children: ReactNode;
  size?: "small" | "big";
}) {
  const widgetClass = size === "small" ? "small-widget" : "large-widget";
  return (
    <div className={`${widgetClass} leaflet-bar widget`}>
      <h1 className="title">{title}</h1>
      <div className="custom-content">{children}</div>
    </div>
  );
}
