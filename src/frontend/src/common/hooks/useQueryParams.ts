import { Dispatch, SetStateAction, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Focus, ViewInfo } from "../../types/common";
import { GroupsManifest } from "../../types/api";

// Typescript madness to allow either multiple or single views
type ToggledReturn<M extends boolean> = M extends true
  ? [ViewInfo[], Dispatch<SetStateAction<ViewInfo[]>>]
  : [ViewInfo | null, Dispatch<SetStateAction<ViewInfo | null>>];
type ToggledState<M extends boolean> = M extends true ? ViewInfo[] : ViewInfo;

// Reordering logic
function shiftOverlays(overlays: ViewInfo[]) {
  for (let i = overlays.length - 1; i >= 0; i--) {
    overlays[i].index = overlays[i].index! + i;
  }
  return overlays;
}

// Returns a tuple of the toggled views and a callback to change the toggled views
// Modifies the query params of the site based on the views toggled also
export function useToggledParams<F extends Focus, M extends boolean>(
  manifest: GroupsManifest<F> | null,
  multiple: M,
): ToggledReturn<M> {
  const [searchParams, setSearchParams] = useSearchParams();
  const [toggled, setToggled] = useState<ToggledState<M> | null>(null);

  // Changes the url and the toggled views on function call
  function setToggledParam(v: SetStateAction<ToggledState<M> | null>) {
    setToggled(v);
    let newToggled: ToggledState<M> | null = null;
    if (typeof v === "function") {
      newToggled = v(toggled);
    } else {
      newToggled = v;
    }

    if (multiple) {
      searchParams.set(
        "views",
        (newToggled as ViewInfo[]).map((o) => `${o.group}.${o.view}`).join(","),
      );
    } else {
      searchParams.set(
        "views",
        newToggled
          ? `${(newToggled as ViewInfo).group}.${(newToggled as ViewInfo).view}`
          : "",
      );
    }

    setSearchParams(searchParams);
    setToggled(newToggled);
  }

  useEffect(() => {
    const urlOverlays = searchParams.get("views");
    let initialOverlays: ViewInfo[] = [];
    if (manifest !== null && urlOverlays !== null) {
      initialOverlays = urlOverlays.split(",").flatMap((viewStr) => {
        const [group, view] = viewStr.split(".");

        // Make sure it exists
        if (manifest?.[group]?.views?.[view] == undefined) {
          return [];
        }

        const index = 0;
        return [{ group, view, index }];
      });
      initialOverlays = shiftOverlays(initialOverlays);
    }

    if (multiple) {
      setToggled(initialOverlays as ToggledState<M>);
    } else {
      setToggled((initialOverlays?.[0] ?? null) as ToggledState<M>);
    }
  }, [manifest, multiple, searchParams, setToggled]);

  if (multiple) {
    return [toggled ?? [], setToggledParam] as ToggledReturn<M>;
  } else {
    return [toggled, setToggledParam] as ToggledReturn<M>;
  }
}
