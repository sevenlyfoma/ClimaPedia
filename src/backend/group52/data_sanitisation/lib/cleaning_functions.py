"""Cleaning functions to be used in clean_data_formatting.

The following functions were copied and adapted from my (200006079)
previous coursework for CS2006, submitted 2022-04-08
"""

from typing import Optional

import re

import pandas as pd

# pylint: disable=unused-argument, no-else-return


def drop_column(df, column_name, args):
    """Drops the specified column from the dataframe.

    Dropping column method found here:
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
    [Last accessed 2022-04-06]

    Args:
        df (dataframe): the dataframe to be altered
        column_name (string): the name of the column to be dropped
        args (list): dummy argument supplied to allow for generalise function calls

    Returns:
        dataframe: the altered data frame. On an invalid input: the original data frame
    """

    try:
        df.drop(column_name, inplace=True, axis=1)
    except KeyError:
        print(
            "Failed to drop column '"
            + column_name
            + "': Column not present in dataframe"
        )
    return df


def extract_json_fields(df, column_name, args):
    """Takes a column in a dataframe filled with a json object and
    extracts the desired fields from that object as their own new columns.

    process for expanding json field found here:
    https://pandas.pydata.org/docs/reference/api/pandas.json_normalize.html
    [Last accessed 2022-04-06]

    process for reseting index found here:
    https://stackoverflow.com/a/35528185 [Last accessed 2022-04-06]

    Args:
        df (dataframe):
        the dataframe to be altered
        column_name (string):
        the name of the column to have its json fields extracted from
        args (list<string>):
        the names of the fields of the json object that will be added to the dataframe

    Returns:
        dataframe:
        the altered data frame
    """
    # Create a new dataframe out of the json object within the column
    json_df = pd.json_normalize(df[column_name], errors="raise")

    for i in json_df:  # For each column
        if i not in args:  # Drop if not specified in the arguments
            drop_column(json_df, i, [])
    # Rename the newly created columns
    # to ensure the new column name would be unique
    for i in json_df.columns:
        json_df = json_df.rename(columns={i: column_name + "_" + i})
    # Reset indexs of columns so that
    # dropped columns dont take up an index anymore
    df = df.reset_index(drop=True)
    df = pd.concat([df, json_df], axis=1)  # Combine the two data frames
    return df


# Copied and adapted code ends here


def rename_column(df, column_name, args):
    """Renames a column in a dataframe

    Args:
        df (dataframe):         the dataframe to be altered
        column_name (string):   the name of the column to be renamed
        args (list<string>):    list whose first argument is the new name of the column,
                                the argument here is a list to facilitate generalisation

    Returns:
        dataframe: the altered data frame
    """
    df = df.rename(columns={column_name: args[0]})
    return df


def split_into_columns(df, column_name, args):
    """Takes a column in a dataframe and splits it into multiple
    columns based on a delimiter in the data

    Args:
        df (dataframe):         the dataframe to be altered
        column_name (string):   the name of the column to be split
        args (list<string>):    list of arguments, first argument is the delimiter
                                on which to split the column, second onwards are
                                the new column names

    Returns:
        dataframe: the altered data frame. On an invalid input: the original data frame
    """
    new_column_names = []  # Get a list containing all the new column names
    for x in range(1, len(args)):
        new_column_names.append(args[x])

    # Method to split a column on a delimiter found here:
    # https://stackoverflow.com/questions/37333299/splitting-a-pandas-dataframe-column-by-delimiter
    # Last accessed 2023-11-02

    try:
        # Split the column into the new columns, on the delimiter specified
        df[new_column_names] = df[column_name].str.split(args[0], expand=True)
    except ValueError as error:
        print("Couldnt split columns: " + str(error))

    return df


def apply_string_mapping(df, column_name, args):
    """Takes a column in a dataframe and applys a function to all data in the column

    Args:
        df (dataframe): the dataframe to be altered
        column_name (string): the name of the column to be mapped
        args (list<string>): list of names ofmapping functions, these are specified within this file

    Returns:
        dataframe: the altered data frame. On an invalid input: the original data frame
    """
    for i in args:  # Go through each function name
        # Method to get the name of a function from within the same file found here:
        # https://stackoverflow.com/a/834451
        # Last accessed 2023-11-02
        try:
            func = globals()[i]  # Get the function
            df[column_name] = df[column_name].map(func)  # Map the column with it
        except KeyError:
            print("apply_string_mapping failed, no mapping function: " + i)
        except TypeError:
            print(
                "apply_string_mapping failed, couldnt apply function '"
                + i
                + "' as a mapping"
            )
    return df


def convert_to_float(string_num):
    """Function to be used with apply_string_mapping
    Converts a string to a fload

    Args:
        string_num (string): the number as a string

    Returns:
        float: the converted string, 0.0 on an invalid input
    """
    x = 0.0
    try:
        x = float(string_num)
    except ValueError as error:
        print(error)
    return x


def extract_q_code(string):
    """Function to be used with apply_string_mapping
    Extracts the Q code of an entry from a url

    Args:
        string (string): the url to be extracted from ie: "http://www.wikidata.org/entity/Q61021340"

    Returns:
        string: the extracted Q code ie "Q61021340", None on an invalid input
    """
    pattern_string = "[Q][0-9]+"  # Create appropriate regex pattern
    m = re.search(pattern_string, string)  # Find the pattern
    if m is None:
        return None
    return m.group()  # Return the extracted form


def reformat_lat_and_long(string):
    """Function to be used with apply_string_mapping
    Takes a formatted latitude and longitude value and reformats
    it to be something easier to deal with

    Args:
        string (string): lat and long in format "Point(long lat)"

    Returns:
        string: reformatted lat and long in format "long lat", "0 0" on an invalid input
    """
    # First extract the bracketed part
    pattern_string = r"Point\((-?[0-9]+\.?[0-9]* -?[0-9]+\.?[0-9]*)\)"
    if (m := re.search(pattern_string, str(string))) is not None:
        return m.group(1)
    else:
        return "0 0"  # If no lat and long specified, set to 0,0


def reformat_station_id(val: Optional[str]) -> str:
    """Reformat strings for station IDs.

    Arguments:
        val: The value.

    Returns:
        Reformatted string.
    """

    return "" if val is None else str(val)
