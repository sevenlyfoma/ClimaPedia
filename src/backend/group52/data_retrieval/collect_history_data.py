"""Code to get weather history data from WikiData"""

import sys
import json
import os
import requests

# pylint: disable=duplicate-code, consider-using-with, too-many-locals


ENDPOINT_URL = "https://query.wikidata.org/sparql"


def collect_history_data(
    json_file_path: str, storage_directory_path: str, stale_entries_path: str
):
    """Takes a json with "weather_history_value" as a field in a list of objects
    and gets the data from that url, and saves it as ajson file

    Args:
        json_file_path (str): the json file, containing a list of weather station objects
        who have a field "weather_history_value" which is a url to the data

        storage_directory_path (str): the directory that will store the downloaded jsons
        stale_entries_path (str): path to file containing stale weather stations
    """

    # Open the json of all the stations
    with open(json_file_path, encoding="UTF-8") as json_file:
        stations_data = json.load(json_file)

    # Get list of all history files
    # Delete them all, we want fresh data
    for file_name in os.listdir(storage_directory_path):
        os.unlink(storage_directory_path + "/" + file_name)

    stale_entries_file = open(stale_entries_path, mode="r", encoding="UTF-8")

    stale_entries = stale_entries_file.read().splitlines()

    print(stale_entries)

    i = 0
    for result in stations_data:
        # Get the url for the history data page
        url = result["weather_history"]["value"]
        qcode = result["item"]["value"][
            result["item"]["value"].rfind("/") :  # noqa: E203
        ]
        # Check we're on the monthly data instead of the almanac data
        # And check data needs to be updated
        if "Monthly" in url and qcode in stale_entries:
            i += 1

            # All requests can cause exceptions
            try:
                # Make the request to the webpage with timeout of 10 seconds
                r = requests.get(url, timeout=10)
                # Turn request into a json object
                table = r.json()

                # Create object to save data into
                to_save = {}

                # Put request into save object in format
                # that cleaning functions expect
                to_save["weather_history"] = table
                # Prepare to save object
                json_object = json.dumps(to_save, indent=4)

                # Create appropriate file path
                filename = storage_directory_path
                filename += result["item"]["value"][
                    result["item"]["value"].rfind("/") :  # noqa: E203
                ]
                filename += "M" + ".json"

                # Save the data
                with open(filename, "w+", encoding="utf-8") as outfile:
                    outfile.write(json_object)

                # Log that we've saved it with a count
                print("saved history data " + str(i) + ": " + filename)

            except requests.exceptions.Timeout:
                print("Request for weather history timed out")
            except requests.exceptions.RequestException:
                # catchall for any other exceptions in getting the data
                print("Problem getting weather history...")
            except ValueError:
                print("Incorrect JSON syntax for weather history")


def collect_history_data_with_limit(
    json_file_path: str, storage_directory_path: str, limit: int
):
    """Takes a json with "weather_history_value" as a field in a list of objects
    and gets the data from that url, and saves it as ajson file, only gets the first n results
    Used for testing

    Args:
        json_file_path (str): the json file, containing a list of weather station objects
        who have a field "weather_history_value" which is a url to the data

        storage_directory_path (str): the directory that will store the downloaded jsons

        limit (int): the number of weather histories to get
    """
    # Open the json of all the stations
    with open(json_file_path, encoding="UTF-8") as json_file:
        stations_data = json.load(json_file)

    # Get list of all history files
    # Delete them all, we want fresh data
    for file_name in os.listdir(storage_directory_path):
        os.unlink(storage_directory_path + "/" + file_name)

    i = 0
    for result in stations_data:
        # Get the url for the history data page
        url = result["weather_history_value"]
        # Check we're on the monthly data instead of the almanac data
        if "Monthly" in url:
            i += 1

            # All requests can cause exceptions
            try:
                # Make the request to the webpage with timeout of 10 seconds
                r = requests.get(url, timeout=10)

                print(r.text)
                # Turn request into a json object
                table = r.json()

                print(table)

                # Create object to save data into
                to_save = {}

                # Put request into save object in format
                # that cleaning functions expect
                to_save["weather_history"] = table
                # Prepare to save object
                json_object = json.dumps(to_save, indent=4)

                # Create appropriate file path
                filename = storage_directory_path
                filename += result["item_value"][
                    result["item_value"].rfind("/") :  # noqa: E203
                ]
                filename += "M" + ".json"

                # Save the data
                with open(filename, "w+", encoding="utf-8") as outfile:
                    outfile.write(json_object)

                # Log that we've saved it with a count
                print("saved history data " + str(i) + ": " + filename)

            except requests.exceptions.Timeout:
                print("Request for weather history timed out")
            except requests.exceptions.RequestException as e:
                # catchall for any other exceptions in getting the data
                print("Problem getting weather history..." + str(e))
            except ValueError:
                print("Incorrect JSON syntax for weather history")

        # Stop if we've reached the limit
        if i >= limit:
            return


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("collect_history_data: requires 3 position alrguments")
    # collect_history_data_with_limit(sys.argv[1], sys.argv[2], 10)
    collect_history_data(sys.argv[1], sys.argv[2], sys.argv[3])
