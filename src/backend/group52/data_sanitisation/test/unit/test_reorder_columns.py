"""Tests for reorder_columns.py"""

import pathlib
import os
import pandas as pd
from pytest import raises
from group52.data_sanitisation.lib.reorder_columns import reorder_columns

# pylint: disable=consider-using-with

# Method for getting file path found here:
# https://stackoverflow.com/a/3430395 [last accessed: 2024-03-08]
MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

REORDERING_PATH = MAIN_PATH + "/temp_reordering.txt"
INITIAL_DATA_PATH = MAIN_PATH + "/temp_initial.json"
CHANGED_DATA_PATH = MAIN_PATH + "/temp_changed.json"


def create_files():
    """
    Creates the temp files to store the data
    Run before each test
    """
    open(REORDERING_PATH, "w", encoding="UTF-8").close()
    open(INITIAL_DATA_PATH, "w", encoding="UTF-8").close()
    open(CHANGED_DATA_PATH, "w", encoding="UTF-8").close()


def delete_files():
    """
    Deletes the temp files
    Run after each test
    """
    os.remove(REORDERING_PATH)
    os.remove(INITIAL_DATA_PATH)
    os.remove(CHANGED_DATA_PATH)


def test_empty_files_crash():
    """
    Test to check the program throws an error on a completely empty initial data file
    """
    create_files()
    with raises(Exception):
        reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)
    delete_files()


def test_empty_json_object_doesnt_crash():
    """
    Test to check if an initial data file of {} is given then it will be saved correctly
    """
    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("")

    data = []
    df = pd.DataFrame(data, columns=[])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_one_column_no_ordering_crashes():
    """
    Test to check if a dict with one column and empty ordering crashes
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("")

    data = [[1]]
    df = pd.DataFrame(data, columns=["A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    with raises(Exception):
        reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_one_column_with_ordering_works():
    """
    Test to check if a dict with one column and a corresponding ordering
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("A")

    data = [[1]]
    df = pd.DataFrame(data, columns=["A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_one_column_too_big_ordering_crashes():
    """
    Test to check if a dict with one column and an ordering that is too long crashes
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("A,B")

    data = [[1]]
    df = pd.DataFrame(data, columns=["A"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    with raises(Exception):
        reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_two_columns_with_identical_order_works():
    """
    Test to check if a dict with two columns and an identical ordering results in no change
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("A,B")

    data = [[1, 2]]
    df = pd.DataFrame(data, columns=["A", "B"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_two_columns_with_new_order_works():
    """
    Test to check if a dict with two columns and a new ordering results in correct change
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("B,A")

    data = [[1, 2]]
    df = pd.DataFrame(data, columns=["A", "B"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    data = [[2, 1]]
    df = pd.DataFrame(data, columns=["B", "A"])

    assert df.equals(changed_df)

    delete_files()


def test_ordering_with_typo_key_causes_crash():
    """
    Test to check if an ordering with a typo causes a crash
    """

    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("A,b")

    data = [[1, 2]]
    df = pd.DataFrame(data, columns=["A", "B"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    with raises(Exception):
        reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_reordering_works_with_multiple_rows():
    """
    Test to check if a dict with multi rows of data is reordered properly
    """
    create_files()

    with open(REORDERING_PATH, "w", encoding="UTF-8") as reorderings:
        reorderings.write("B,A,D,C")

    data = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    reorder_columns(REORDERING_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    data = [[2, 1, 4, 3], [6, 5, 8, 7], [10, 9, 12, 11], [14, 13, 16, 15]]
    df = pd.DataFrame(data, columns=["B", "A", "D", "C"])

    assert df.equals(changed_df)

    delete_files()
