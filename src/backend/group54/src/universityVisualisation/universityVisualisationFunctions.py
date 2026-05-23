import os
import sys
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cacheMaintainance import queryDatabase
import sqlite3
from datetime import datetime

import auxiliaryFunctions


# format according to protocol
def cleanDoB(dob):
    """
    Takes in a string of the date of birth in ISO 8601 format and returns a 
    string of the date of birth in the format YYYY-MM-DD.

    Args:
        dob (str): A string representing the date of birth in ISO 8601 format.

    Returns:
        str: A string representing the date of birth in the YYYY-MM-DD format.
    """

    return dob.split("T")[0]

def institution(startDate: str, endDate: str):
    """
    Fetches and returns data of institutions that have had students born 
    within a specified date range.

    Args:
        startDate (str, optional): The start of the date range for filtering 
            scientists' DOBs.
                Defaults to None, which can be replaced with a default value 
                as needed.
        endDate (str, optional): The end of the date range for filtering 
            scientists' DOBs.
                Defaults to None, which can be replaced with a default value 
                as needed.
    
    Returns:
        dict: A dictionary containing formatted data of institutions including
            coordinates, series information, IDs, and labels.
    """
    res = queryDatabase("""
            SELECT DISTINCT institution.QNo, institution.name, institution.longitude, institution.latitude, COUNT(*) AS size
            FROM institution
            JOIN attending ON institution.QNo = attending.QNoInstitution
            JOIN person ON attending.QNoPerson = person.QNo
            WHERE (date(dob) <= ? AND (date(IFNULL(dod, DATE(dob, '+72 years'))) >= ?))
            GROUP BY institution.QNo, institution.name, institution.longitude, institution.latitude;
        """, (endDate, startDate))
    
     # Process the query results and format the data into a dictionary before 
     # returning
    formatted_data = {
        "coords": [[row[2], row[3]] for row in res], # latitude,longitude
        "series": [0 for _ in res], # Assume one series for all institutions
        "seriesLegend": [{
            "name": "Institutions",
            "colour": "blue",
            "shape": "circle"
        },
          {
            "name": "Scientists",
            "colour": "red",
            "shape": "star"
        }],
        "values": [1 for i in res],
        "sizes": (x := [row[4] for row in res]),
        "sizeRange": [min(x), max(x)],
        "ids": [row[0] for row in res],  # institution QNo as IDs
        "labels" : [row[1] for row in res],
    }
    return formatted_data

def scientistName(startDate: str, endDate: str, uni_id: str):
    """
    Fetches and returns a list of scientists from specified institutions, 
    filtered by DOB range.

    Args:
        startDate (str): The start date for the DOB range filter.
        endDate (str): The end date for the DOB range filter.
            latest date is used.
        uni_ids (str): A tuple of institution IDs to filter the scientists
            by their attending institutions.
    Raises:
        ValueError: If no institution IDs are provided in the `uni_ids` 
        argument.

    Returns:
        dict: A dictionary with the formatted data of person including 
            coordinates, series information, IDs, and labels.
    """
    if not uni_id:
        raise ValueError("No institution IDs provided.")
    
    # Create the SQL query string with the dynamic placeholders
    query = f"""
        SELECT DISTINCT person.QNo, person.name, person.longitude, 
            person.latitude
        FROM person
        JOIN attending ON person.QNo = attending.QNoPerson
        WHERE (attending.QNoInstitution = ?) AND (date(dob) <= ? AND (date(IFNULL(dod, DATE(dob, '+72 years'))) >= ?));
    """

    # Execute the query using the uni_ids for the IN clause and startDate, 
    # endDate for the range
    res = queryDatabase(query, (uni_id, endDate, startDate))

    
     # Format the data before returning
    formatted_data = {
        "coords": [[row[2], row[3]] for row in res], # latitude,longitude
        "series": [1 for _ in res], # Assume one series for all scientists
        "values": [1 for i in res],
        "ids": [f'{uni_id}_{row[0]}' for row in res], # QNo as IDs
        "labels": [row[1] for row in res],
    }

    return formatted_data

def makeMetadata():
    """
    Looks at the data and makes the meta data for the dynamic meta points

    - timeData: list of DoBs unique and sorted.
    - range: tuple of min and max DoB.
    - period:
        {
            'unit': string of unit of time (e.g., second, minute, hour, day,
            month, year),
            'value': int of the value of the unit, defaults to 1.
        }
    - batchLoad: boolean of whether the data is loaded all at once.
    - persistent: boolean of whether the data is persistent.
    """
    # Execute a query to select dates of birth from person
    data = queryDatabase("SELECT DISTINCT dob FROM person ORDER BY dob ASC;")
    data = [item[0] for item in data]

    # Define the period for the metadata
    period = {"unit": "day", "value": 1}

    # Compile the metadata dictionary
    metadata = {
        "timeData": {
            "times": data,
            "range": (auxiliaryFunctions.incrementYearDate(-100, data[0]), 
                      auxiliaryFunctions.incrementYearDate(100,data[-1])),
            "period": period,
            "batchLoad": False,
            "persistent": False
        }
    }

    return metadata
