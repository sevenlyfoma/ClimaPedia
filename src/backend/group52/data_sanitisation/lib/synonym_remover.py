"""Script to change synonym fields in json into unified field"""

import json
import sys

# This file is currently not used in the data cleaning process, it may be needed at a later date


def main():
    "Calls remove synonyms with the command line arguments"
    remove_synonyms(sys.argv[1], sys.argv[2], sys.argv[3])


def remove_synonyms(synonym_file_name, data_file_name, destination_file_name):
    """Function to rename json fields based on potential synonyms

    Args:
        synonym_file_name (string): filepath to json file which contains synonym data
        data_file_name (string): filepath to json file containing synonyms to remove
        destination_file_name (string): filepath to save cleaned data into
    """

    # First Get Synonym List
    with open(synonym_file_name, encoding="UTF-8") as synonym_file:
        synonym_data = json.load(synonym_file)

    # Second get data itself
    with open(data_file_name, encoding="UTF-8") as data_file:
        data = json.load(data_file)

    new_data = []
    count = 0
    for entry in data:  # Go through every entry in the data
        new_data.append(entry.copy())  # Copy data into new data object
        for field in entry:  # Go through every field in the entry
            for synonym_entry in synonym_data:  # Go through every possible synonym
                if (
                    field in synonym_entry["synonyms"]
                ):  # If the field is a synonym of another
                    new_data[count][synonym_entry["fieldname"]] = entry[
                        field
                    ]  # Rename it
                    new_data[count].pop(field)
        count += 1
    with open(destination_file_name, "w", encoding="UTF-8") as destination_file:
        json.dump(new_data, destination_file)  # Write the copied and changed data


if __name__ == "__main__":
    main()
