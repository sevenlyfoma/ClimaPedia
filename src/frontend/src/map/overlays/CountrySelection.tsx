import { useCallback, useContext } from "react";
import { GeoJSON } from "react-leaflet";
import {
  CountryGeoJSONFeature,
  CountryGeoJSONProperties,
} from "../../types/map";
import { CountriesContext } from "../../common/contexts/CountriesContext";
import { OverlayContext } from "./OverlayContext";
import { paneKey } from "../../utils/common";

interface CountrySelectionProps {
  countries: string[];
  selectCountry: (country: string) => void;
}

// Rendering the country outlines for users to choose from
export default function CountrySelection(props: CountrySelectionProps) {
  const countries = useContext(CountriesContext);
  const { group, view } = useContext(OverlayContext);

  const selectableCountries = useCallback(
    (f: CountryGeoJSONFeature) => props.countries.includes(f.properties.ISO_A3),
    [props.countries],
  );

  if (countries == null) {
    return null;
  }

  return (
    <GeoJSON
      data={countries}
      onEachFeature={(c, layer) =>
        layer.addEventListener("click", () =>
          props.selectCountry(
            (c.properties as CountryGeoJSONProperties).ISO_A3,
          ),
        )
      }
      filter={selectableCountries}
      pane={paneKey(group, view)}
    />
  );
}
