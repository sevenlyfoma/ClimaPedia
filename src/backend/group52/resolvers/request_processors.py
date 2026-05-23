"""
This module defines functions for processing request to each of this API's endpoints.
"""

from datetime import datetime
from typing import Union

from group52.resolvers import (
    get_extreme_accessor,
    get_report_accessor,
    get_logger,
    get_station_accessor,
)
from group52.resolvers.response_makers import (
    make_response__extreme_events,
    make_response__extreme_events_meta,
    make_response__precipitation,
    make_response__precipitation_meta,
    make_response__reports,
    make_response__reports_meta,
    make_response__reports_part,
    make_response__temperature,
    make_response__temperature_meta,
)


def process_request__reports(
    is_meta: bool = False, country_code: Union[str, None] = None
) -> str:
    """
    Processes the `reports` request.

    Args:
        meta: Whether metadata is requested.
              If `True`, the response will only contain a meta object.
              Otherwise, the response will not contain any meta information.
    Returns:
        The response JSON string.
    """
    logger = get_logger()
    strreq = f"(is_meta={is_meta}, country_code={country_code})"
    logger.info("Processing reports_view request: %s", strreq)

    station_acc, dblock = get_station_accessor()
    report_acc, _ = get_report_accessor()

    if station_acc is None:
        logger.error("Failed to get db accessor")
        return "{}"

    stations = []

    try:
        if country_code:
            with dblock:
                stations = station_acc.get_stations_by_country(country_code)
        else:
            with dblock:
                stations = station_acc.get_all_stations()
        logger.info("Found %d stations for: %s", len(stations), strreq)
    except ValueError as e:
        logger.error("Failed to get stations: %s", str(e))

    if is_meta:
        with dblock:
            oldest_time = report_acc.get_oldest_report_time()
        return make_response__reports_meta(stations, oldest_time)

    return make_response__reports(stations)


def process_request__reports_part(station_id: str, time: Union[datetime, None]) -> str:
    """
    Processes the `reports` part request.

    Args:
        station_id: The ID of the station.
    Returns:
        The response JSON string.
    """
    logger = get_logger()
    strreq = f"(station_id={station_id})"
    logger.info("Processing reports_part request: %s", strreq)

    report_acc, dblock = get_report_accessor()
    if report_acc is None:
        logger.error("Failed to get db accessor")
        return "{}"

    if not time:
        time = datetime.now()

    try:
        with dblock:
            report = report_acc.get_nearest_date_report_by_station(station_id, time)

        if report:
            logger.info(
                "Found nearest report at %s for: (%s, %s) at ",
                report.time,
                station_id,
                time,
            )
        else:
            logger.info(
                "No nearest report found for station=%s, date=%s", station_id, time
            )

        return make_response__reports_part(station_id, report)

    except Exception as e:
        logger.error(
            "Failed to get nearest report for station %s: %s", station_id, str(e)
        )

    return "{}"


def process_request__temperature(is_meta: bool, time: Union[datetime, None]) -> str:
    """
    Processes the `temperature` request.

    Args:
        time: The time to get temperature data for.
    Returns:
        The response JSON string.
    """
    strreq = f"(is_meta={is_meta}, time={time})"

    logger = get_logger()
    logger.info("Processing temperature request: %s", strreq)
    report_acc, dblock = get_report_accessor()

    if report_acc is None:
        logger.error("Failed to get db accessor")
        return "{}"

    if is_meta:
        with dblock:
            return make_response__temperature_meta(report_acc.get_oldest_report_time())

    if not time:
        time = datetime.now()

    try:
        with dblock:
            coords_to_temperature = report_acc.get_temperature_avgs_by_month(
                time.month, time.year
            )
            least_recorded_temperature = report_acc.get_least_temperature_avg()
            greatest_recorded_temperature = report_acc.get_greatest_temperature_avg()

        logger.info(
            "Found least recorded avg temperature=%f and greatest recorded avg temperature=%d",
            least_recorded_temperature,
            greatest_recorded_temperature,
        )

        if coords_to_temperature is not None:  # Allow dict, catch None only.
            logger.info(
                "Found %d temperature values for month=%02d-%04d",
                len(coords_to_temperature),
                time.month,
                time.year,
            )
            return make_response__temperature(
                coords_to_temperature,
                least_recorded_temperature,
                greatest_recorded_temperature,
            )
    except Exception as e:
        logger.error("Failed to get temperatures: %s", str(e))

    return "{}"


def process_request__precipitation(is_meta: bool, time: Union[datetime, None]) -> str:
    """
    Processes the `precipitation` request.

    Args:
        time: The time to get precipitation data for.
    Returns:
        The response JSON string.
    """
    strreq = f"(is_meta={is_meta}, time={time})"
    logger = get_logger()
    logger.info("Processing precipitation request %s", strreq)
    report_acc, dblock = get_report_accessor()

    if report_acc is None:
        logger.error("Failed to get db accessor")
        return "{}"

    if is_meta:
        with dblock:
            return make_response__precipitation_meta(
                report_acc.get_oldest_report_time()
            )

    if not time:
        time = datetime.now()

    try:
        with dblock:
            least_recorded_precipitation = report_acc.get_least_precipitation_total()
            greatest_recorded_precipitation = (
                report_acc.get_greatest_precipitation_total()
            )

            coords_to_precipitation = report_acc.get_precipitation_totals_by_month(
                time.month, time.year
            )

        logger.info(
            "Found least recorded precipitation=%f and greatest recorded precipitation=%d",
            least_recorded_precipitation,
            greatest_recorded_precipitation,
        )

        if (
            coords_to_precipitation is not None
        ):  # As above, allow empty dict, catch None only.
            logger.info(
                "Found %d precipitation values for month=%02d-%04d",
                len(coords_to_precipitation),
                time.month,
                time.year,
            )
            return make_response__precipitation(
                coords_to_precipitation,
                least_recorded_precipitation,
                greatest_recorded_precipitation,
            )
    except Exception as e:
        logger.error("Failed to get precipitation totals: %s", str(e))

    return "{}"


def process_request__extreme_events(
    is_meta: bool, time_from: Union[datetime, None], time_to: Union[datetime, None]
) -> str:
    """
    Processes the `extreme-events` request.

    Args:
        time: The time to get extreme events data for.
    Returns:
        The response JSON string.
    """
    strreq = f"(is_meta={is_meta}, time_from={time_from}, time_to={time_to})"
    logger = get_logger()
    logger.info("Processing extreme-events request: %s", strreq)
    extreme_acc, dblock = get_extreme_accessor()

    if extreme_acc is None:
        logger.error("Failed to get db accessor")
        return "{}"

    if is_meta:
        with dblock:
            return make_response__extreme_events_meta(extreme_acc.get_all_event_times())

    if not time_from or not time_to:
        time_to = datetime.now()
        time_from = datetime(time_to.year - 10, time_to.month, time_to.day)

    try:
        with dblock:
            extreme_events = extreme_acc.get_active_events_in_time_range(
                time_from, time_to
            )

        if extreme_events is not None:  # Allow empty list, catch None only.
            logger.info(
                "Found %d extreme events active in time range (%s, %s)",
                len(extreme_events),
                time_from,
                time_to,
            )
            return make_response__extreme_events(extreme_events)
    except Exception as e:
        logger.error("Failed to get extreme events: %s", str(e))

    return "{}"
