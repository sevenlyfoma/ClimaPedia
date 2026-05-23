"""Main cleaning script
This code was adapted from my (200006079) previous coursework for CS2006, submitted 2022-04-08"""

import json
import sys

import pandas as pd

from . import cleaning_functions


def main():
    """Calls clean data formatting with the command line arguments"""
    clean_data_formatting(sys.argv[1], sys.argv[2], sys.argv[3])


def clean_data_formatting(
    refinement_mappings_file_name, origin_file_name, destination_file_name
):
    """Takes a set of mappings in json format, the name of a json file,
    and applies those mappings, saving the results in another file

    Args:
        refinement_mappings_file_name (string): filepath to the mappings json file
        origin_file_name (string):              filepath to the json to which the mappings will
                                                be applied
        destination_file_name (string):         filepath to the json in which the altered
                                                json will be stored
    """
    with open(origin_file_name, "r+", encoding="UTF-8") as origin_file:
        data = json.load(origin_file)

    if isinstance(data, dict):
        data = [data]

    # print(type(data))

    df = pd.DataFrame.from_dict(data)

    if df.empty:
        df.to_json(destination_file_name, orient="records", indent=1, date_format="iso")
        return

    # Read the mappings into a json object
    with open(refinement_mappings_file_name, encoding="UTF-8") as f:
        arguments = json.load(f)

    for i in arguments:  # Go through each column specified in the mappings
        # Apply the cleaning functions specified on that column
        try:
            df = apply_cleaning_function(
                df, i, arguments[i]["cleaningFuncs"], arguments[i]["cleaningArgs"]
            )
        except KeyError:
            pass

    # Save mapped data into new json, other arguments make result more readable
    df.to_json(destination_file_name, orient="records", indent=1, date_format="iso")


def apply_cleaning_function(df, column_name, cleaning_funcs, args):
    """Takes a dataframe, a column from that dataframe,
    and applys specified cleaning functions to that column.

    Method for calling a function with the string of its name found here:
    https://stackoverflow.com/a/3071 [Last accessed 2023-11-02].

    Args:
        df (dataframe): the dataframe holding the data to be cleaned
        column_name (string): the name of the column to have cleaning functions applied to it
        cleaning_funcs (list<string>): the names of all the cleaning functions to be applied
        args (list<list<string>>): a list of lists of arguments, each corresponding to an
        associated cleaning function

    Returns:
        dataframe: the dataframe with the specified column cleaned
    """
    i = 0
    for i_func in cleaning_funcs:  # Go through each cleaning function
        # Get the cleaning function from its name from cleaning_functions.py
        function_to_apply = getattr(cleaning_functions, i_func)
        # Then apply the function with the corresponding arguments
        df = function_to_apply(df, column_name, args[i])
        i += 1
    return df


if __name__ == "__main__":
    main()
