import { InteractiveTimeMetaData } from "../../types/common";
import { useRef, useEffect, useState } from "react";
import * as vis from "vis-timeline";
import { DataSet } from "vis-data";
import "vis-timeline/styles/vis-timeline-graph2d.min.css";
import { snapTime } from "../../utils/time";

// The delay before setting time while moving a persistent time slider (ms)

interface TimeSliderProps {
  timeData: InteractiveTimeMetaData;
}

export default function TimeSlider(props: TimeSliderProps) {
  const { times, range, persistent, startTime, endTime, setTime, fetchDelay } =
    props.timeData;

  const divRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<vis.Timeline | null>(null);
  const itemsRef = useRef<DataSet<vis.DataItem, "id">>(
    new DataSet([
      {
        id: 1,
        content: "Selection",
        start: startTime,
        end: endTime,
        editable: {
          remove: false,
          updateGroup: false,
          updateTime: true,
        },
        group: 1,
        type: persistent ? "box" : "range",
      },
    ]),
  );

  const [waiting, setWaiting] = useState(false);
  const [waitTime, setWaitTime] = useState(startTime);

  // Prevent the time from changing too frequently (to reduce number of requests)
  useEffect(() => {
    if (persistent && !waiting && waitTime !== startTime) {
      setTime(waitTime);
      setWaiting(true);

      setTimeout(() => {
        setWaiting(false);
        setTime(waitTime);
      }, fetchDelay);
    }
  }, [persistent, setTime, waitTime, waiting, startTime, fetchDelay]);

  // Creation of timeline
  useEffect(() => {
    if (divRef.current !== null) {
      const groups: vis.DataGroupCollectionType = [
        {
          id: 1,
          content: "",
        },
        {
          id: 2,
          content: "",
        },
      ];

      timelineRef.current = new vis.Timeline(
        divRef.current,
        itemsRef.current,
        groups,
        {
          // Min zoom is 1 day
          zoomMin: 86400000,
          stack: false,
          clickToUse: true,
        },
      );
      return () => {
        timelineRef.current?.destroy();
        timelineRef.current = null;
      };
    }
  }, [divRef]);

  // Adding data
  useEffect(() => {
    itemsRef.current?.update(
      times.map((t, i) => ({
        id: i + 2,
        content: "",
        start: t,
        group: 2,
        selectable: false,
        type: "point",
      })),
    );
  }, [times]);

  // Updating range
  useEffect(() => {
    timelineRef.current?.setOptions({
      min: range[0],
      max: range[1],
    });
  }, [range]);

  // Updating on change options
  useEffect(() => {
    if (persistent) {
      // Set snapping and update while moving for persistent
      timelineRef.current?.setOptions({
        snap: (date) => new Date(snapTime(times, date)),
        onMoving(item, callback) {
          if (
            new Date(range[0]).getTime() >= new Date(item.start).getTime() &&
            new Date(range[1]).getTime() <= new Date(item.start).getTime()
          ) {
            callback(null);
            return;
          }
          const start = snapTime(times, new Date(item.start));
          if (waitTime !== start) {
            setWaitTime(start);
          }
          callback(item);
        },
      });
    } else {
      // If not persistent, updating on resize or moving
      timelineRef.current?.setOptions({
        // In the future, may change to onMoving, and then only refetch if we 'times' in range change
        onMove(item, callback) {
          if (startTime !== item.start || endTime !== item.end) {
            // Using Iso dates
            setTime(
              new Date(item.start).toISOString(),
              item.end !== undefined
                ? new Date(item.end).toISOString()
                : undefined,
            );
          }
          callback(item);
        },
        onMoving(item, callback) {
          // Prevent slider from moving out of range
          if (
            new Date(range[0]).getTime() - 3600000 >
              new Date(item.start).getTime() ||
            new Date(range[1]).getTime() + 3600000 <
              new Date(item.end!).getTime()
          ) {
            callback(null);
            return;
          }
          // Prevent start and end from crossing or equating in range slider
          if (new Date(item.start).getTime() >= new Date(item.end!).getTime()) {
            callback(null);
            return;
          }
          callback(item);
        },
      });
    }
  }, [persistent, range, setTime, startTime, endTime, times, waitTime]);

  return <div ref={divRef} className="timeline" />;
}
