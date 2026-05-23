import { createContext } from "react";
import { GroupsManifest } from "../../types/api";
import { Focus } from "../../types/common";

// Manifest in context that may be accessed by components
export const ManifestContext = createContext<GroupsManifest<Focus>>({});
