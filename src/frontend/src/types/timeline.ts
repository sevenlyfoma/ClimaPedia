export type TimelineType = "layeredTimeline";

export interface TimelineInfo {
  group: string;
  view: string;
}

export interface Duration {
  id: string;
  title: string;
  start: Date;
  end: Date;
  style?: {
    backgroundColor: string;
    boxShadow: string;
  };
}
export interface TrackEvent {
  id: string;
  title: string;
  elements: Duration[];
}

export interface Track {
  id: string;
  title: string;
  elements: Duration[];
  tracks: TrackEvent[];
  isOpen: boolean;
}
