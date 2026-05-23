"""Tests for clean_data_formatting.py"""

import pathlib
import os
import json
import pandas as pd
from pandas import DataFrame
from pytest import raises
from group52.data_sanitisation.lib.clean_data_formatting import clean_data_formatting
from group52.data_sanitisation.lib.clean_data_formatting import apply_cleaning_function

# pylint: disable=consider-using-with

# Method for getting file path found here:
# https://stackoverflow.com/a/3430395 [last accessed: 2024-03-08]
MAIN_PATH = str(pathlib.Path(__file__).parent.resolve())

INITIAL_DATA_PATH = MAIN_PATH + "/temp_initial.json"
CHANGED_DATA_PATH = MAIN_PATH + "/temp_changed.json"
MAPPINGS_PATH = MAIN_PATH + "/temp_mappings.json"


def create_files():
    """
    Creates the temp files to store the data
    Run before each test
    """
    open(INITIAL_DATA_PATH, "w", encoding="UTF-8").close()
    open(CHANGED_DATA_PATH, "w", encoding="UTF-8").close()
    open(MAPPINGS_PATH, "w", encoding="UTF-8").close()


def delete_files():
    """
    Deletes the temp files
    Run after each test
    """
    os.remove(INITIAL_DATA_PATH)
    os.remove(CHANGED_DATA_PATH)
    os.remove(MAPPINGS_PATH)


# Apply Cleaning Functions Tests


def test_acf_no_functions_is_ok():
    """
    Test to check nothing happens when no cleaning functionsare applied in
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])

    newdf = apply_cleaning_function(df, "A", [], [])

    assert df.equals(newdf)

    delete_files()


def test_acf_fake_function_fails():
    """
    Test to check program crashes when a fake cleaning function is used in
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])

    with raises(Exception):
        apply_cleaning_function(df, "A", ["Fake_function"], [[]])

    delete_files()


def test_acf_real_function_works():
    """
    Test to check program doesnt crash when using a real cleaning function in
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])

    new_df = apply_cleaning_function(df, "A", ["drop_column"], [[]])

    data = [[1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["B", "C", "D", "E"])

    assert df.equals(new_df)

    delete_files()


def test_acf_function_with_no_args_crashes():
    """
    Test to check program crashes when a fake cleaning function is used in
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, 2, 3, 4]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])

    with raises(Exception):
        apply_cleaning_function(df, "A", ["drop_column"], [])

    delete_files()


def test_acf_multiple_functions_work():
    """
    Test to check program works fine for applying multiple cleaning functions
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, "1", 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])

    new_df = apply_cleaning_function(
        df,
        "C",
        ["apply_string_mapping", "rename_column"],
        [["convert_to_float"], ["F"]],
    )

    create_files()
    data = [[1, 1, 1.0, 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "F", "D", "E"])

    assert df.equals(new_df)

    delete_files()


def test_acf_multiple_functions_fail_when_second_is_fake():
    """
    Test to check program works crashes when second of two functions is fake
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, "1", 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    with raises(Exception):
        apply_cleaning_function(
            df,
            "C",
            ["apply_string_mapping", "fake function"],
            [["convert_to_float"], [""]],
        )

    delete_files()


def test_acf_multiple_functions_fail_with_missing_args():
    """
    Test to check program works crashes when second of two functions has no args
    apply_cleaning_function
    """
    create_files()
    data = [[1, 1, "1", 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    with raises(Exception):
        apply_cleaning_function(
            df, "C", ["apply_string_mapping", "rename_column"], [["convert_to_float"]]
        )

    delete_files()


def test_cdf_crashes_with_empty_mappings_file():
    """
    Test to check if program crashes when not provided with a mappings file
    in clean data formatting
    """

    create_files()
    data = [[1, 1, "1", 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    with raises(Exception):
        clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_cdf_does_nothing_with_empty_mappings_json():
    """
    Test to check nothing happens to the json if provided with an empty json
    in clean_data_formatting
    """
    create_files()
    data = [[1, 1, "1", 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    mappings_dict = {}

    with open(MAPPINGS_PATH, "w", encoding="UTF-8") as mappings_file:
        json.dump(mappings_dict, mappings_file)

    clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))
    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_cdf_single_mapping_works():
    """
    Test to check a single mapping works
    in clean_data_formatting
    """
    create_files()
    data = [[1, 1, 1, 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    mappings_dict = {}
    mappings_dict["A"] = {"cleaningFuncs": ["drop_column"], "cleaningArgs": [[]]}

    with open(MAPPINGS_PATH, "w", encoding="UTF-8") as mappings_file:
        json.dump(mappings_dict, mappings_file)

    clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [[1, 1, 1, 1]]
    df = pd.DataFrame(data, columns=["B", "C", "D", "E"])

    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_cdf_crashes_with_no_mapping_args():
    """
    Test to check cdf crashes when the mappings file has missing args
    in clean_data_formatting
    """
    create_files()
    data = [[1, 1, 1, 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    mappings_dict = {}
    mappings_dict["A"] = {"cleaningFuncs": ["drop_column"], "cleaningArgs": []}

    with open(MAPPINGS_PATH, "w", encoding="UTF-8") as mappings_file:
        json.dump(mappings_dict, mappings_file)

    with raises(Exception):
        clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    delete_files()


def test_cdf_multiple_mappings_can_be_specified():
    """
    Test to check multiple mappings can be specified for a mappings file
    in clean_data_formatting
    """
    create_files()
    data = [["1", 1, 1, 1, 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    mappings_dict = {}
    mappings_dict["A"] = {
        "cleaningFuncs": ["apply_string_mapping", "rename_column"],
        "cleaningArgs": [["convert_to_float"], ["F"]],
    }

    with open(MAPPINGS_PATH, "w", encoding="UTF-8") as mappings_file:
        json.dump(mappings_dict, mappings_file)

    clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [[1.0, 1, 1, 1, 1]]
    df = pd.DataFrame(data, columns=["F", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))
    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()


def test_cdf_multiple_mappings_can_be_specified_for_multiple_columns():
    """
    Test to check multiple mappings can be specified for a mappings file
    in clean_data_formatting
    """
    create_files()
    data = [["1", 1, 1, "1", 1]]
    df = pd.DataFrame(data, columns=["A", "B", "C", "D", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    mappings_dict = {}
    mappings_dict["A"] = {
        "cleaningFuncs": ["apply_string_mapping", "rename_column"],
        "cleaningArgs": [["convert_to_float"], ["F"]],
    }
    mappings_dict["D"] = {
        "cleaningFuncs": ["apply_string_mapping", "rename_column"],
        "cleaningArgs": [["convert_to_float"], ["J"]],
    }

    with open(MAPPINGS_PATH, "w", encoding="UTF-8") as mappings_file:
        json.dump(mappings_dict, mappings_file)

    clean_data_formatting(MAPPINGS_PATH, INITIAL_DATA_PATH, CHANGED_DATA_PATH)

    data = [[1.0, 1, 1, 1.0, 1]]
    df = pd.DataFrame(data, columns=["F", "B", "C", "J", "E"])
    df.to_json(INITIAL_DATA_PATH, orient="records", indent=1, date_format="iso")

    df = DataFrame(pd.read_json(INITIAL_DATA_PATH))
    changed_df = pd.read_json(CHANGED_DATA_PATH)

    assert df.equals(changed_df)

    delete_files()
