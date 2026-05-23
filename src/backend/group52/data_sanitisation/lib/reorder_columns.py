"""Script to reorder the column order in a json file"""

import sys

import pandas as pd
from pandas import DataFrame


def main():
    """Calls reorder with the command line arguments"""
    reorder_columns(sys.argv[1], sys.argv[2], sys.argv[3])


def reorder_columns(reordering_file_name, origin_file_name, destination_file_name):
    """Takes a txt file specifying the desired order of the columns in a json file,
    and reorders the columns.

    Reordering method found here:
    https://sparkbyexamples.com/pandas/pandas-change-position-of-a-column/
    last accessed [2023-11-01].

    Args:
        reordering_file_name (string): filepath to txt specifying the new column order
        origin_file_name (string): filepath to the json to be reordered
        destination_file_name (string): filepath to the destination of the reordered json
    """
    df = pd.read_json(origin_file_name)  # Read the json into a data frame

    if DataFrame(df).empty:
        DataFrame(df).to_json(destination_file_name)  # Save as
        return

    # Open and read in the contents of the ordering text file
    with open(reordering_file_name, encoding="UTF-8") as f:
        text = f.read()
        f.close()

    in_order_args = text.strip().split(
        ","
    )  # Split the ordering on the delimiter into a list
    # Reorder the dataframe with the list of column names
    df = df[in_order_args]

    df.to_json(
        destination_file_name, orient="records", indent=1, date_format="iso"
    )  # Save as


if __name__ == "__main__":
    main()
