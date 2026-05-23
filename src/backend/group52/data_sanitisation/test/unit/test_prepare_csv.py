"""Tests for prepare_csv.py"""

import pathlib
import os
import pandas as pd
from pytest import raises
from group52.data_sanitisation.lib.prepare_csv import prepare_csv

# pylint: disable=consider-using-with

# Method for getting file path found here:
# https://stackoverflow.com/a/3430395 [last accessed: 2024-03-08]
MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

INITIAL_DATA_PATH = MAIN_PATH + "/temp_initial.json"
CHANGED_DATA_PATH = MAIN_PATH + "/temp_changed.json"


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


def test_empty_files_crash():
    """
    Test to check the program throws an error on a completely empty initial data file
    """
    create_files()
    with raises(Exception):
        prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)
    delete_files()


def test_empty_json_written_correctly():
    """
    Test that an empty json gets written as an empty txt
    """

    create_files()
    data = []
    df = pd.DataFrame(data, columns=[])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    with open(CHANGED_DATA_PATH, "r", encoding="UTF-8") as change_file:
        assert change_file.read() == ""

    delete_files()


def test_1_col_1_row_written_correctly():
    """
    Test that a json with 1 column and 1 value is written correctly
    """

    create_files()
    data = [1]
    df = pd.DataFrame(data, columns=["A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    with open(CHANGED_DATA_PATH, "r", encoding="UTF-8") as change_file:
        assert change_file.read() == "1\n"

    delete_files()


def test_multiple_cols_1_row_written_correctly():
    """
    Test that a json with multiple columns and 1 row is written correctly
    """

    create_files()
    data = [[1, 1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    with open(CHANGED_DATA_PATH, "r", encoding="UTF-8") as change_file:
        assert change_file.read() == "1;1;2;3;4\n"

    delete_files()


def test_multiple_cols_multiple_rows_written_correctly():
    """
    Test that a json with multiple columns and multiple rows is written correctly
    """
    create_files()
    data = [
        [1, 2, 3, 4, 5],
        [2, 3, 4, 5, 6],
        [3, 4, 5, 6, 7],
        [4, 5, 6, 7, 8],
        [5, 6, 7, 8, 9],
    ]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    with open(CHANGED_DATA_PATH, "r", encoding="UTF-8") as change_file:
        assert (
            change_file.read()
            == "1;2;3;4;5\n2;3;4;5;6\n3;4;5;6;7\n4;5;6;7;8\n5;6;7;8;9\n"
        )

    delete_files()


def test_null_values_saved_correctly():
    """
    Test that null values are correctly saved as \\N
    """
    create_files()
    data = [[1, 1, None, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    prepare_csv(INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    with open(CHANGED_DATA_PATH, "r", encoding="UTF-8") as change_file:
        assert change_file.read() == "1;1;\\N;3;4\n"

    delete_files()
