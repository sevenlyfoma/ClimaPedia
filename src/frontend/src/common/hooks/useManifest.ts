import { useContext, useMemo } from "react";
import { Focus } from "../../types/common";
import { filterManifest } from "../../utils/common";
import { ManifestContext } from "../contexts/ManifestContext";

// Returns the manifest with only views of the specific focus
export function useManifest<F extends Focus>(focus: F) {
  const manifest = useContext(ManifestContext);

  return useMemo(() => filterManifest(manifest, focus), [focus, manifest]);
}
