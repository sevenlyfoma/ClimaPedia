import os
import re

from datetime import datetime

from flask import Blueprint, request

from .prediction_db import PredictionDB
from .temperature_overlay import TemperatureOverlay
from .extreme_overlay import ExtremeOverlay

blueprint = Blueprint("group51", __name__)

FLASK_ENV = os.getenv("FLASK_ENV", "development")

DB_HOST = "localhost" if FLASK_ENV == "development" else os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_DATABASE = os.getenv("MYSQL_DATABASE")


def init_db() -> PredictionDB:
    """Initialise the database but don't open it.

    Returns:
        A new unopened database connection.
    """
    return PredictionDB(DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE, port=DB_PORT)


@blueprint.route("/predict/")
@blueprint.route("/actual/")
def temperature_overlay():
    """Temperature overlays"""
    is_pred = re.search(r"predict", request.path) is not None

    temp_overlay = TemperatureOverlay(init_db(), is_pred=is_pred)
    if request.args.get("meta", "0") == "1":
        return temp_overlay.get_meta()

    dt_str = request.args.get("time")
    if dt_str is None:
        return {}, 400

    return temp_overlay.get_response(datetime.strptime(dt_str, "%Y-%m-%d:%H:%M:%S"))


@blueprint.route("/extreme_cold/")
def extreme_cold_overlay():
    """Extreme cold overlay."""
    extreme_overlay = ExtremeOverlay(init_db())

    if request.args.get("meta", "0") == "1":
        return extreme_overlay.get_meta()

    dt_str = request.args.get("time")
    if dt_str is None:
        return {}, 400

    return extreme_overlay.get_response(datetime.strptime(dt_str, "%Y-%m-%d:%H:%M:%S"))
