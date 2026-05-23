import Draggable from "react-draggable";
import { customHTML } from "../../common/CustomHTML";

export interface InfoBoxProps {
  x: number;
  y: number;
  width: number;
  height: number;
  name: string;
  colour: string;
  order?: number;
  onDrag?: () => void;
  onClose?: () => void;
  html?: string;
}

// For rendering custom html for charts
export function InfoBox(props: InfoBoxProps) {
  return (
    <Draggable onDrag={props.onDrag}>
      <div
        className="infobox-container"
        style={{
          top: props.y,
          left: props.x,
          width: props.width,
          height: props.height,
          zIndex: props.order,
        }}
      >
        <h1>{props.name}</h1>
        <div className="accent" style={{ backgroundColor: props.colour }}>
          <button onClick={props.onClose}>X</button>
        </div>
        <div className="custom-content">
          {props.html && customHTML(props.html)}
        </div>
      </div>
    </Draggable>
  );
}
