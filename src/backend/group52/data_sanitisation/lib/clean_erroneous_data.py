"""File to clean erroneous json data,
currently not necessary for our program, but might become so later"""

import json
import sys
import shutil


def main():
    """Main fucntion, runs clean_erroneous_data with cmd arguments"""
    clean_erroneous_data(sys.argv[1], sys.argv[2])


def clean_erroneous_data(errorneous_data_file_name, destination_file_name):
    """Function to remove errors in json formatting

    Args:
        errorneous_data_file_name (string):
        the name of the file containing potentially badly formatted json
        destination_file_name (string):
        the name of the destination to store the cleansed json
    """
    with open(errorneous_data_file_name, encoding="UTF-8"):
        # Copy the file to the destination
        shutil.copyfile(errorneous_data_file_name, destination_file_name)
    error_free = False
    # Attempt to parse the json repeatedly until it no longer throws any JSONDecodeErrors
    while not error_free:
        error_free = True
        with open(destination_file_name, "r+", encoding="UTF-8") as dest_file:
            try:
                json.load(dest_file)
            except json.JSONDecodeError as error:
                """Method for python error checking found here:
                https://docs.python.org/3/tutorial/errors.html [last accessed 2023-10-25]
                """
                error_free = False
                # If there is an error pass to handleError, with the error and the file
                handle_error(error, dest_file)
            error_free = True


def handle_error(error, file):
    """Function to respond to an error in json parsing
    Skeleton function, can be expanded upon more with better error checking

    Args:
        error (error):  error object given by exception, contains details of
                        what caused the exception
        file (file):    the open file
    """
    if error.msg == "Expecting value":
        handle_bad_property_or_value(error, file, "Missing Value", [",", "}", "]"])
    elif error.msg == "Expecting property name enclosed in double quotes":
        handle_bad_property_or_value(error, file, "Missing Property", [":"])
    else:  # Otherwise quit out, due to not being able to fix the error
        print("There was an error in parsing that could not be dealt with:")
        print(error)
        file.close()
        sys.exit()


def handle_bad_property_or_value(error, file, no_entry_string, ending_chars):
    """Given a bad property or value error, try to rectify the situation

    Args:
        error (error):  error object given by exception, contains details
                        of what caused the exception
        file (file):    the open file
        no_entry_string (string):   if the value or property is missing,
                                    what should it be replaced by
        ending_chars (list<string>):    if the value or property is not missing
                                        what could it be terminated by e.g "," or "}"
    """
    nextChar = ""
    error_string = ""

    file.seek(error.pos)  # Move read 'head' to position of error
    nextChar = file.read(1)

    # Read characters into ending string until reacing a termianting char
    while nextChar not in ending_chars:
        error_string += nextChar
        nextChar = file.read(1)

    remainingText = file.read()  # Read in the remainder of the file

    file.seek(error.pos)  # Go to the position of the error
    if (
        len(error_string) == 0
    ):  # If the value or propety is missing, isnert appropriate string
        file.write('"' + no_entry_string + '"' + nextChar)
    else:  # Otherwise enclose property or value in double quotes
        file.write('"' + error_string + '"' + nextChar)
    # Write the remaineder of the file
    file.write(remainingText)


if __name__ == "__main__":
    main()
