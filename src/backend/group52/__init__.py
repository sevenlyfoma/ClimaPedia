"""Base script for group52"""

from datetime import datetime

from flask import Blueprint, request
from typing import Union

from group52.resolvers import get_logger
from group52.resolvers.request_processors import (
    process_request__reports,
    process_request__reports_part,
    process_request__temperature,
    process_request__precipitation,
    process_request__extreme_events,
)

"""
Defines the group52 endpoint resolvers.
"""

# Don't change this line!
blueprint = Blueprint("group52", __name__)


def _parse_meta(request_args: dict[str, str]) -> bool:
    """
    Parses the meta parameter.

    Args:
        request_args: The request arguments.

    Returns:
        Whether metadata is requested.
    """
    return "meta" in request_args and "1" == request_args["meta"]


def _parse_country(request_args: dict[str, str]) -> Union[str, None]:
    """
    Parses the country parameter.

    Args:
        request_args: The request arguments.

    Returns:
        The country code to get reports for.
    """
    return request_args["country"] if "country" in request_args else None


def _iso_trailing_z_to_datetime(iso: str) -> datetime:
    """
    Converts an ISO date string with a trailing Z character to `datetime`.

    Args:
        iso: The date string.

    Returns:
        The `datetime`.
    """
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _parse_time(
    request_args: dict[str, str]
) -> Union[tuple[datetime, datetime], tuple[datetime, None], tuple[None, None]]:
    """
    Parses the time parameter.

    Args:
        request_args: The request arguments.

    Returns:
        The parsed time.
    """
    try:
        if "time" in request_args:
            return (
                _iso_trailing_z_to_datetime(request_args["time"]),
                None,
            )
        if "starttime" in request_args and "endtime" in request_args:
            return (
                _iso_trailing_z_to_datetime(request_args["starttime"]),
                _iso_trailing_z_to_datetime(request_args["endtime"]),
            )
    except ValueError:
        get_logger().error("Failed to parse time: %s", str(request_args))
        pass

    return (
        None,
        None,
    )


@blueprint.route("/reports", methods=["GET"])
def reports():
    """
    Resolves the `reports` endpoint.

    Args:
        time: The time to get reports for.
        meta: Whether metadata is requested.
              If `1`, the response will only contain a meta object.
              Otherwise, the response will not contain any meta information.
        country: The country code to get reports for.
    """
    is_meta = _parse_meta(request.args)
    country_code = _parse_country(request.args)

    return process_request__reports(is_meta, country_code=country_code)


@blueprint.route("/reports/<string:station_id>", methods=["GET"])
def reports_part(station_id: str):
    """
    Resolves the `reports` part endpoint.

    Args:
        station_id: The ID of the station to get the timewise-nearest report for.
    """
    time, _ = _parse_time(request.args)

    return process_request__reports_part(station_id, time)


@blueprint.route("/temperature", methods=["GET"])
def temperature():
    """
    Resolves the `temperatures` endpoint.
    """
    is_meta = _parse_meta(request.args)
    time, _ = _parse_time(request.args)

    return process_request__temperature(is_meta, time)


@blueprint.route("/precipitation", methods=["GET"])
def precipitation():
    """
    Resolves the `precipitation` endpoint.
    """
    is_meta = _parse_meta(request.args)
    time, _ = _parse_time(request.args)

    return process_request__precipitation(is_meta, time)


@blueprint.route("/extreme-events", methods=["GET"])
def extreme_events():
    """
    Resolves the `extreme-events` endpoint.
    """
    is_meta = _parse_meta(request.args)
    time_from, time_to = _parse_time(request.args)

    return process_request__extreme_events(is_meta, time_from, time_to)
