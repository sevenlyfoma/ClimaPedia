import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from chartUtils import makeChartEntries
from chartUtils import makeBarChartMetaData as makeMetadata

def getData():
    """
        Get the data for the bar chart, must return an array of the form 
        [[QNo1, Name1, Count1], [QNo2, Name2, Count2] ...]
    """

    ## SQL Query, check peopleInstitutionsPieChart.py for an example

def exampleBarChart():
    data = getData()
    chartEntries = makeChartEntries(data)
    metaData = makeMetadata(chartEntries)
    return metaData

