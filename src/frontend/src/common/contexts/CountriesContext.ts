import { createContext } from "react";
import { CountryGeoJSON } from "../../types/map";

// Provide country geoJSON for when needed
export const CountriesContext = createContext<CountryGeoJSON | null>(null);
