"""Tests for clean_and_save_extreme_weather.py"""

# pylint: disable=line-too-long

import decimal
import pandas as pd

from group52.data_sanitisation.lib.clean_and_save_extreme_weather import (
    convert_to_sql_date,
    safe_convert_to_decimal,
    convert_json_to_csvs,
)


def test_convert_to_sql_date_normal():
    """Test convert_to_sql_date with normal input"""
    assert convert_to_sql_date("2023-04-01T12:00:00Z") == "2023-04-01T12:00:00"
    assert convert_to_sql_date("2022-12-31T23:59:59Z") == "2022-12-31T23:59:59"


def test_convert_to_sql_date_invalid():
    """Test convert_to_sql_date with invalid input"""
    assert convert_to_sql_date("invalid_date") is None


# Tests for safe_convert_to_decimal
def test_safe_convert_to_decimal_normal():
    """Test safe_convert_to_decimal with normal input"""
    assert safe_convert_to_decimal("10.0") == decimal.Decimal("10.0000000000")
    assert safe_convert_to_decimal("3.14159") == decimal.Decimal("3.1415900000")


def test_safe_convert_to_decimal_large_number():
    """Test safe_convert_to_decimal with a large number"""
    large_number = "12345678901.2345678901"
    expected_result = decimal.Decimal("12345678901.2345678901")
    assert safe_convert_to_decimal(large_number) == expected_result


def test_safe_convert_to_decimal_invalid():
    """Test safe_convert_to_decimal with invalid input"""
    assert safe_convert_to_decimal("invalid") is None


def test_convert_json_to_csvs(tmp_path):
    """Test convert_json_to_csvs with a sample JSON file (tests convert_df_to_csv as well)"""
    # Create a sample JSON file
    sample_json = """
    [
        {
            "item": {"value": "http://www.wikidata.org/entity/Q61021340"},
            "geo": {"value": "Point(1.2345 6.7890)"},
            "startTime": {"value": "2022-01-01T00:00:00Z"},
            "endTime": {"value": "2022-01-02T12:34:56Z"},
            "country": {"value": "http://www.wikidata.org/entity/Q16"},
            "type": {"value": "http://www.wikidata.org/entity/Q8072"},
            "itemLabel": {"value": "Sample Event"}
        }
    ]
    """
    sample_file = tmp_path / "sample.json"
    sample_file.write_text(sample_json)

    # Call the function
    convert_json_to_csvs(str(sample_file), str(tmp_path))

    # Check if the CSV files were created
    assert (tmp_path / "Countries.csv").exists()
    assert (tmp_path / "Types.csv").exists()
    assert (tmp_path / "Events.csv").exists()
    assert (tmp_path / "EventTypes.csv").exists()
    assert (tmp_path / "EventCountries.csv").exists()

    # Check the contents of the Events.csv file
    events_df = pd.read_csv(
        tmp_path / "Events.csv",
        sep=";",
        header=None,
        names=[
            "EVENT_ID",
            "LATITUDE",
            "LONGITUDE",
            "START_TIME",
            "END_TIME",
            "ITEM_LABEL",
        ],
    )
    assert len(events_df) == 1
    assert events_df["EVENT_ID"].iloc[0] == "Q61021340"
    assert events_df["START_TIME"].iloc[0] == "2022-01-01T00:00:00"
    assert events_df["END_TIME"].iloc[0] == "2022-01-02T12:34:56"
    assert str(events_df["LATITUDE"].iloc[0]) == "1.2345"
    assert str(events_df["LONGITUDE"].iloc[0]) == "6.789"
    assert events_df["ITEM_LABEL"].iloc[0] == "Sample Event"
