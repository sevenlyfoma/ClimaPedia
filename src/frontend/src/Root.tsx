import { Outlet } from "react-router-dom";
import NavigationBar from "./navigation/NavigationBar";
import { useEffect, useState } from "react";
import SettingModal from "./settings/SettingModal";
import { getManifest } from "./utils/api";
import { GroupsManifest } from "./types/api";
import { ManifestContext } from "./common/contexts/ManifestContext";
import { CountryGeoJSON } from "./types/map";
import { CountriesContext } from "./common/contexts/CountriesContext";
import { Focus } from "./types/common";
import { ErrorScreen } from "./ErrorScreen";

// Putting content shared by our pages here
export function Root() {
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [manifest, setManifest] = useState<GroupsManifest<Focus> | null>(null);
  const [countries, setCountries] = useState<CountryGeoJSON | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Fetching the data on page load
  useEffect(() => {
    getManifest()
      .then((r: GroupsManifest<Focus>) => setManifest(r))
      .catch((e) => {
        console.error("Failed to load manifest", e);
        setError("Failed to load the data manifest");
      });

    fetch("/countries.geojson")
      .then((d) => d.json())
      .then((d) => setCountries(d as CountryGeoJSON))
      .catch((e) => console.warn("Failed to load the countries:", e));
  }, []);

  // Nested pages rendered in <Outlet />
  // Providing manifest and countries to content via contexts
  return (
    <>
      <NavigationBar
        showSettings={showSettings}
        setShowSettings={setShowSettings}
      />
      {error === null ? (
        manifest === null ? null : (
          <ManifestContext.Provider value={manifest}>
            <CountriesContext.Provider value={countries}>
              <Outlet />
            </CountriesContext.Provider>
          </ManifestContext.Provider>
        )
      ) : (
        <ErrorScreen message={error} />
      )}
      <SettingModal show={showSettings} setShow={setShowSettings} />
    </>
  );
}
