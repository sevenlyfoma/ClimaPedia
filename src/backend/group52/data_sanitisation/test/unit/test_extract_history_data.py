"""Tests for extract_history_data.py"""

import pathlib
import os
import json
import pandas as pd
from pandas import DataFrame
from pytest import raises
from group52.data_sanitisation.lib.extract_history_data import extract_history_data

# pylint: disable=consider-using-with, line-too-long, duplicate-code

# Method for getting file path found here:
# https://stackoverflow.com/a/3430395 [last accessed: 2024-03-08]
MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

INITIAL_DATA_PATH = MAIN_PATH + "/temp_initialM.json"
CHANGED_DATA_PATH = MAIN_PATH + "/temp_changedM.json"


def create_files():
    """
    Creates the temp files to store the data
    Run before each test
    """
    open(INITIAL_DATA_PATH, "w", encoding="UTF-8").close()
    open(CHANGED_DATA_PATH, "w", encoding="UTF-8").close()


def delete_files():
    """
    Deletes the temp files
    Run after each test
    """
    os.remove(INITIAL_DATA_PATH)
    os.remove(CHANGED_DATA_PATH)


def test_crashes_on_empty_file():
    """
    Tess extraction crashes on an empty file
    """
    create_files()

    with raises(Exception):
        extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_crashes_on_json_with_wrong_attributes():
    """
    Test extraction fails when the source file doesnt have the right attributes
    """
    create_files()

    data_dict = {}
    data_dict["weather_histor"] = {"schema": {"fields": [{"name": "A"}]}, "data": []}

    with raises(Exception):
        extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_correctly_formats_one_column_one_row():
    """
    Test extraction succeeds when one column and 1 row specified
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["1"]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [["temp_initial", "1"]]
    df = pd.DataFrame(data, columns=["Station", "A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_correctly_formats_one_column_multiple_rows():
    """
    Test extraction succeeds when one column and multiple rows specified
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}]},
        "data": [["1"], ["3"], ["4"], ["6"], ["1"], ["2"]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [
        ["temp_initial", "1"],
        ["temp_initial", "3"],
        ["temp_initial", "4"],
        ["temp_initial", "6"],
        ["temp_initial", "1"],
        ["temp_initial", "2"],
    ]
    df = pd.DataFrame(data, columns=["Station", "A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_correctly_formats_multiple_columns_one_row():
    """
    Test extraction succeeds when multiple columns and one row specified
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}, {"name": "B"}, {"name": "D"}]},
        "data": [["1", "4", "44"]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [["temp_initial", "1", "4", "44"]]
    df = pd.DataFrame(data, columns=["Station", "A", "B", "D"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_correctly_formats_multiple_columns_multiple_rows():
    """
    Test extraction succeeds when multiple columns and multiple rows specified
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}, {"name": "B"}, {"name": "D"}]},
        "data": [["1", "4", "44"], ["1", "22", "4"], ["11", "64", "44"]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [
        ["temp_initial", "1", "4", "44"],
        ["temp_initial", "1", "22", "4"],
        ["temp_initial", "11", "64", "44"],
    ]
    df = pd.DataFrame(data, columns=["Station", "A", "B", "D"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_nulls_are_preserved():
    """
    Test extraction keeps null values correctly
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}, {"name": "B"}, {"name": "D"}]},
        "data": [["1", "4", None], ["1", "22", None], ["11", None, "44"]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [
        ["temp_initial", "1", "4", None],
        ["temp_initial", "1", "22", None],
        ["temp_initial", "11", None, "44"],
    ]
    df = pd.DataFrame(data, columns=["Station", "A", "B", "D"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_missing_data_is_replaced_with_null():
    """
    Test if there is missing data it is replaced by None
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}, {"name": "B"}, {"name": "D"}]},
        "data": [["11", None, "4"], ["11", None]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [["temp_initial", "11", None, "4"], ["temp_initial", "11", None, None]]
    df = pd.DataFrame(data, columns=["Station", "A", "B", "D"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")
    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_different_column_and_value_numbers_causes_crash():
    """
    Test if there is a crash if there is an unequal number of fields and data columns
    """
    create_files()

    data_dict = {}
    data_dict["weather_history"] = {
        "schema": {"fields": [{"name": "A"}, {"name": "B"}, {"name": "D"}]},
        "data": [["11", None], ["11", None]],
    }

    with open(INITIAL_DATA_PATH, "w", encoding="UTF-8") as origin_file:
        json.dump(data_dict, origin_file)

    with raises(Exception):
        extract_history_data(INITIAL_DATA_PATH, CHANGED_DATA_PATH)
    delete_files()
