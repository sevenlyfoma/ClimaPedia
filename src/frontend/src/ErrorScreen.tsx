import { useState } from "react";

interface ErrorScreenProps {
  message: string;
}

// Phrases to switch between on error screen
const phrases = [
  ["Toto, we're not in Kansas anymore...", "tornado"],
  ["Experiencing an ice cream blizzard", "icecream"],
  ["Busy fixing the water cycle", "weather_hail"],
  ["Occupied at the beach", "sunny"],
  ["Still waiting for better weather", "cloud"],
  ["Busy salting the icey roads", "ac_unit"],
];

export function ErrorScreen(props: ErrorScreenProps) {
  const [index] = useState(Math.floor(Math.random() * phrases.length));

  return (
    <div className="central-message">
      <h1>{phrases[index][0]}</h1>
      <p className="error-message">({props.message})</p>
      <span className="material-symbols-outlined" style={{ fontSize: "6rem" }}>
        {phrases[index][1]}
      </span>
    </div>
  );
}
