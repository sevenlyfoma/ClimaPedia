"""Tests for cleaning functions of cleaning_functionas.py"""

# pylint: disable=line-too-long

import pandas as pd
from group52.data_sanitisation.lib import cleaning_functions


# Tests for functions ued by apply_string_mapaping


# Tests for convert_to_float
def test_convert_to_float_normal_data():
    """Test convert_to_float with normal data"""
    assert cleaning_functions.convert_to_float("10") == 10.0
    assert cleaning_functions.convert_to_float("1") == 1.0
    assert cleaning_functions.convert_to_float("35") == 35.0
    assert cleaning_functions.convert_to_float("900") == 900.0


def test_convert_to_float_boundary_data():
    """Test convert_to_float with boundary data"""
    assert cleaning_functions.convert_to_float("0") == 0.0
    assert cleaning_functions.convert_to_float("1.0") == 1.0
    assert cleaning_functions.convert_to_float("-10") == -10.0
    assert (
        cleaning_functions.convert_to_float("92222222222222222222")
        == 92222222222222222222.0
    )


def test_convert_to_float_error_data():
    """Test convert_to_float with error data"""
    assert cleaning_functions.convert_to_float("") == 0.0
    assert cleaning_functions.convert_to_float("hello") == 0.0


# Tests for extract_q_code
def test_extract_q_code_normal_data():
    """Test extract_q_code with normal data"""
    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q61021340")
        == "Q61021340"
    )

    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q61207992")
        == "Q61207992"
    )

    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q61308944")
        == "Q61308944"
    )

    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q61282136")
        == "Q61282136"
    )


def test_extract_q_code_boundary_data():
    """Test extract_q_code with boundary data"""
    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q1") == "Q1"
    )
    assert (
        cleaning_functions.extract_q_code("http://www.wikidata.org/entity/Q0") == "Q0"
    )
    assert (
        cleaning_functions.extract_q_code(
            "http://www.wikidata.org/entity/Q9000000000000000000000000000"
        )
        == "Q9000000000000000000000000000"
    )
    assert (
        cleaning_functions.extract_q_code("http://www.wikidaQ61021340") == "Q61021340"
    )
    assert cleaning_functions.extract_q_code("xQ61021340") == "Q61021340"
    assert cleaning_functions.extract_q_code("Q61021340") == "Q61021340"
    assert cleaning_functions.extract_q_code("Q61021340XS") == "Q61021340"
    assert cleaning_functions.extract_q_code("Q61021340Q1") == "Q61021340"


def test_extract_q_code_error_data():
    """Test extract_q_code with error data"""
    assert cleaning_functions.extract_q_code("1") is None
    assert cleaning_functions.extract_q_code("Q") is None
    assert cleaning_functions.extract_q_code("") is None
    assert cleaning_functions.extract_q_code("hello world") is None


# Tests for reformat_lat_and_long
def test_reformat_lat_and_long_normal_data():
    """Test reformat_lat_and_long with normal data"""
    assert cleaning_functions.reformat_lat_and_long("Point(1 1)") == "1 1"
    assert cleaning_functions.reformat_lat_and_long("Point(1 -1)") == "1 -1"
    assert cleaning_functions.reformat_lat_and_long("Point(-1 1)") == "-1 1"
    assert cleaning_functions.reformat_lat_and_long("Point(-1 -1)") == "-1 -1"

    assert cleaning_functions.reformat_lat_and_long("Point(70 30)") == "70 30"
    assert cleaning_functions.reformat_lat_and_long("Point(40 -56)") == "40 -56"
    assert cleaning_functions.reformat_lat_and_long("Point(-65 12)") == "-65 12"
    assert cleaning_functions.reformat_lat_and_long("Point(-14 -17)") == "-14 -17"


def test_reformat_lat_and_long_boundary_data():
    """Test reformat_lat_and_long with boundary data"""
    assert cleaning_functions.reformat_lat_and_long("Point(0 0)") == "0 0"
    assert cleaning_functions.reformat_lat_and_long("Point(1110 11210)") == "1110 11210"
    # assert cleaning_functions.reformat_lat_and_long("P(1 1)") == "1 1"
    # assert cleaning_functions.reformat_lat_and_long("(1 1)") == "1 1"
    assert cleaning_functions.reformat_lat_and_long("Point(1 1)xxxx") == "1 1"


def test_reformat_lat_and_long_error_data():
    """Test reformat_lat_and_long with error data"""
    assert cleaning_functions.reformat_lat_and_long("") == "0 0"
    assert cleaning_functions.reformat_lat_and_long("Point()") == "0 0"
    assert cleaning_functions.reformat_lat_and_long("Point(x y)") == "0 0"


# Tests for cleaning functions that operate on data frames


# Tests for drop_column
def test_drop_column_normal():
    """Test drop_column drops a single column specified and no more"""
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)

    df = cleaning_functions.drop_column(df, "col1", [])

    assert "col1" not in list(df.columns)
    assert "col2" in list(df.columns)

    df = cleaning_functions.drop_column(df, "col2", [])

    assert "col1" not in list(df.columns)
    assert "col2" not in list(df.columns)


def test_drop_column_column_not_in_dataframe():
    """Test drop_column doesnt drop anything if the column isnt in the dataframe"""
    d = {"col1": [1, 2], "col2": [3, 4]}
    df = pd.DataFrame(data=d)

    df = cleaning_functions.drop_column(df, "col3", [])

    assert "col1" in list(df.columns)
    assert "col2" in list(df.columns)


# Tests for extract_json_fields
def test_extract_json_fields_extract_from_one_field_object():
    """test extract_json_fields when extracting
    a single field from an object with a single field"""
    d = [{"col1": {"x": 4}, "col2": {"x": 3}}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.extract_json_fields(df, "col1", ["x"])
    assert "col1" in list(df.columns)
    assert "col1_x" in list(df.columns)


def test_extract_json_fields_extract_one_from_two_field_object():
    """test extract_json_fields when extracting
    a single field from an object with a two fields"""
    d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.extract_json_fields(df, "col1", ["y"])
    assert "col1" in list(df.columns)
    assert "col1_y" in list(df.columns)


def test_extract_json_fields_extract_mutliple_fields():
    """test extract_json_fields when extracting
    multiple fields from an object with multiple fields"""
    d = [{"col1": {"x": 4, "y": 6, "z": 8, "w": 2}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.extract_json_fields(df, "col1", ["y", "z", "x"])
    assert "col1" in list(df.columns)
    assert "col1_x" in list(df.columns)
    assert "col1_y" in list(df.columns)
    assert "col1_z" in list(df.columns)
    assert "col1_w" not in list(df.columns)


def test_extract_json_fields_extract_invalid_field():
    """test extract_json_fields when extracting
    an invalid field that nothing is extracted"""
    d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.extract_json_fields(df, "col1", ["z"])
    assert "col1" in list(df.columns)
    assert "col1_z" not in list(df.columns)
    assert "col1_x" not in list(df.columns)
    assert "col1_y" not in list(df.columns)


def test_extract_json_fields_extrac_no_field():
    """test extract_json_fields when extracting
    a blank field that nothing is extracted"""
    d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.extract_json_fields(df, "col1", [""])
    assert "col1" in list(df.columns)
    assert "col1_" not in list(df.columns)
    assert "col1_x" not in list(df.columns)
    assert "col1_y" not in list(df.columns)


# Tests for rename_column
def test_rename_column_normal():
    """test that rename_column works under normal circumstances,
    old column gone, new column present"""
    d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.rename_column(df, "col1", ["newcol"])

    assert "newcol" in list(df.columns)
    assert "col1" not in list(df.columns)


def test_rename_column_too_many_args():
    """test extract_json_fields works when too many arguments are provided,
    ignoring the extra arguments"""
    d = [{"col1": {"x": 4, "y": 6}, "col2": "3"}]
    df = pd.DataFrame(data=d)

    df = cleaning_functions.rename_column(df, "col1", ["newcol", "newcol2"])

    assert "newcol" in list(df.columns)
    assert "col1" not in list(df.columns)
    assert "newcol2" not in list(df.columns)


# TEsts for split_into_columns
def test_split_into_columns_two_values_space():
    """test that split_into_columns works in the normal scenario
    of 2 values delimited by a space"""
    d = [{"col1": "6 5", "col2": "3"}, {"col1": "2 2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.split_into_columns(df, "col1", [" ", "x", "y"])

    assert "col1" in list(df.columns)
    assert "x" in list(df.columns)
    assert "y" in list(df.columns)

    assert df["x"].iloc[0] == "6"
    assert df["y"].iloc[0] == "5"

    assert df["x"].iloc[1] == "2"
    assert df["y"].iloc[1] == "2"


def test_split_into_columns_two_values_comma():
    """test that split_into_columns works
    in the irregular scenario of 2 values delimited by a comma"""
    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y"])

    assert "col1" in list(df.columns)
    assert "x" in list(df.columns)
    assert "y" in list(df.columns)

    assert df["x"].iloc[0] == "6"
    assert df["y"].iloc[0] == "5"

    assert df["x"].iloc[1] == "2"
    assert df["y"].iloc[1] == "2"


def test_split_into_columns_three_values():
    """test that split_into_columns works in the irregular scenario of 3 values"""
    d = [{"col1": "6,5,5", "col2": "3"}, {"col1": "2,2,6", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y", "z"])

    assert "col1" in list(df.columns)
    assert "x" in list(df.columns)
    assert "y" in list(df.columns)
    assert "z" in list(df.columns)

    assert df["x"].iloc[0] == "6"
    assert df["y"].iloc[0] == "5"
    assert df["z"].iloc[0] == "5"

    assert df["x"].iloc[1] == "2"
    assert df["y"].iloc[1] == "2"
    assert df["z"].iloc[1] == "6"


def test_split_into_columns_too_many_columns():
    """test that split_into_columns doesnt change the dataframe
    if too many columns are provided"""
    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.split_into_columns(df, "col1", [",", "x", "y", "z"])

    assert "col1" in list(df.columns)
    assert "x" not in list(df.columns)
    assert "y" not in list(df.columns)
    assert "z" not in list(df.columns)


def test_split_into_columns_too_few_columns():
    """test that split_into_columns doesnt change the dataframe
    if too few columns are provided"""
    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.split_into_columns(df, "col1", [",", "x"])

    assert "col1" in list(df.columns)
    assert "x" not in list(df.columns)


# Tests for apply string mappings
def test_apply_string_mappings_normal():
    """test that apply_string mappings works in the normal case"""
    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.apply_string_mapping(df, "col2", ["convert_to_float"])

    assert df["col2"].iloc[0] == 3.0
    assert df["col2"].iloc[1] == 4.0


def test_apply_string_mappings_invalid_function():
    """test that apply_string mappings doesnt throw an error
    with a non existant function"""

    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.apply_string_mapping(df, "col2", ["hello"])


def test_apply_string_mappings_valid_unworking_function():
    """test that apply_string mappings doesnt throw an error
    with a real but non functional function"""
    d = [{"col1": "6,5", "col2": "3"}, {"col1": "2,2", "col2": "4"}]
    df = pd.DataFrame(data=d)
    df = cleaning_functions.apply_string_mapping(df, "col2", ["apply_string_mapping"])
