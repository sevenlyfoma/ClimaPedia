import { type ReactNode } from "react";

export type MapType = "points" | "voronoi-heat" | "point-heat" | "point-tree";

// Types for overlay widget
export interface OverlayWidgetData {
  name: string;
  size?: "small" | "big";
  component: ReactNode;
  order?: number;
}

// Countires as parsed from the countries file

export interface CountryGeoJSON {
  type: "FeatureCollection";
  features: CountryGeoJSONFeature[];
}
export interface CountryGeoJSONFeature {
  type: "Feature";
  properties: CountryGeoJSONProperties;
  geometry: unknown;
}
export interface CountryGeoJSONProperties {
  ADMIN: string;
  ISO_A3: string;
  ISO_A2: string;
}
