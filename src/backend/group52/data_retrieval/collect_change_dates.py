"""Code to get weather history data modified times from WikiData"""

import sys
import json
import re
from datetime import datetime
import requests

# pylint: disable=duplicate-code, consider-using-with, too-many-locals

ENDPOINT_URL = "https://query.wikidata.org/sparql"


def get_change_times_dict(storage_file_path: str):
    """
    Helper function to read in change time file and store them in a dictionary
    Args:
        storage_file_path (str): the file storing the change times
    """
    save_file = open(storage_file_path, encoding="UTF-8")
    lines = save_file.read().splitlines()
    value_dict = {}
    for line in lines:
        splitted = line.split(";")
        value_dict[splitted[0]] = splitted[1]

    return value_dict


def write_dict(storage_file_path: str, value_dict: dict):
    """
    Helper function to write to change time file with contents of dictionary
    Args:
        storage_file_path (str): the file storing the change times
    """
    save_file = open(storage_file_path, "w", encoding="UTF-8")
    for i in value_dict.keys():
        save_file.write(str(i) + ";" + str(value_dict.get(i)) + "\n")


def collect_change_dates(
    json_file_path: str, storage_file_path: str, stale_data_path: str
):
    """Takes a json with "weather_history_value" as a field in a list of objects
    and gets the data modified time from a changed version of that url
    Gets the time each was modified last and compares it to the new value
    If there has been a change, that entry is stored in the stale data file

    Args:
        json_file_path (str): the json file, containing a list of weather station objects
        who have a field "weather_history_value" which is a url to the data

        storage_file_path (str): the file that stores the modified time of each file

        stale_data_path (str): the file that stores the name of all the stale stations
    """
    # Open the json of all the stations
    with open(json_file_path, encoding="UTF-8") as json_file:
        stations_data = json.load(json_file)

    # Open the file to store the names of stale entries
    stale_data_file = open(stale_data_path, "w", encoding="UTF-8")

    # Dictionary to store the new change times
    change_times_dict = get_change_times_dict(storage_file_path)
    up_to_date_dict = {}

    # Timing how long the process takes
    before = datetime.now()

    i = 0
    for result in stations_data:
        # Get the url for the history data page
        url = result["weather_history"]["value"]
        # Check we're on the monthly data instead of the almanac data
        if "Monthly" in url:
            i += 1

            # All requests can cause exceptions
            try:

                # Change the url to get the html version
                newurl = url[:29] + "wiki" + url[38:]
                # Make the request to the webpage with timeout of 10 seconds
                r = requests.get(newurl, timeout=10)

                # Turn request into a str
                html_text = r.text

                # Find the time last edited in the html
                # This really seems to be the only way to do this to me
                filename = result["item"]["value"][
                    result["item"]["value"].rfind("/") :  # noqa: E203
                ]
                m = re.search(r"This page was last edited on (.*?)\.", html_text)

                # If the section is found
                if m:
                    # Get it
                    section = m.group()

                    # Get the previous modify time
                    old_date = change_times_dict.get(filename)
                    # Add new modify time to
                    up_to_date_dict[filename] = section

                    # Check if they are different
                    # and add them to stale list if needed
                    if old_date != section:
                        stale_data_file.write(filename + "\n")

                    # Print for logging
                    print(str(i) + ". " + filename + " " + section)

            except requests.exceptions.Timeout:
                print("Request for weather history timed out")
            except requests.exceptions.RequestException as e:
                # catchall for any other exceptions in getting the data
                print("Problem getting weather history..." + str(e))
            except ValueError:
                print("Incorrect JSON syntax for weather history")

    later = datetime.now()
    print(later - before)
    write_dict(storage_file_path, up_to_date_dict)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("collect_history_data: requires 3 position alrguments")
    collect_change_dates(sys.argv[1], sys.argv[2], sys.argv[3])
