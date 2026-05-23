import chroma from "chroma-js";

const COLOURS = [
  "blue",
  "red",
  "green",
  "cyan",
  "magenta",
  "yellow",
  "orange",
  "black",
  "white",
];

// Check if a given colour is supported
export function isSupported(val: string) {
  if (COLOURS.indexOf(val) >= 0) {
    return true;
  }
  console.warn(
    `"${val}" is an unsupported colour! For accessibility support, ensure that all colours used are one of: ${COLOURS.join(",")}`,
  );
  return false;
}

// Given a color, check if it is supported in the CSS mappings and convert to the corresponding variable name
// If converting to a valid CSS colour value, use getColourVarValue instead!
export function mappedColour(value: string) {
  if (isSupported(value)) {
    return getComputedStyle(document.body).getPropertyValue(
      `--replace-${value}`,
    );
  }
  return value;
}

// Given a value, its range, and a range of colours, get the colour corresponding to the value relative to the value range
export function getContinuousColour(
  value?: number,
  valueRange?: [number, number],
  colourRange: string[] = ["#000", "#fff"], // Can be a mix of supported and non-supported colours
): string {
  if (value === undefined || valueRange === undefined) {
    return "#000";
  }

  return chroma.scale(colourRange).domain(valueRange)(value).hex();
}

// Converting from mapping of normalised values to colours, to an array of 20 equally spaced colours
export function magnitudesToColourArray(mag: Record<number, string>): string[] {
  const pairs = Object.entries(mag).sort((a, b) => +a[0] - +b[0]);
  return chroma
    .scale(pairs.map((p) => p[1]))
    .domain(pairs.map((p) => +p[0]))
    .colors(20);
}

// Converting from array of equally spaced colours to mapping of normalised values to colours
export function colourArrayToMagnitude(
  colours: string[],
): Record<number, string> {
  return Object.fromEntries(
    colours.map<[number, string]>((c, i) => [i / (colours.length - 1), c]),
  );
}
