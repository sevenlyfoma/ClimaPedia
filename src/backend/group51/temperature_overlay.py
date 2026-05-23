from datetime import datetime

import pandas as pd


from .utils import create_voronoi, CANADA_BOUNDS
from .prediction_db import PredictionDB
from .overlay import Overlay


class TemperatureOverlay(Overlay):
    """An overlay for temperature prediction."""

    def __init__(self, db: PredictionDB, *, is_pred: bool) -> None:
        super().__init__(db, is_pred=is_pred)

    def get_response(self, req_time: datetime):
        """Get the response.

        Parameters:
            req_time: The datetime to get for.

        Returns:
            Response for the API.
        """
        with PredictionDB.ensure_open(self.db):
            min_max_pred = self.db.get_min_max_preds(is_pred=self.is_pred)

            df = pd.DataFrame.from_records(
                self.db.get_vals_for_time(req_time, is_pred=self.is_pred),
                columns=["temperature", "latitude", "longitude"],
            )

        points = df[["latitude", "longitude"]].to_numpy()
        temperatures = df["temperature"].to_numpy()

        polys, values = create_voronoi(points, temperatures, CANADA_BOUNDS)

        return {
            "polygons": polys,
            "values": values,
            "valuesLegend": {
                "valueRange": [
                    min_max_pred["min"],
                    min_max_pred["max"],
                ],
                "unit": "°C",
                "ticks": 5,
                "colourRange": ["blue", "green", "yellow", "red"],
            },
        }
