import { createContext } from "react";

export interface ChartContextProps {
  group: string;
  view: string;
  staticChart?: boolean;
}

// Basically the props provided to the chart views
export const ChartContext = createContext<ChartContextProps>({
  group: "",
  view: "",
  staticChart: false,
});
