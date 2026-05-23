"""
Code which runs the data fetching and sanitation and uploading to the database for weather stations
"""

# pylint: disable=duplicate-code, consider-using-with

import sys
import os
from group52.data_retrieval.collect_station_data import collect_station_data
from group52.data_sanitisation.lib.clean_data_formatting import clean_data_formatting
from group52.data_sanitisation.lib.reorder_columns import reorder_columns
from group52.data_sanitisation.lib.prepare_csv import prepare_csv
from group52.db_accessor.db_connector import DBConnection, Databases
from group52.db_accessor.group52 import StationAccessor, Tables

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DIRECTORY_PATH = os.path.join(BASE_DIR, "data_uploading/station_data")

MAPPINGS_DIRECTORY_PATH = os.path.join(
    BASE_DIR, "data_sanitisation/utility/non_history_mappings"
)

MAPPING_1_PATH = os.path.join(
    MAPPINGS_DIRECTORY_PATH, "1.non_history_refinement_mappings.json"
)
MAPPING_2_PATH = os.path.join(MAPPINGS_DIRECTORY_PATH, "2.extracted_mappings.json")
MAPPING_3_PATH = os.path.join(
    MAPPINGS_DIRECTORY_PATH, "3.type_conversion_mappings.json"
)
MAPPING_4_PATH = os.path.join(MAPPINGS_DIRECTORY_PATH, "4.reordering.txt")

FILE_1_PATH = os.path.join(DIRECTORY_PATH, "1.non_history_data.json")
FILE_2_PATH = os.path.join(DIRECTORY_PATH, "2.extracted_non_history_data.json")
FILE_3_PATH = os.path.join(DIRECTORY_PATH, "3.cleaned_non_history_data.json")
FILE_4_PATH = os.path.join(DIRECTORY_PATH, "4.final_non_history_data.json")
FILE_5_PATH = os.path.join(DIRECTORY_PATH, "5.reordered_final_non_history_data")
FILE_6_PATH = os.path.join(DIRECTORY_PATH, "6.non_history_data_csv.csv")

DATE_PATH = os.path.join(BASE_DIR, "data_uploading/date_data")
LAST_UPLOAD_PATH = os.path.join(DATE_PATH, "last_station_upload.txt")


def download_clean_upload_stations(database_to_use: Databases):
    """Fetchs, cleans and uploads station data

    Args:
        database_to_use (Database): the databse (either dev or prod) to upload the data to

    """

    # First make sure station data directory exists
    directory_exists = os.path.exists(DIRECTORY_PATH)
    if not directory_exists:
        os.makedirs(DIRECTORY_PATH)
    date_directory_exists = os.path.exists(DATE_PATH)
    if not date_directory_exists:
        os.makedirs(DATE_PATH)
    open(LAST_UPLOAD_PATH, "a+", encoding="UTF-8").close()
    # Get data from wikidata
    print("Getting station data...", end="")
    sys.stdout.flush()
    collect_station_data(FILE_1_PATH, LAST_UPLOAD_PATH)
    print("Done.")

    # Apply mappings to eventually save as a CSV
    print("Applying first mapping...", end="")
    sys.stdout.flush()
    clean_data_formatting(MAPPING_1_PATH, FILE_1_PATH, FILE_2_PATH)
    print("Done.")

    print("Applying second mapping...", end="")
    sys.stdout.flush()
    clean_data_formatting(MAPPING_2_PATH, FILE_2_PATH, FILE_3_PATH)
    print("Done.")

    print("Applying third mapping...", end="")
    sys.stdout.flush()
    clean_data_formatting(MAPPING_3_PATH, FILE_3_PATH, FILE_4_PATH)
    print("Done.")

    print("Reordering columns...", end="")
    sys.stdout.flush()
    reorder_columns(MAPPING_4_PATH, FILE_4_PATH, FILE_5_PATH)
    print("Done.")

    print("Saving as CSV...", end="")
    sys.stdout.flush()
    prepare_csv(FILE_5_PATH, FILE_6_PATH)
    print("Done.")

    # Upload the data to the database
    print("Settinng up DB and stations table...", end="")
    sys.stdout.flush()
    with DBConnection(database_to_use) as conn:
        print("Done.")
        accessor = StationAccessor(conn)

        print("Uploading CSV to STATIONS...", end="")
        sys.stdout.flush()
        accessor.load_data(Tables.STATIONS, FILE_6_PATH)
        print("Done.")

        f = open(FILE_6_PATH, "r", encoding="UTF-8")
        print("Uploaded " + str(len(f.read().splitlines())) + " stations")
        f.close()

        print("There are now " + str(len(accessor.get_all_stations())) + " stations")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "download_clean_upload_stations: requires 1 positional argument"
        )

    if sys.argv[1] != "DEV" and sys.argv[1] != "PROD":
        raise SystemExit(
            "download_clean_upload_stations: database must either be 'DEV' or 'PROD'"
        )

    print("download_clean_upload_stations will use '" + sys.argv[1] + "' as the db")

    if sys.argv[1] == "DEV":
        download_clean_upload_stations(Databases.DEV)
    if sys.argv[1] == "PROD":
        download_clean_upload_stations(Databases.PROD)
