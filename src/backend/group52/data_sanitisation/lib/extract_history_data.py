"""Module to extract history data"""

import json
import sys

import numpy as np
import pandas as pd


def main():
    """Main function for running body function with cmd args"""
    extract_history_data(sys.argv[1], sys.argv[2])


def extract_history_data(origin_file_name, destination_file_name):
    """
    Takes original history file, extracts fields and history data and turns it into a
    new json file with only that info in a sensical manner

    Args:
        origin_file_name (string):              filepath to the json to which the mappings will
                                                be applied
        destination_file_name (string):         filepath to the json in which the altered
                                                json will be stored
    """

    # Open origin file and load a json object of it
    with open(origin_file_name, "r+", encoding="UTF-8") as origin_file:

        data = json.load(origin_file)

    # Get a list of fields with extra data
    fields = data["weather_history"]["schema"]["fields"]

    # Get the data itself
    weather_data = data["weather_history"]["data"]

    field_names = []

    # Extra only the field name
    count = 0
    for i in fields:
        field_names.append(i["name"])

    # Create a data frame with those fields and data
    df = pd.DataFrame(weather_data, columns=field_names)

    # Remove Nans
    df = df.replace({np.nan: None})

    # Find weather station id from its file name
    start = 0
    count = 0
    for i in origin_file_name:
        count += 1
        if i == "/":
            start = count
    # Insert in column with station name and one for id for csv parsing ease
    df.insert(0, "Station", origin_file_name[start:-6])
    # Reconvert to json
    df.to_json(destination_file_name, orient="records", indent=1, date_format="iso")


if __name__ == "__main__":
    main()
