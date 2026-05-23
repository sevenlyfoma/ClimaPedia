"""Code which runs the data fetching sanitation and uploading of all data.
Schedules it to be run every day to keep it up to date. Must be run with tmux"""

import time
import sys
import os
import pathlib
import schedule

# pylint: disable=consider-using-with

from group52.data_uploading.download_clean_upload_histories import (
    download_clean_upload_histories,
)
from group52.data_uploading.download_clean_upload_stations import (
    download_clean_upload_stations,
)
from group52.data_uploading.download_clean_upload_extreme_weather import (
    download_clean_upload_extreme_weather,
)
from group52.db_accessor.db_connector import Databases

database_to_use = Databases.DEV

MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())
DATE_PATH = MAIN_PATH + "/date_data"
HISTORY_MODIFIED_DATES_PATH = DATE_PATH + "/history_modified_times.txt"
STALE_HISTORY_PATH = DATE_PATH + "/stale_history_data.txt"
LAST_UPLOAD_PATH = DATE_PATH + "/last_station_upload.txt"


def job():
    """Define the job to be run periodically
    List all tasks to be executed when the job runs
    """

    print("Running stations script", end="")
    sys.stdout.flush()
    download_clean_upload_stations(database_to_use)
    print("Done.")

    print("Running histories script", end="")
    sys.stdout.flush()
    download_clean_upload_histories(database_to_use)
    print("Done.")

    print("Running extreme weather script", end="")
    sys.stdout.flush()
    download_clean_upload_extreme_weather(database_to_use)
    print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("start_upload_daemon: requires 1 positional argument")

    if sys.argv[1] != "DEV" and sys.argv[1] != "PROD":
        raise SystemExit("start_upload_daemon: database must either be 'DEV' or 'PROD'")

    print("start_upload_daemon will use '" + sys.argv[1] + "' as the db")

    if sys.argv[1] == "DEV":
        database_to_use = Databases.DEV
    if sys.argv[1] == "PROD":
        database_to_use = Databases.PROD

    # Clear the files for keeping track
    print("Clear time tracking files")
    if not os.path.exists(DATE_PATH):
        os.makedirs(DATE_PATH)
    open(HISTORY_MODIFIED_DATES_PATH, "w", encoding="UTF-8").close()
    open(STALE_HISTORY_PATH, "w", encoding="UTF-8").close()
    open(LAST_UPLOAD_PATH, "w", encoding="UTF-8").close()
    print("Done.")

    job()

    # schedule the job to run periodically
    schedule.every().day.at("01:00").do(job)

    while True:
        schedule.run_pending()
        time.sleep(60)
