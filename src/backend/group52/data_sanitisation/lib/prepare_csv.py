"""Script to turn json into csv"""

import sys

import pandas as pd


def main():
    """Calls prepare csv with the command line arguments"""
    prepare_csv(sys.argv[1], sys.argv[2])


def prepare_csv(origin_file_name, destination_file_name):
    """Takes a json file and converts it to csv

    Args:
        origin_file_name (string): the file name of the json
        destination_file_name (string): the file name where the csv will be stored
    """
    df = pd.read_json(origin_file_name, typ="frame")  # Read in json

    df = pd.DataFrame(df).drop_duplicates()  # Get rid of duplicate rows
    df.to_csv(
        destination_file_name, index=False, header=False, sep=";", na_rep="\\N"
    )  # Save as csv


if __name__ == "__main__":
    main()
