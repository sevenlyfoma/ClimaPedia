"""
Code which runs the data fetching and sanitation and uploading to the database for weather historie
"""

import sys
import os

# pylint: disable=duplicate-code, consider-using-with

from group52.data_retrieval.collect_history_data import collect_history_data
from group52.data_sanitisation.lib.clean_all_histories import clean_all_histories
from group52.db_accessor.db_connector import DBConnection, Databases
from group52.db_accessor.group52 import ReportAccessor, Tables
from group52.data_retrieval.collect_change_dates import collect_change_dates
from group52.data_retrieval.collect_station_data import (
    collect_station_data_with_history,
)

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DIRECTORY_PATH = os.path.join(BASE_PATH, "data_uploading/history_data")

UNCLEANED_PATH = os.path.join(DIRECTORY_PATH, "uncleaned")

CLEANED_PATH = os.path.join(DIRECTORY_PATH, "cleaned")

JSON_FILE_PATH = os.path.join(DIRECTORY_PATH, "1.station_data.json")

MAPPING_PATH = os.path.join(
    BASE_PATH, "data_sanitisation/utility/monthly_history_mappings"
)

MONTHLY_HISTORIES_MAPPING_PATH = os.path.join(MAPPING_PATH, "monthly_reorderings.txt")

DATE_PATH = os.path.join(BASE_PATH, "data_uploading/date_data")

HISTORY_MODIFIED_DATES_PATH = os.path.join(DATE_PATH, "history_modified_times.txt")

STALE_HISTORY_PATH = os.path.join(DATE_PATH, "stale_history_data.txt")


def download_clean_upload_histories(database_to_use: Databases):
    """Fetchs, cleans and uploads hsitory data

    Args:
        database_to_use (Database): the databse (either dev or prod) to upload the data to

    """

    # Check all directories exist, if they dont, make them
    if not os.path.exists(DIRECTORY_PATH):
        os.makedirs(DIRECTORY_PATH)

    if not os.path.exists(UNCLEANED_PATH):
        os.makedirs(UNCLEANED_PATH)

    if not os.path.exists(CLEANED_PATH):
        os.makedirs(CLEANED_PATH)

    if not os.path.exists(DATE_PATH):
        os.makedirs(DATE_PATH)

    open(HISTORY_MODIFIED_DATES_PATH, "a+", encoding="UTF-8").close()
    open(STALE_HISTORY_PATH, "a+", encoding="UTF-8").close()

    # First get all stations with a weather history
    print("Finding weather stations with histories...")
    sys.stdout.flush()
    collect_station_data_with_history(JSON_FILE_PATH)
    print("Done.")

    # Find out which histories are stale

    print("Finding stale weather histories...")
    sys.stdout.flush()
    collect_change_dates(
        JSON_FILE_PATH, HISTORY_MODIFIED_DATES_PATH, STALE_HISTORY_PATH
    )
    print("Done.")

    # Query wikidata for history data and save it
    print("Getting history data...")
    sys.stdout.flush()
    collect_history_data(JSON_FILE_PATH, UNCLEANED_PATH, STALE_HISTORY_PATH)
    print("Done.")

    # Run sanitisation scripts on all wiki data
    print("Cleaning all monthly weather histories...")
    sys.stdout.flush()
    clean_all_histories(MONTHLY_HISTORIES_MAPPING_PATH, UNCLEANED_PATH, CLEANED_PATH)
    print("Done")

    # Get a list of all cleaned wiki data
    data_list = os.listdir(CLEANED_PATH)

    # Create connection to DB, create clean table for histories
    print("Setting up DB and HISTORY table...", end="")
    sys.stdout.flush()
    with DBConnection(database_to_use) as conn:
        print("Done.")
        accessor = ReportAccessor(conn)

        total_uploads = 0
        # Go through every cleaned csv and upload the data
        for i in data_list:
            print("Adding CSV contents of " + i + " to HISTORY table...", end="")
            sys.stdout.flush()
            accessor.load_data(Tables.HISTORY, CLEANED_PATH + "/" + i)
            print("Done")
            f = open(CLEANED_PATH + "/" + i, "r", encoding="UTF-8")
            total_uploads += len(f.read().splitlines())
            f.close()

        print("Uploaded " + str(total_uploads) + " items into HISTORY")
        print(
            "There are now "
            + str(len(accessor.get_all_reports()))
            + " items in HISTORY"
        )


def upload_histories(database_to_use: Databases):
    """Only uploads history data, useful when you dont want to wait 2 hours to fetch the data

    Args:
        database_to_use (Database): the databse (either dev or prod) to upload the data to

    """

    # Get a list of all cleaned wiki data
    data_list = os.listdir(CLEANED_PATH)

    # Create connection to DB, create clean table for histories
    print("Setting up DB and HISTORY table...", end="")
    sys.stdout.flush()
    with DBConnection(database_to_use) as conn:
        print("Done.")
        accessor = ReportAccessor(conn)

        total_uploads = 0
        # Go through every cleaned csv and upload the data
        for i in data_list:
            print("Adding CSV contents of " + i + " to HISTORY table...", end="")
            sys.stdout.flush()
            accessor.load_data(Tables.HISTORY, CLEANED_PATH + "/" + i)
            print("Done")
            f = open(CLEANED_PATH + "/" + i, "r", encoding="UTF-8")
            total_uploads += len(f.read().splitlines())
            f.close()

        print("Uploaded " + str(total_uploads) + " items into HISTORY")
        print(
            "There are now "
            + str(len(accessor.get_all_reports()))
            + " items in HISTORY"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "download_clean_upload_histories: requires 1 positional argument"
        )

    if sys.argv[1] != "DEV" and sys.argv[1] != "PROD":
        raise SystemExit(
            "download_clean_upload_histories: database must either be 'DEV' or 'PROD'"
        )

    print("download_clean_upload_histories will use '" + sys.argv[1] + "' as the db")

    if sys.argv[1] == "DEV":
        download_clean_upload_histories(Databases.DEV)
        # upload_histories(Databases.DEV)

    if sys.argv[1] == "PROD":
        download_clean_upload_histories(Databases.PROD)
        # upload_histories(Databases.PROD)
