"""Tests for clean_all_histories.py"""

import pathlib
import os
import shutil
import json
from pytest import raises
from group52.data_sanitisation.lib.clean_all_histories import clean_all_histories

# pylint: disable=consider-using-with, line-too-long, duplicate-code

# Method for getting file path found here:
# https://stackoverflow.com/a/3430395 [last accessed: 2024-03-08]
MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

INITIAL_DATA_DIRECTORY = MAIN_PATH + "/origin_data"
INITIAL_DATA_PATH_1 = INITIAL_DATA_DIRECTORY + "/temp_initial1.json"
INITIAL_DATA_PATH_2 = INITIAL_DATA_DIRECTORY + "/temp_initial2.json"
CHANGED_DATA_DIRECTORY = MAIN_PATH + "/changed_data"
REORDER_PATH = MAIN_PATH + "/temp_reorder.json"


def create_files():
    """
    Creates the temp files to store the data
    Run before each test
    """
    if os.path.exists(INITIAL_DATA_DIRECTORY):
        shutil.rmtree(INITIAL_DATA_DIRECTORY)
    if os.path.exists(CHANGED_DATA_DIRECTORY):
        shutil.rmtree(CHANGED_DATA_DIRECTORY)

    os.makedirs(INITIAL_DATA_DIRECTORY)

    open(REORDER_PATH, "w", encoding="UTF-8").close()


def delete_files():
    """
    Deletes the temp files
    Run after each test
    """
    if os.path.exists(INITIAL_DATA_DIRECTORY):
        shutil.rmtree(INITIAL_DATA_DIRECTORY)
    if os.path.exists(CHANGED_DATA_DIRECTORY):
        shutil.rmtree(CHANGED_DATA_DIRECTORY)
    if os.path.exists(REORDER_PATH):
        os.remove(REORDER_PATH)


def test_non_existant_origin_directory_crashes():
    """
    Check program crashes if there is no specified directory
    """
    delete_files()

    with raises(Exception):
        clean_all_histories(
            REORDER_PATH, INITIAL_DATA_DIRECTORY, CHANGED_DATA_DIRECTORY
        )


def test_empty_everything_is_fine():
    """
    Check program doesnt crash when all files and directories exist but all are empty
    """
    create_files()

    clean_all_histories(REORDER_PATH, INITIAL_DATA_DIRECTORY, CHANGED_DATA_DIRECTORY)

    delete_files()


def test_empty_reording_crashes_when_jsons_exit():
    """
    Check program crashes with an empty reording and json files to reorder
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["1"], ["3"], ["4"], ["6"], ["1"], ["2"]],
    }

    with open(
        INITIAL_DATA_DIRECTORY + "/Q1M.json", "w", encoding="UTF-8"
    ) as origin_file:
        json.dump(data_dict, origin_file)

    with raises(Exception):
        clean_all_histories(
            REORDER_PATH, INITIAL_DATA_DIRECTORY, CHANGED_DATA_DIRECTORY
        )

    delete_files()


def test_one_json_is_cleaned_and_stored_correctly():
    """
    Check a directory with one json file in it is cleaned and stored correctly
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["1"], ["3"], ["4"], ["6"], ["2"]],
    }

    with open(
        INITIAL_DATA_DIRECTORY + "/Q1M.json", "w", encoding="UTF-8"
    ) as origin_file:
        json.dump(data_dict, origin_file)

    with open(REORDER_PATH, "w", encoding="UTF-8") as reorder_file:
        reorder_file.write("Station,A")

    clean_all_histories(REORDER_PATH, INITIAL_DATA_DIRECTORY, CHANGED_DATA_DIRECTORY)

    with open(
        CHANGED_DATA_DIRECTORY + "/Q1M.csv", "r", encoding="UTF-8"
    ) as change_file:
        assert change_file.read() == "Q1;1\nQ1;3\nQ1;4\nQ1;6\nQ1;2\n"

    delete_files()


def test_multiple_jsons_cleaned_and_stored_correctly():
    """
    Check a directory with multiple json file in it is cleaned and stored correctly
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["1"], ["3"], ["4"], ["6"], ["2"]],
    }
    with open(
        INITIAL_DATA_DIRECTORY + "/Q1M.json", "w", encoding="UTF-8"
    ) as origin_file:
        json.dump(data_dict, origin_file)

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["11"], ["31"], ["41"], ["61"], ["21"]],
    }
    with open(
        INITIAL_DATA_DIRECTORY + "/Q2M.json", "w", encoding="UTF-8"
    ) as origin_file:
        json.dump(data_dict, origin_file)

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["12"], ["32"], ["42"], ["62"], ["22"]],
    }
    with open(
        INITIAL_DATA_DIRECTORY + "/Q3M.json", "w", encoding="UTF-8"
    ) as origin_file:
        json.dump(data_dict, origin_file)

    with open(REORDER_PATH, "w", encoding="UTF-8") as reorder_file:
        reorder_file.write("Station,A")

    clean_all_histories(REORDER_PATH, INITIAL_DATA_DIRECTORY, CHANGED_DATA_DIRECTORY)

    with open(
        CHANGED_DATA_DIRECTORY + "/Q1M.csv", "r", encoding="UTF-8"
    ) as change_file:
        assert change_file.read() == "Q1;1\nQ1;3\nQ1;4\nQ1;6\nQ1;2\n"
    with open(
        CHANGED_DATA_DIRECTORY + "/Q2M.csv", "r", encoding="UTF-8"
    ) as change_file:
        assert change_file.read() == "Q2;11\nQ2;31\nQ2;41\nQ2;61\nQ2;21\n"
    with open(
        CHANGED_DATA_DIRECTORY + "/Q3M.csv", "r", encoding="UTF-8"
    ) as change_file:
        assert change_file.read() == "Q3;12\nQ3;32\nQ3;42\nQ3;62\nQ3;22\n"

    delete_files()
