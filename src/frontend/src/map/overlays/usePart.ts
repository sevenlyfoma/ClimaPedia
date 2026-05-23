import { useState, useEffect, useContext } from "react";
import { OverlayContext } from "./OverlayContext";
import { GetPartFn, PartData } from "../../types/api";
import { customHTML } from "../../common/CustomHTML";
import * as L from "leaflet";

// Handles fetching custom parts data
export function usePart<T extends PartData, R>(
  getPart: GetPartFn<T>,
  validIds: string[],
  setPartStyle: (el: R, enable: boolean) => void = () => undefined,
  extraParams: Record<string, string> = {},
): { handleClick: (id: string) => L.LeafletEventHandlerFn; id: string | null } {
  const [selectedPart, setSelectedPart] = useState<{
    id: string;
    part: R;
    startTime?: string;
  } | null>(null);

  const { updateWidget, timeData } = useContext(OverlayContext);

  // Handling part no longer being on screen (then close it)
  useEffect(() => {
    if (selectedPart == null) {
      return;
    }

    // If part not on screen, then remove custom widget
    if (!validIds.includes(selectedPart.id)) {
      updateWidget("custom", null);
      selectedPart && setPartStyle(selectedPart.part, false);
      setSelectedPart(null);
    }
  }, [selectedPart, setPartStyle, updateWidget, validIds]);

  // Handling part on time changes
  useEffect(() => {
    if (
      timeData?.partRefetch &&
      selectedPart != null &&
      selectedPart.startTime !== timeData.startTime
    ) {
      getPart(selectedPart.id, extraParams)
        .then((v) => {
          if (v?.widget !== undefined) {
            updateWidget("custom", {
              name: v.widget.title,
              component: customHTML(v.widget.markup),
              size: v.widget.size ? "small" : "big",
              order: 1000,
            });
            setSelectedPart({ ...selectedPart, startTime: timeData.startTime });
          }
        })
        .catch((e) => console.error(e));
    }
  }, [
    extraParams,
    getPart,
    selectedPart,
    timeData?.partRefetch,
    timeData?.startTime,
    updateWidget,
  ]);

  // The function, which given the part id, returns a leaflet click handler
  function handleClick(id: string): L.LeafletEventHandlerFn {
    return (async (e) => {
      if (selectedPart?.id === id) {
        updateWidget("custom", null);
        selectedPart && setPartStyle(e.target as R, false);
        setSelectedPart(null);
        return;
      }

      try {
        const v = await getPart(id, extraParams);
        if (v?.widget !== undefined) {
          updateWidget("custom", {
            name: v.widget.title,
            component: customHTML(v.widget.markup),
            size: v.widget.size ? "small" : "big",
            order: 1000,
          });
          setPartStyle(e.target as R, true);
          selectedPart && setPartStyle(selectedPart.part, false);
          setSelectedPart({
            id,
            part: e.target as R,
            startTime: timeData?.startTime,
          });
        }
      } catch (e) {
        console.error("Failed to get part protocol for part:", id, e);
      }
    }) as L.LeafletEventHandlerFn;
  }

  return { handleClick, id: selectedPart?.id ?? null };
}
