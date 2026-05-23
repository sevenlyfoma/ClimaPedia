import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import cacheMaintainance

from chartUtils import Line
from chartUtils import Point
from chartUtils import makeLineChartMetaData as makeMetadata

def getData():
    """
        Get the data for the line chart

        Will need data for peple over time
    """

    ## SQL Query, check peopleInstitutionsPieChart.py for an example
    
    conn = sqlite3.connect(cacheMaintainance.DATABASE_PATH)
    cur = conn.cursor()

    # Query to select all of the DOB's of the people
    query = """
        SELECT DOB FROM person;
    """

    cur.execute(query)
    data = cur.fetchall()

    # Split the date and time for each of the DOB's
    for i in range(len(data)):
        data[i] = data[i][0].split("T")[0]

    return data

def peopleOverTimeLineChart():
    """
        Can use Line and Point classes to represent the data for the line 
        chart. A point is a single point on the line chart and a line is an
        array of points.
        Example:

            point1 = Point(1, 2)
            point1.getPoint() # [1, 2]

            point2 = Point(2, 3)
            point2.getPoint() # [2, 3]

            Line = Line([point1, point2])
            Line.getLine() # [[1, 2], [2, 3]]

        Then you can use the makeMetadata function to create the metadata for 
        the line chart
        Example:

            lines = [Line([point1, point2])]
            ids = ["line1"]

            # for 1 line chart with 2 points
            metaData = makeMetadata(lines, ids)
            metaData # {"data": [[[1, 2], [2, 3]]], "ids": ["line1"]}

            # for 2 line charts with 2 points each
            metaData = makeMetadata(lines, ids)
            metaData # {"data": [[[1, 2], [2, 3]], [[1, 2], [2, 3]]], 
                "ids": ["line1", "line2"]}
    """
    data = getData()

    yearCounts = {}
    for date in data:
        # Extract the year from the date
        year = date[:4]  # e.g., '1920'
        
        # Add the count to the appropriate year in the new dictionary
        if year in yearCounts:
            yearCounts[year] += 1
        else:
            yearCounts[year] = 1         

    # Sort the dictionary by keys (years) in ascending order
    yearCounts = {k: yearCounts[k] for k in sorted(yearCounts)}
    
    # print(yearCounts)

    # Process the data into Line and Point objects
    points = []
    for i, (year, count) in enumerate(yearCounts.items()):
        point = Point(year, count)
        points.append(point)

    line = Line(points)
    ids = ["line1"]

    meta = makeMetadata(
        [line], 
        ids, 
        styles=[{"showMarkers":False, "shape":"linear", "line":"solid"}], 
        xAxis={"title":"Year of Birth"}, 
        yAxis={"title":"Number of People"}, 
        title="Atmospheric Scientists Over Time")

    return meta