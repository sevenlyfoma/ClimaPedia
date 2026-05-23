"""Script to clean history data through cleaning pipelines"""

import os
import sys

from . import extract_history_data, prepare_csv, reorder_columns


def main():
    """Main function that is called if program is run as main, runs body function with cmd args"""
    clean_all_histories(sys.argv[1], sys.argv[2], sys.argv[3])


def clean_all_histories(
    reordering_file_name, origin_directory_name, destination_directory_name
):
    """

    Args:
        reordering_file_name                    filepath of reordering txt that tells
                                                which columns to place where

        origin_file_name (string):              filepath to the json to which the mappings will
                                                be applied
        destination_file_name (string):         filepath to the json in which the altered
                                                json will be stored
    """

    # Make destination for cleaned histories if it doesnt exist
    if not os.path.exists(destination_directory_name):
        os.makedirs(destination_directory_name)

    # Get all files in directory
    data_list = os.listdir(origin_directory_name)

    # Check if monthly data, only monthly is supported
    new_data_list = []
    for i in data_list:
        print(i[-6])
        if i[-6] == "M":
            new_data_list.append(i)

    # Create locations for temporary files, each stage of the cleaning
    # pipeline gets saved into one
    temp_file_name = destination_directory_name + "/temp.json"
    temp_file_name2 = destination_directory_name + "/temp2.json"

    # Go through all data files
    for i in new_data_list:
        # Get full path
        origin_file_name = origin_directory_name + "/" + i
        # Get full path of csv to be created
        destination_file_name = destination_directory_name + "/" + i[:-4] + "csv"

        extract_history_data.extract_history_data(origin_file_name, temp_file_name)
        reorder_columns.reorder_columns(
            reordering_file_name, temp_file_name, temp_file_name2
        )
        prepare_csv.prepare_csv(temp_file_name2, destination_file_name)

        # Remove temp files
        os.remove(temp_file_name)
        os.remove(temp_file_name2)


if __name__ == "__main__":
    main()
