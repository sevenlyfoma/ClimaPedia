from __future__ import annotations
from types import TracebackType

from contextlib import AbstractContextManager, contextmanager
from datetime import datetime

import pymysql
import pymysql.cursors


class PredictionDB(AbstractContextManager):
    """Manages a database connection for Group 51.

    Attributes:
        conn: The connection object.
        cur: The cursor object.
        host: The host to connect to.
        port: The port to connect on.
        user: The user to connect as.
        password: The password to connect with.
        database: The database to use.
    """

    @contextmanager
    def ensure_open(db: PredictionDB):
        """Ensure a PredictionDB object is open.

        Parameters:
            db: The database object.
        """
        must_close = False
        if not db.is_open():
            must_close = True
            db.open()

        try:
            yield
        finally:
            if must_close:
                db.close()

    conn: pymysql.Connection | None
    cur: pymysql.cursors.Cursor | None

    host: str
    port: int
    user: str
    password: str
    database: str

    def __init__(
        self, host: str, user: str, password: str, database: str, port: int = 3306
    ) -> None:
        """Constructor.

        Parameters:
            host: The host to connect to.
            user: The user to connect as.
            password: The password to connect with.
            database: The database to use.
            port: The port to connect on. (Optional)
        """
        self.conn = None
        self.cur = None

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def __enter__(self) -> PredictionDB:
        """Open the database connection."""
        self.open()

        return super().__enter__()

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None,
    ) -> bool | None:
        """Close the database connection."""
        self.close()

        return None

    def open(self) -> None:
        """Open the database connection"""
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )

        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

    def close(self) -> None:
        """Close the database connection"""
        if self.cur is not None:
            self.cur.close()
            self.cur = None

        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def is_open(self) -> bool:
        """Check if the connection is open."""
        return self.conn is not None

    def get_max_min_dates(self, is_pred: bool) -> dict:
        """Get the maximum and minimum dates in the database.

        Parameters:
            is_pred: Get predictions or actual values.

        Returns:
            Dict of results.
        """
        if self.cur is None:
            raise RuntimeError()

        self.cur.execute(
            """
            SELECT
                MAX(datetime) AS max,
                MIN(datetime) AS min
            FROM prediction
            WHERE is_prediction=%s
            """,
            (is_pred,),
        )

        return self.cur.fetchone()

    def get_min_max_preds(self, *, is_pred: bool) -> dict:
        """Get the minimum and maximum values in the database.

        Parameters:
            is_pred: If we're getting predictions or not.

        Returns:
            A dict of results.
        """
        self.cur.execute(
            """
            SELECT
                MAX(p.temperature) as max,
                MIN(p.temperature) as min
            FROM prediction p
            LEFT JOIN station s ON p.station_id = s.can_id
            WHERE p.is_prediction=%s
            """,
            (is_pred,),
        )

        return self.cur.fetchone()

    def get_vals_for_time_province(
        self, dt: datetime, province: str, *, is_pred: bool
    ) -> tuple[dict, ...]:
        """Get the values for a time in a province.

        Parameters:
            dt: The datetime to get.
            province: The province/territory to get from.
            is_pred: If we're getting predictions or actual values.

        Returns:
            Tuple of dicts of results.
        """
        self.cur.execute(
            """
            SELECT
                p.temperature AS temperature,
                IFNULL(s.latitude, 0) AS latitude,
                IFNULL(s.longitude, 0) AS longitude
            FROM prediction p
            INNER JOIN ca_station_map s_map ON p.station_id = s_map.station_id
            LEFT JOIN station s ON p.station_id = s.can_id
            WHERE
                p.datetime=%s AND
                p.is_prediction=%s AND
                s_map.province=%s
            """,
            (dt, is_pred, province),
        )

        return self.cur.fetchall()

    def get_vals_for_time(self, dt: datetime, *, is_pred: bool) -> tuple[dict, ...]:
        """Get values for a time from all of Canada.

        Parameters:
            dt: The datetime to get.
            is_pred: If we're getting predictions or actual values.

        Returns:
            Tuple of dicts of results.
        """
        self.cur.execute(
            """
            SELECT
                p.temperature AS temperature,
                IFNULL(s.latitude, 0) AS latitude,
                IFNULL(s.longitude, 0) AS longitude
            FROM prediction p
            LEFT JOIN station s ON p.station_id = s.can_id
            WHERE
                p.datetime=%s AND
                p.is_prediction=%s
            """,
            (dt, is_pred),
        )

        return self.cur.fetchall()
