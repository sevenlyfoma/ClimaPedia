// Parse the given API path
export const API_PATH = (
  (import.meta.env.FRONTEND_API_PATH ?? import.meta.env.BASE_URL) as string
).replace(/\/$/, "");

console.log(import.meta.env);

// Determing if in dev mode
export const TEST = import.meta.env.FRONTEND_TEST === "1";
