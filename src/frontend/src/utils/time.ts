import _ from "lodash";

// Get the latest time from a list of times
export function getMaxTime(times: string[]): string {
  return _.maxBy(times, (t) => new Date(t).getTime()) ?? times[0];
}

// Get the earliest time from a list of times
export function getMinTime(times: string[]): string {
  return _.minBy(times, (t) => new Date(t).getTime()) ?? times[0];
}

// Get the earliest and latest time from a list of times
export function getTimeRange(times: string[]): [string, string] {
  const max = getMaxTime(times);
  const min = getMinTime(times);

  return [min, max];
}

// Snap the given time to one in a list of times
export function snapTime(times: string[], time: Date): string {
  return times.reduce(
    (acc, red) =>
      Math.abs(time.getTime() - new Date(red).getTime()) <
      Math.abs(time.getTime() - new Date(acc).getTime())
        ? red
        : acc,
    times[0],
  );
}
