"""A module for accessing the weather database for group52."""

from datetime import datetime
import os
from typing import Union
from dotenv import load_dotenv, find_dotenv

# from .db_connector import DBConnection

from .db_accessor import DBAccessor

load_dotenv(find_dotenv())

STATIONS_SCHEMA = os.path.dirname(__file__) + "/stationsSchema.txt"
HISTORY_SCHEMA = os.path.dirname(__file__) + "/historySchema.txt"
EVENTS_SCHEMA = os.path.dirname(__file__) + "/eventsSchema.txt"
TYPES_SCHEMA = os.path.dirname(__file__) + "/typesSchema.txt"
COUNTRIES_SCHEMA = os.path.dirname(__file__) + "/countriesSchema.txt"
EVENT_TYPES_SCHEMA = os.path.dirname(__file__) + "/eventTypesSchema.txt"
EVENT_COUNTRIES_SCHEMA = os.path.dirname(__file__) + "/eventCountriesSchema.txt"


class Tables:
    """Enum storing all tables"""

    STATIONS = "station"
    HISTORY = "weather_data"
    EVENTS = "Events"
    TYPES = "Types"
    COUNTRIES = "Countries"
    EVENT_TYPES = "EventTypes"
    EVENT_COUNTRIES = "EventCountries"


class Station:
    """A class to represent a weather station."""

    def __init__(
        self,
        station_id: str,
        name: str,
        country: str,
        latitude: float,
        longitude: float,
        elevation: int,
    ) -> None:
        """Initializes a station object."""
        self.id = station_id
        self.name = str(name) if name is not None else None
        self.country = str(country) if country is not None else None
        self.latitude = float(latitude) if latitude is not None else None
        self.longitude = float(longitude) if longitude is not None else None
        self.elevation = int(elevation) if elevation is not None else None
        self.reports = []

    def __str__(self):
        """Returns a string representation of the station."""
        return f"""Station ID: {self.id}, Name: {self.name}, Country: {self.country},
                Latitude: {self.latitude}, Longitude: {self.longitude},
                Elevation: {self.elevation}"""


class Report:
    """A class to represent a weather report."""

    def __init__(
        self,
        station_id: str,
        time: datetime,
        avg_high_temp: float,
        avg_low_temp: float,
        avg_temp: float,
        ext_high_temp: float,
        ext_low_temp: float,
        precipation_total_rain: float,
        precipation_total_snow: float,
        precipation_total: float,
        snow_grnd_last_day: float,
        wind_dir_max_gust: float,
        wind_speed_max_gust: float,
    ) -> None:
        """Initializes a report object."""
        self.station_id = station_id
        self.time = time
        self.avg_high_temp = float(avg_high_temp) if avg_high_temp is not None else None
        self.avg_low_temp = float(avg_low_temp) if avg_low_temp is not None else None
        self.avg_temp = float(avg_temp) if avg_temp is not None else None
        self.ext_high_temp = float(ext_high_temp) if ext_high_temp is not None else None
        self.ext_low_temp = float(ext_low_temp) if ext_low_temp is not None else None
        self.precipation_total_rain = (
            float(precipation_total_rain)
            if precipation_total_rain is not None
            else None
        )
        self.precipation_total_snow = (
            float(precipation_total_snow)
            if precipation_total_snow is not None
            else None
        )
        self.precipation_total = (
            float(precipation_total) if precipation_total is not None else None
        )

        self.snow_grnd_last_day = (
            float(snow_grnd_last_day) if snow_grnd_last_day is not None else None
        )

        self.wind_dir_max_gust = (
            float(wind_dir_max_gust) if wind_dir_max_gust is not None else None
        )

        self.wind_speed_max_gust = (
            float(wind_speed_max_gust) if wind_speed_max_gust is not None else None
        )

    def __str__(self):
        """Returns a string representation of the weather data"""
        return f"""Station_id: {self.station_id},
                    Measurement Time: {self.time},
                    Average high temp: {self.avg_high_temp},
                    Average low temp: {self.avg_low_temp},
                    Average temp: {self.avg_temp},
                    Extreme high temp: {self.ext_high_temp},
                    Extreme low temp: {self.ext_low_temp},
                    Total Rain: {self.precipation_total_rain},
                    Total Snow: {self.precipation_total_snow},
                    Total Precipitation: {self.precipation_total},
                    Ground Snow: {self.snow_grnd_last_day},
                    Wind direction: {self.wind_dir_max_gust},
                    Wind Speed Max: {self.wind_speed_max_gust}"""


class Event:
    """A class to represent a extreme weather event."""

    def __init__(
        self,
        event_id: int,
        event_name: str,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        countries: list[str],
        types: list[str],
    ) -> None:
        """Initializes a report object."""
        self.event_id = event_id
        self.event_name = event_name
        self.latitude = latitude
        self.longitude = longitude
        self.start_time = start_time
        self.end_time = end_time
        self.countries = countries.split(",") if countries else []
        self.types = types.split(",") if types else []

    def __str__(self):
        """Returns a string representation of the weather data"""
        return f"""Event_id: {self.event_id},
                    Event_name: \n{self.event_name}\n,
                    Latitude: {self.latitude},
                    Longitude: {self.longitude},
                    Start_time: {self.start_time},
                    End_time: {self.end_time},
                    Countries: {self.countries},
                    Types: {self.types}"""


class StationAccessor(DBAccessor):
    """Class containing methods specific to the station table.
    Inherits from DBAccessor"""

    def get_all_stations(self) -> list:
        """Get all stations in the table"""
        return self.convert_result_set_to_stations(
            self.conn.exec(f"select * from {Tables.STATIONS}")
        )

    def get_stations_by_country(self, country_code: str) -> list:
        """Get all stations from a country in the table"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.STATIONS} where country=%s", country_code
            )
        )

    def get_stations_by_name(self, name: str) -> list:
        """Get all stations by name in the table"""
        return self.convert_result_set_to_stations(
            self.conn.exec(f"select * from {Tables.STATIONS} where name=%s", name)
        )

    def get_stations_by_elevation_range(
        self, from_elevation: float, to_elevation: Union[float, None] = None
    ) -> list:
        """Get all stations in the table with an elevation between a specified range"""
        if not to_elevation:
            return self.convert_result_set_to_stations(
                self.conn.exec(
                    f"select * from {Tables.STATIONS} where elevation >= %f",
                    from_elevation,
                )
            )

        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.STATIONS} where elevation >= %f and elevation <= %f",
                from_elevation,
                to_elevation,
            )
        )

    def get_stations_by_coordinate_range(
        self, lat_range: tuple[float, float], lon_range: tuple[float, float]
    ) -> list:
        """Get all stations in the table with an coordinates between a specified range"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.STATIONS} where latitude >= %f and latitude <= %f and longitude >= %f and longitude <= %f",
                lat_range[0],
                lat_range[1],
                lon_range[0],
                lon_range[1],
            )
        )

    def convert_result_set_to_stations(self, query_result: list) -> list:
        """Method to convert the results of a query to a python object"""
        return [
            Station(result[0], result[1], result[2], result[3], result[4], result[5])
            for result in query_result
        ]

    def show_indexs(self) -> list:
        return self.conn.exec(f"show indexes from {Tables.HISTORY}")

    def create_index_on_date(self):
        self.conn.exec(
            f"create index date_index on {Tables.HISTORY} (MEASUREMENT_DATE)"
        )

    def drop_index_on_date(self):
        self.conn.exec(f"alter table {Tables.HISTORY} drop index date_index")


class ReportAccessor(StationAccessor):
    """Class containing methods specific to the reports/history table.
    Inherits from DBAccessor"""

    def get_all_reports(self) -> list[Report]:
        """Get all weather reports"""
        return self.convert_result_set_to_weather_history(
            self.conn.exec(f"select * from {Tables.HISTORY}")
        )

    def get_reports_by_station(self, station_id: str) -> list[Report]:
        """Get all weather reports for a station"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.HISTORY} where station=%s order by measurement_date desc",
                station_id,
            )
        )

    def get_reports_by_time_range(
        self, start_time: datetime, end_time: datetime
    ) -> list:
        """Get all weather reports between a range of datetimes"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.HISTORY} where measurement_date >= %s and measurement_date <= %s",
                start_time,
                end_time,
            )
        )

    def get_all_stations_and_reports(self) -> list:
        """Get all stations along with their reports"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                f"select * from {Tables.STATIONS} join {Tables.HISTORY} on {Tables.STATIONS}.station_id={Tables.HISTORY}.station"
            )
        )

    def get_stations_and_reports_by_country(self, country_code: str) -> list:
        """Get all stations along with their reports for a certain country"""
        return self.convert_result_set_to_stations(
            self.conn.exec(
                "select * "
                + f"from {Tables.STATIONS} join {Tables.HISTORY} "
                + f"on {Tables.STATIONS}.station_id={Tables.HISTORY}.station "
                + f"where {Tables.STATIONS}.country=%s",
                country_code,
            )
        )

    def get_oldest_report_time(self) -> datetime:
        """Get the oldest weather report"""
        report_date = self.conn.exec(
            f"select min(measurement_date) from {Tables.HISTORY}"
        )

        if not report_date:
            return datetime.now()

        report_date = report_date[0][0]

        if not report_date:
            return datetime.now()
        # TODO beautiful
        print(report_date)
        return datetime(report_date.year, report_date.month, report_date.day)

    def get_nearest_date_report_by_station(
        self, station_id: str, time: datetime
    ) -> Union[Report, None]:
        """Get the nearest weather report to a certain datetime"""
        report = self.convert_result_set_to_weather_history(
            self.conn.exec(
                f"select * from {Tables.HISTORY} where station=%s order by abs(datediff(%s, measurement_date)) asc limit 1",
                station_id,
                time,
            )
        )
        if not report:
            return None
        return report[0]

    def get_temperature_avgs_by_month(
        self, month: int, year: int
    ) -> dict[tuple[float, float], float]:
        data = self.conn.exec(
            "select latitude, longitude, avg_temp "
            + f"from {Tables.HISTORY}, {Tables.STATIONS} "
            + "where month(measurement_date)=%s "
            + "and year(measurement_date)=%s "
            + f"and {Tables.HISTORY}.station={Tables.STATIONS}.station_id",
            month,
            year,
        )
        return {
            (float(row[0]), float(row[1])): float(row[2])
            for row in data
            if None not in row
        }

    def get_precipitation_totals_by_month(
        self, month: int, year: int
    ) -> dict[tuple[float, float], float]:
        data = self.conn.exec(
            "select latitude, longitude, precip_total "
            + f"from {Tables.HISTORY}, {Tables.STATIONS} "
            + "where month(measurement_date)=%s and year(measurement_date)=%s "
            + f"and {Tables.HISTORY}.station={Tables.STATIONS}.station_id",
            month,
            year,
        )
        return {
            (float(row[0]), float(row[1])): float(row[2])
            for row in data
            if None not in row
        }

    def get_least_temperature_avg(self) -> float:
        temp = self.conn.exec(f"select min(avg_temp) from {Tables.HISTORY}")

        if temp and temp[0][0]:
            return float(temp[0][0])
        return 0.0

    def get_greatest_temperature_avg(self) -> float:
        temp = self.conn.exec(f"select max(avg_temp) from {Tables.HISTORY}")

        if temp and temp[0][0]:
            return float(temp[0][0])
        return 0.0

    def get_least_precipitation_total(self) -> float:
        prec = self.conn.exec(f"select min(precip_total) from {Tables.HISTORY}")

        if prec and prec[0][0]:
            return float(prec[0][0])
        return 0.0

    def get_greatest_precipitation_total(self) -> float:
        prec = self.conn.exec(f"select max(precip_total) from {Tables.HISTORY}")

        if prec and prec[0][0]:
            return float(prec[0][0])
        return 0.0

    def convert_result_set_to_weather_history(self, query_result: list) -> list[Report]:
        """Method to convert the results of a query to a python object"""
        measurements = [
            Report(
                result[0],
                result[1],
                result[2],
                result[3],
                result[4],
                result[5],
                result[6],
                result[7],
                result[8],
                result[9],
                result[10],
                result[11],
                result[12],
            )
            for result in query_result
        ]
        return measurements


class ExtremeWeatherAccessor(DBAccessor):
    """A class to access the extreme weather database."""

    def _round_down_to_decade(self, year: int) -> int:
        return (year // 10) * 10

    def get_all_events(self):
        """Get all events from the database."""
        return self.convert_result_set_to_event(
            self.conn.exec(
                """
                SELECT
                    e.EVENT_ID,
                    e.ITEM_LABEL,
                    e.LATITUDE,
                    e.LONGITUDE,
                    e.START_TIME,
                    e.END_TIME,
                    GROUP_CONCAT(DISTINCT c.COUNTRY_ID) AS countries,
                    GROUP_CONCAT(DISTINCT t.TYPE_ID) AS types
                FROM
                    Events e
                LEFT JOIN
                    EventCountries ec ON e.EVENT_ID = ec.EVENT_ID
                LEFT JOIN
                    Countries c ON ec.COUNTRY_ID = c.COUNTRY_ID
                LEFT JOIN
                    EventTypes et ON e.EVENT_ID = et.EVENT_ID
                LEFT JOIN
                    Types t ON et.TYPE_ID = t.TYPE_ID
                GROUP BY
                    e.EVENT_ID;
                """
            )
        )

    def get_active_events_in_time_range(self, time_from: datetime, time_to: datetime):

        return self.convert_result_set_to_event(
            self.conn.exec(
                f"""
                SELECT
                    e.EVENT_ID,
                    e.ITEM_LABEL,
                    e.LATITUDE,
                    e.LONGITUDE,
                    e.START_TIME,
                    e.END_TIME,
                    GROUP_CONCAT(DISTINCT c.COUNTRY_ID) AS countries,
                    GROUP_CONCAT(DISTINCT t.TYPE_ID) AS types
                FROM
                    Events e
                LEFT JOIN
                    EventCountries ec ON e.EVENT_ID = ec.EVENT_ID
                LEFT JOIN
                    Countries c ON ec.COUNTRY_ID = c.COUNTRY_ID
                LEFT JOIN
                    EventTypes et ON e.EVENT_ID = et.EVENT_ID
                LEFT JOIN
                    Types t ON et.TYPE_ID = t.TYPE_ID
                WHERE
                    e.START_TIME <= '{time_to}' AND e.END_TIME >= '{time_from}'
                GROUP BY
                    e.EVENT_ID;
                """
            )
        )

    def get_oldest_event_decade(self) -> datetime:
        event_date = self.conn.exec("SELECT min(START_TIME) FROM Events;")

        if not event_date:
            return datetime.now()

        event_date = event_date[0][0]

        return datetime(self._round_down_to_decade(event_date.year), 1, 1)

    def get_all_event_times(self) -> list[datetime]:
        event_dates = self.conn.exec("SELECT distinct(START_TIME) FROM Events;")

        if not event_dates:
            return [datetime.now()]

        return [
            event_date[0] for event_date in event_dates if event_date[0] is not None
        ]

    def get_events_by_country(self, country):
        return self.convert_result_set_to_event(
            self.conn.exec(
                f"""
                SELECT
                    e.EVENT_ID,
                    e.ITEM_LABEL,
                    e.LATITUDE,
                    e.LONGITUDE,
                    e.START_TIME,
                    e.END_TIME,
                    GROUP_CONCAT(DISTINCT c.COUNTRY_ID) AS countries,
                    GROUP_CONCAT(DISTINCT t.TYPE_ID) AS types
                FROM
                    Events e
                LEFT JOIN
                    EventCountries ec ON e.EVENT_ID = ec.EVENT_ID
                LEFT JOIN
                    Countries c ON ec.COUNTRY_ID = c.COUNTRY_ID
                LEFT JOIN
                    EventTypes et ON e.EVENT_ID = et.EVENT_ID
                LEFT JOIN
                    Types t ON et.TYPE_ID = t.TYPE_ID
                WHERE
                    c.COUNTRY_ID = '{country}'
                GROUP BY
                    e.EVENT_ID;
                """
            )
        )

    def get_events_by_type(self, type):
        return self.convert_result_set_to_event(
            self.conn.exec(
                f"""
                SELECT
                    e.EVENT_ID,
                    e.ITEM_LABEL,
                    e.LATITUDE,
                    e.LONGITUDE,
                    e.START_TIME,
                    e.END_TIME,
                    GROUP_CONCAT(DISTINCT c.COUNTRY_ID) AS countries,
                    GROUP_CONCAT(DISTINCT t.TYPE_ID) AS types
                FROM
                    Events e
                LEFT JOIN
                    EventCountries ec ON e.EVENT_ID = ec.EVENT_ID
                LEFT JOIN
                    Countries c ON ec.COUNTRY_ID = c.COUNTRY_ID
                LEFT JOIN
                    EventTypes et ON e.EVENT_ID = et.EVENT_ID
                LEFT JOIN
                    Types t ON et.TYPE_ID = t.TYPE_ID
                WHERE
                    t.TYPE_ID = '{type}'
                GROUP BY
                    e.EVENT_ID;
                """
            )
        )

    def get_events_by_country_and_type(self, country, type):
        return self.convert_result_set_to_event(
            self.conn.exec(
                f"""
                SELECT
                    e.EVENT_ID,
                    e.ITEM_LABEL,
                    e.LATITUDE,
                    e.LONGITUDE,
                    e.START_TIME,
                    e.END_TIME,
                    GROUP_CONCAT(DISTINCT c.COUNTRY_ID) AS countries,
                    GROUP_CONCAT(DISTINCT t.TYPE_ID) AS types
                FROM
                    Events e
                LEFT JOIN
                    EventCountries ec ON e.EVENT_ID = ec.EVENT_ID
                LEFT JOIN
                    Countries c ON ec.COUNTRY_ID = c.COUNTRY_ID
                LEFT JOIN
                    EventTypes et ON e.EVENT_ID = et.EVENT_ID
                LEFT JOIN
                    Types t ON et.TYPE_ID = t.TYPE_ID
                WHERE
                    c.COUNTRY_ID = '{country}'
                    AND t.TYPE_ID = '{type}'
                GROUP BY
                    e.EVENT_ID;
                """
            )
        )

    def convert_result_set_to_event(self, query_result: list) -> list:
        """Converts a query result to a list of events."""
        events = [
            Event(
                result[0],  # event_id
                result[1],  # event_name
                float(result[2]) if result[2] is not None else None,
                # latitude
                float(result[3]) if result[3] is not None else None,
                # longitude
                (
                    datetime.combine(result[4], datetime.min.time())
                    if result[4] is not None
                    else None
                ),  # start_time
                (
                    datetime.combine(result[5], datetime.min.time())
                    if result[5] is not None
                    else None
                ),  # end_time
                result[6],  # countries
                result[7],  # types
            )
            for result in query_result
        ]
        return events
