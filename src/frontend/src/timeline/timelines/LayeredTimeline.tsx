import { defaultTimelineData } from "../../utils/default";
import { TimeLineSubentry, TimelineEntry } from "../../types/common";
import { useData } from "./useData";
import _ from "lodash";
import { TimelineLayeredTimelineData, PartData } from "../../types/api";
// @ts-expect-error Ignore lack of types for react-timelines
import Timeline from "react-timelines";
import { useContext, useState, useEffect } from "react";
import { customHTML } from "../../common/CustomHTML";

import "react-timelines/lib/css/style.css";
import { TimelineContext } from "./TimelineContext";
import { Duration, Track, TrackEvent } from "../../types/timeline";
import { colourTimelineData } from "../../utils/colourmap";

// constants
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
const MIN_ZOOM = 0.05,
  MAX_ZOOM = 20;

//note: if you find any mention of satellites, please remove it

// export element for rendering
export function LayeredTimeline() {
  const { data, getPart } = useData<TimelineLayeredTimelineData, PartData>(
    defaultTimelineData,
    colourTimelineData,
  );
  const { updateWidget } = useContext(TimelineContext);
  const [selectedPart, setSelectedPart] = useState<{
    id: string;
  } | null>(null);

  const [open, setOpen] = useState(false);
  const [zoom, setZoom] = useState(2);
  const [tracksById, setTracksById] = useState<Record<string, Track> | null>(
    null,
  );

  useEffect(() => {
    if (data == null) {
      return;
    }

    // protocol to react-timeline tracks
    function extractTracks(entries: TimelineEntry[]): Record<string, Track> {
      const dict: Record<string, Track> = {};
      for (const entry of entries) {
        const eventTrack = [
          extractEventsTrack(entry.subentries, entry.id, entry.label),
        ];

        dict[entry.id] = {
          id: entry.id,
          title: entry.label,
          elements: getDurationTrack(entry),
          tracks: eventTrack,
          isOpen: false,
        };
      }

      return dict;
    }

    // get date of day after date
    function dayAfter(dateString: string) {
      const oldDate = new Date(dateString);
      return new Date(
        `${oldDate.getFullYear()}-${oldDate.getMonth() + 1}-${oldDate.getDate() + 1}`,
      );
    }

    // turn subentries into track of events
    function extractEventsTrack(
      subentries: TimeLineSubentry[],
      parentID: string,
      parentTitle: string,
    ): TrackEvent {
      const trackItems = [];
      let colour;
      for (const subentry of subentries) {
        colour = subentry.defaultColour ? subentry.defaultColour : "blue";
        trackItems.push({
          id: subentry.id,
          title: subentry.label,
          start: new Date(subentry.point),
          end: dayAfter(subentry.point),
          style: {
            backgroundColor: colour,
            boxShadow: "0px 4px 4px rgba(0, 0, 0, 0.4)",
          },
        });
      }

      return {
        id: parentID + "events",
        title: parentTitle + "'s events",
        elements: trackItems,
      };
    }

    // react-timelines track for total entry duration
    function getDurationTrack(entry: TimelineEntry): Duration[] {
      return [
        {
          id: entry.id,
          title: entry.label,
          start: new Date(entry.range[0]),
          end: new Date(entry.range[1]),
          style: {
            backgroundColor: entry.defaultColour
              ? entry.defaultColour
              : "white",
            boxShadow: "0px 4px 4px rgba(0, 0, 0, 0.4)",
          },
        },
      ];
    }

    setTracksById(extractTracks(data.entries));
  }, [data]);

  //waiting on data
  if (data == null || tracksById == null) {
    return <p>loading...</p>;
  }

  const range = [new Date(data.range[0]), new Date(data.range[1])];
  const [monthTiles, yearTiles] = getDateTiles(range);
  const timeAxis = createAxis(monthTiles, yearTiles);

  // get date at start of month 'extra' months after 'year'
  function monthIncrement(year: number, extra: number) {
    return new Date(`${year + Math.floor(extra / 12)}-${1 + (extra % 12)}`);
  }

  // get tiles for dates to make up timeline
  function getDateTiles(range: Date[]) {
    const monthTiles = [],
      yearTiles = [];
    const noMonths =
      Math.ceil(
        (range[1].valueOf() - range[0].valueOf()) /
          (1000 * 3600 * 24 * (365.25 / 12)),
      ) +
      12 * 10;

    const firstYear = range[0].getFullYear();

    for (let index = 0; index < noMonths; index++) {
      const monthID = index;
      monthTiles.push({
        id: `${monthID}` + "month",
        title: MONTHS[index % 12],
        start: monthIncrement(range[0].getFullYear(), monthID),
        end: monthIncrement(range[0].getFullYear(), monthID + 1),
      });

      // years start in january
      if (monthID % 12 == 0) {
        yearTiles.push({
          id: `${monthID}` + "year",
          title: `${firstYear + Math.ceil(monthID / 12)}`,
          start: monthIncrement(range[0].getFullYear(), monthID),
          end: monthIncrement(range[0].getFullYear(), monthID + 12),
        });
      }
    }
    return [monthTiles, yearTiles];
  }

  // time axes for months and years for timeline
  function createAxis(monthTiles: Duration[], yearTiles: Duration[]) {
    return [
      {
        id: "years",
        title: "years",
        cells: yearTiles,
        useAsGrid: true,
      },
      {
        id: "months",
        title: "Months",
        cells: monthTiles,
      },
    ];
  }

  // 180030967 witchcraft
  async function clickElement(element: Duration) {
    const v = await getPart(element.id);
    const id = element.id;
    if (v?.widget !== undefined) {
      if (selectedPart?.id === id) {
        updateWidget("custom", null);
        setSelectedPart(null);
      } else {
        updateWidget("custom", {
          name: v.widget.title,
          component: customHTML(v.widget.markup),
          size: v.widget.size ? "small" : "big",
        });
        setSelectedPart({ id });
      }
    }
  }

  // toggle whether timeline is open
  function openClose() {
    setOpen((o) => !o);
  }

  // zoom in button handler
  function zoomIn() {
    setZoom((z) => Math.min(z + 0.2, MAX_ZOOM));
  }

  // zoom out button handler
  function zoomOut() {
    setZoom((z) => Math.max(z - 0.2, MIN_ZOOM));
  }

  // toggle selected track to open, code for this function based on 'handleToggleTrackOpen()':
  // https://github.com/JSainsburyPLC/react-timelines/blob/master/demo/src/App.jsx
  // last accessed: 11/03/2024 - 16:08
  function toggleTrackOpen(track: Track) {
    setTracksById((s) => {
      if (s == null) {
        return s;
      }

      const newS = _.cloneDeep(s);
      newS[track.id].isOpen = !newS[track.id].isOpen;

      return newS;
    });
  }

  const start = range[0];
  const end = range[1];
  const scaleData = {
    start,
    end,
    zoom,
    zoomMin: MIN_ZOOM,
    zoomMax: MAX_ZOOM,
  };

  // auto overflow to allow for scrolling
  return (
    <div style={{ overflow: "auto" }}>
      <Timeline
        scale={scaleData}
        isOpen={open}
        toggleOpen={openClose}
        zoomIn={zoomIn}
        zoomOut={zoomOut}
        clickElement={clickElement}
        toggleTrackOpen={toggleTrackOpen}
        timebar={timeAxis}
        tracks={Object.values(tracksById)}
        enableSticky
        now={end}
        scrollToNow
      />
    </div>
  );
}
