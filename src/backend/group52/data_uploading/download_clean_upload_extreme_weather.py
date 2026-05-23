"""
Code which runs the data fetching and sanitation and
uploading to the database for extreme weather data
"""

import sys
import os
import pathlib

# pylint: disable=duplicate-code, consider-using-with

from group52.data_retrieval.get_extreme_weather_data import data_to_file
from group52.data_sanitisation.lib.clean_and_save_extreme_weather import (
    convert_json_to_csvs,
)
from group52.db_accessor.db_connector import DBConnection, Databases
from group52.db_accessor.group52 import ExtremeWeatherAccessor

MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

DIRECTORY_PATH = MAIN_PATH + "/extreme_weather_data"

CLEANED_PATH = DIRECTORY_PATH + "/cleaned"

DOWNLOAD_PATH = DIRECTORY_PATH + "/download"

JSON_FILE_PATH = DOWNLOAD_PATH + "/extreme_weather.json"


def download_clean_upload_extreme_weather(database_to_use: Databases):
    """Fetchs, cleans and uploads extreme weather data

    Args:
        database_to_use (Database): the databse (either dev or prod) to upload the data to

    """

    # Check all directories exist, if they dont, make them
    if not os.path.exists(DIRECTORY_PATH):
        os.makedirs(DIRECTORY_PATH)

    if not os.path.exists(CLEANED_PATH):
        os.makedirs(CLEANED_PATH)

    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)

    # First get all extreme weather data and save it into json
    print("Finding all extreme weather data points.")
    sys.stdout.flush()
    data_to_file(JSON_FILE_PATH)
    print("Done.")

    # Run sanitisation scripts on all wiki data
    print("Cleaning and saving all extreme weather data to CSVs.")
    sys.stdout.flush()
    convert_json_to_csvs(JSON_FILE_PATH, CLEANED_PATH)
    print("Done")

    # Get a list of all cleaned wiki data
    data_list = [
        "Events.csv",
        "Types.csv",
        "Countries.csv",
        "EventTypes.csv",
        "EventCountries.csv",
    ]

    # Create connection to DB, create clean table for histories
    print("Setting up DB and EXTREME WEATHER tables...", end="")
    sys.stdout.flush()
    with DBConnection(database_to_use) as conn:
        print("Done.")
        accessor = ExtremeWeatherAccessor(conn)

        for i in data_list:
            filename = i.split(".")[
                0
            ]  # Table name is equal to the filename without the extension
            print(
                "Adding CSV contents of " + i + " to EXTREME WEATHER table...", end=""
            )
            sys.stdout.flush()
            print(filename)
            accessor.load_data(filename, CLEANED_PATH + "/" + i)
            print("Done")

        print(
            "There are now "
            + str(len(accessor.get_all_events()))
            + " items in EXTREME WEATHER"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "download_clean_upload_extreme_weather: requires 1 positional argument"
        )

    if sys.argv[1] != "DEV" and sys.argv[1] != "PROD":
        raise SystemExit(
            "download_clean_upload_extreme_weather: database must either be 'DEV' or 'PROD'"
        )

    print(
        "download_clean_upload_extreme_weather will use '" + sys.argv[1] + "' as the db"
    )

    if sys.argv[1] == "DEV":
        download_clean_upload_extreme_weather(Databases.DEV)

    if sys.argv[1] == "PROD":
        download_clean_upload_extreme_weather(Databases.PROD)
