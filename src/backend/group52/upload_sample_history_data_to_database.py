"""Code which runs the data fetching and sanitation.
Schedules it to be run every day to keep it up to date.
Adapted from run_data.py created by ac481
"""

import time
import sys
import os
import schedule

from data_retrieval.get_histories import get_data_with_limit
from data_sanitisation.lib.clean_data_formatting import clean_data_formatting
from data_sanitisation.lib.reorder_columns import reorder_columns
from data_sanitisation.lib.prepare_csv import prepare_csv
from data_sanitisation.lib.clean_all_histories import clean_all_histories
from db_accessor.db_accessor import create_connection_no_db, create_connection_to_db
from db_accessor.db_accessor import (
    create_db,
    create_table,
    insert_data_by_csv,
    end_connection,
)


def add_csv_to_db(filename: str, table_name: str, schema_file: str):
    """Method which add cleaned csv data to the database

    Args:
        filename (str): the name of the file that contains the CSV data
        table_name (str): name of table to add data into
        schema_file (str): file containing schema for table
    """
    server = create_connection_no_db()
    create_db(server)
    db = create_connection_to_db()
    create_table(db, table_name, schema_file)
    insert_data_by_csv(db, table_name, filename)
    end_connection(db)


def job():
    """Define the job to be run periodically
    List all tasks to be executed when the job runs
    """
    print("Getting data...", end="")
    sys.stdout.flush()
    get_data_with_limit("./non_history_data/1.non_history_data.json", True, 4)
    print("Done.")
    print("Cleaning data...", end="")
    sys.stdout.flush()
    clean_data_formatting(
        "./data_sanitisation/utility/non_history_mappings/1.non_history_refinement_mappings.json",
        "./non_history_data/1.non_history_data.json",
        "./non_history_data/2.extracted_non_history_data.json",
    )
    clean_data_formatting(
        "./data_sanitisation/utility/non_history_mappings/2.extracted_mappings.json",
        "./non_history_data/2.extracted_non_history_data.json",
        "./non_history_data/3.cleaned_non_history_data.json",
    )
    clean_data_formatting(
        "./data_sanitisation/utility/non_history_mappings/3.type_conversion_mappings.json",
        "./non_history_data/3.cleaned_non_history_data.json",
        "./non_history_data/4.final_non_history_data.json",
    )
    print("Done.")
    print("Reordering data and making CSV...", end="")
    sys.stdout.flush()
    reorder_columns(
        "./data_sanitisation/utility/non_history_mappings/4.reordering.txt",
        "./non_history_data/4.final_non_history_data.json",
        "./non_history_data/5.reordered_final_non_history_data",
    )
    prepare_csv(
        "./non_history_data/5.reordered_final_non_history_data",
        "./non_history_data/6.non_history_data_csv.csv",
    )
    print("Done.")

    print("Cleaning all monthly weather histories...", end="")
    sys.stdout.flush()
    clean_all_histories(
        "data_sanitisation/utility/monthly_history_mappings/monthly_reorderings.txt",
        "example_data",
        "example_data_cleaned",
    )
    print("Done")

    data_list = os.listdir("example_data_cleaned")

    for i in data_list:
        print("Adding CSV contents of " + i + " to weather_data table...", end="")
        sys.stdout.flush()
        add_csv_to_db(
            "example_data_cleaned/" + i, "weather_data", "db_accessor/historySchema.txt"
        )
        print("Done")

    sys.stdout.flush()


job()

schedule.every().day.at("01:00").do(job)  # schedule the job to run periodically

while True:
    schedule.run_pending()
    time.sleep(60)
