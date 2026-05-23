"""Convert extreme weather JSON data to CSVs"""

import sys
from datetime import datetime
import decimal
import pandas as pd


def convert_to_sql_date(date_str):
    """Convert date string to SQL date format

    Args:
        date_str (str): date string

    Returns:
        str: date string in the format "YYYY-MM-DDTHH:MM:SS"
    """
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt.isoformat()
    except ValueError:
        return None


def convert_df_to_csv(df, filename, dest_path):
    """Convert dataframe to csv

    Args:
        df (pandas.DataFrame): dataframe to be converted
        filename (str): name of the file to be saved
    """
    df.to_csv(
        dest_path + "/" + filename, index=False, na_rep="\\N", header=False, sep=";"
    )


def safe_convert_to_decimal(value_str):
    """Convert string to decimal

    Args:
        value_str (str): string to be converted

    Returns:
        decimal: the converted value
    """
    try:
        value = decimal.Decimal(value_str)
        # Ensuring the value fits within DECIMAL(30,10) constraints
        return value.quantize(
            decimal.Decimal("0.0000000000"), rounding=decimal.ROUND_HALF_UP
        )
    except decimal.InvalidOperation:
        return None


def convert_json_to_csvs(source_file, dest_path):
    """Convert JSON data to CSVs

    Args:
        source_file (str): the file to be converted
    """

    df = pd.read_json(source_file)

    # Extract unique countries and types (Q codes only)
    unique_countries = (
        df["country"]
        .apply(lambda x: x["value"].split("/")[-1] if isinstance(x, dict) else x)
        .dropna()
        .unique()
    )
    unique_types = (
        df["type"]
        .apply(lambda x: x["value"].split("/")[-1] if isinstance(x, dict) else x)
        .dropna()
        .unique()
    )

    all_events = df.apply(  # pylint: disable=E1101
        lambda row: (
            row["item"]["value"].split("/")[-1],
            (
                safe_convert_to_decimal(
                    row["geo"]["value"]
                    .replace("Point(", "")
                    .replace(")", "")
                    .split(" ")[0]
                )
                if "geo" in row
                else None
            ),
            (
                safe_convert_to_decimal(
                    row["geo"]["value"]
                    .replace("Point(", "")
                    .replace(")", "")
                    .split(" ")[1]
                )
                if "geo" in row
                else None
            ),
            (
                convert_to_sql_date(row["startTime"]["value"])
                if "startTime" in row
                and isinstance(row["startTime"], dict)
                and "value" in row["startTime"]
                else None
            ),
            (
                convert_to_sql_date(row["endTime"]["value"])
                if "endTime" in row
                and isinstance(row["endTime"], dict)
                and "value" in row["endTime"]
                else None
            ),
            (
                row["country"]["value"].split("/")[-1]
                if "country" in row
                and isinstance(row["country"], dict)
                and "value" in row["country"]
                else None
            ),
            (
                row["type"]["value"].split("/")[-1]
                if "type" in row
                and isinstance(row["type"], dict)
                and "value" in row["type"]
                else None
            ),
            row["itemLabel"]["value"],
        ),
        axis=1,
    ).tolist()

    # Generate CSVs for sql insert
    events_df = pd.DataFrame(
        all_events,
        columns=[
            "EVENT_ID",
            "START_TIME",
            "END_TIME",
            "LATITUDE",
            "LONGITUDE",
            "COUNTRY_ID",
            "TYPE_ID",
            "ITEM_LABEL",
        ],
    )
    event_types_df = events_df[["EVENT_ID", "TYPE_ID"]].dropna(subset=["TYPE_ID"])
    event_countries_df = events_df[["EVENT_ID", "COUNTRY_ID"]].dropna(
        subset=["COUNTRY_ID"]
    )

    # create csv out of unique countries and types list
    unique_countries_df = pd.DataFrame(unique_countries, columns=["COUNTRY_ID"])
    unique_types_df = pd.DataFrame(unique_types, columns=["TYPE_ID"])

    cleared_events_df = events_df.drop_duplicates(subset=["EVENT_ID"]).drop(
        columns=["COUNTRY_ID", "TYPE_ID"]
    )  # drop duplicates and event_id and type_id columns

    # Save to CSV
    convert_df_to_csv(unique_countries_df, "Countries.csv", dest_path)
    convert_df_to_csv(unique_types_df, "Types.csv", dest_path)
    convert_df_to_csv(
        cleared_events_df, "Events.csv", dest_path
    )  # pylint: disable=E1120
    convert_df_to_csv(event_types_df, "EventTypes.csv", dest_path)
    convert_df_to_csv(event_countries_df, "EventCountries.csv", dest_path)


def main():
    """Main function"""
    file_name = sys.argv[1]
    convert_json_to_csvs(file_name)  # pylint: disable=E1120


if __name__ == "__main__":
    main()
