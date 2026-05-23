import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from chartUtils import Line
from chartUtils import Point
from chartUtils import makeLineChartMetaData as makeMetadata

def getData():
    """
        Get the data for the line chart
    """

    ## SQL Query, check peopleInstitutionsPieChart.py for an example

def exampleLineChart():
    """
        Can use Line and Point classes to represent the data for the line chart. 
        A point is a single point on the line chart and a line is an array of points.
        Example:

            point1 = Point(1, 2)
            point1.getPoint() # [1, 2]

            point2 = Point(2, 3)
            point2.getPoint() # [2, 3]

            Line = Line([point1, point2])
            Line.getLine() # [[1, 2], [2, 3]]

        Then you can use the makeMetadata function to create the metadata for the line chart
        Example:

            lines = [Line([point1, point2])]
            ids = ["line1"]

            # for 1 line chart with 2 points
            metaData = makeMetadata(lines, ids)
            metaData # {"data": [[[1, 2], [2, 3]]], "ids": ["line1"]}

            # for 2 line charts with 2 points each
            metaData = makeMetadata(lines, ids)
            metaData # {"data": [[[1, 2], [2, 3]], [[1, 2], [2, 3]]], "ids": ["line1", "line2"]}
    """
    data = getData()

    # Process the data into Line and Point objects

    metaData = makeMetadata(data)
    return metaData