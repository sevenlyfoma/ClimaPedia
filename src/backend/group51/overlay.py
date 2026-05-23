from abc import ABC, abstractmethod
from datetime import datetime
from dateutil import rrule

from .prediction_db import PredictionDB


class Overlay(ABC):
    db: PredictionDB
    is_pred: bool

    def __init__(self, db: PredictionDB, *, is_pred: bool) -> None:
        self.db = db
        self.is_pred = is_pred

    def get_meta(self) -> dict:
        """Get the metadata for the request.

        Returns:
            Meta response.
        """
        with PredictionDB.ensure_open(self.db):
            res = self.db.get_max_min_dates(self.is_pred)

        min_date = res["min"]
        max_date = res["max"]

        times = [
            dt.strftime("%Y-%m-%d:%H:%M:%S")
            for dt in rrule.rrule(rrule.HOURLY, dtstart=min_date, until=max_date)
        ]

        return {
            "timeData": {
                "times": times,
                "period": {"unit": "hour", "value": 1},
                "range": [min_date, max_date],
                "value": min_date,
                "persistent": True,
            },
        }

    @abstractmethod
    def get_response(self, req_dt: datetime): ...
