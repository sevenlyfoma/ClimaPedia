import { GroupsManifest } from "../types/api";
import { View, type Focus } from "../types/common";

export function normalise(value: number, valueRange: [number, number]): number {
  return (value - valueRange[0]) / (valueRange[1] - valueRange[0]);
}

// Filter manifest based on view focus
export function filterManifest<F extends Focus>(
  manifest: GroupsManifest<Focus>,
  focus: F,
): GroupsManifest<F> {
  return Object.fromEntries(
    Object.entries(manifest).map(([g, group]) => {
      return [
        g,
        {
          ...group,
          views: Object.fromEntries(
            Object.entries(group.views).filter(
              ([, view]) => view.focus === focus,
            ),
          ) as Record<string, View<F>>,
        },
      ];
    }),
  );
}

// Getting the pane key given the group and view
export function paneKey(group: string, view: string) {
  return `${group}-${view}`;
}
