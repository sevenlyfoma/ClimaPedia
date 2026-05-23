from datetime import datetime, timedelta

import pandas as pd

from .prediction_db import PredictionDB
from .overlay import Overlay
from .utils import create_voronoi, ONTARIO_BOUNDS


class ExtremeOverlay(Overlay):
    """An overlay for extreme cold.

    Constants:
        ONTARIO: String for Ontario.
        MATTAWA: The location of Mattawa.
        VALUES_LENGEND: The values legend.
    """

    ONTARIO = "ON"
    MATTAWA = (46.32, -78.70)
    VALUES_LEGEND = {
        "valueRange": [0, 1],
        "ticks": 2,
        "colourRange": ["red", "blue"],
    }

    def __init__(self, db: PredictionDB) -> None:
        super().__init__(db, is_pred=True)

    def get_response(self, req_dt: datetime):
        """Get extreme cold for Ontario.

        Parameters:
            req_dt: The time of the weather.

        Returns:
            JSON response.
        """
        with PredictionDB.ensure_open(self.db):
            preds = pd.DataFrame.from_records(
                self.db.get_vals_for_time_province(
                    req_dt, self.ONTARIO, is_pred=self.is_pred
                ),
                columns=["temperature", "latitude", "longitude"],
            )
            preds_next_hour = pd.DataFrame.from_records(
                self.db.get_vals_for_time_province(
                    req_dt + timedelta(hours=1), self.ONTARIO, is_pred=self.is_pred
                ),
                columns=["temperature", "latitude", "longitude"],
            )

        if preds_next_hour.shape[0] == 0:
            print("error, no next hour found.")
            return {"polygons": [], "values": [], "valuesLegend": self.VALUES_LEGEND}

        all_preds = pd.merge(
            preds,
            preds_next_hour,
            on=["latitude", "longitude"],
            suffixes=("", "_next"),
        )

        points = all_preds[["latitude", "longitude"]].to_numpy()
        warnings = all_preds.apply(self.__get_warning, axis=1).to_numpy()

        polys, warnings = create_voronoi(points, warnings, ONTARIO_BOUNDS)

        return {
            "polygons": [p for i, p in enumerate(polys) if warnings[i]],
            "values": [1 for x in warnings if x],
            "valuesLegend": self.VALUES_LEGEND,
        }

    def __get_warning(self, row: pd.Series) -> bool:
        """Get if this row should display a warning.

        Parameters:
            row: The row from the DF.

        Returns:
            True if this row has a warning.
        """
        lat, long = row[["latitude", "longitude"]]

        if lat > self.MATTAWA[0] and long > self.MATTAWA[1]:
            # South-east.
            min_temp = -35
        elif lat < self.MATTAWA[0] and long <= self.MATTAWA[1]:
            # Central and South-west.
            min_temp = -30
        else:
            # Northern
            min_temp = -30

        return (row[["temperature", "temperature_next"]] <= min_temp).all()
