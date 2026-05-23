import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cacheMaintainance import queryDatabase

from chartUtils import makeChartEntries
from chartUtils import makePieChartMetadata as makeMetadata

def getData():
    """
        This function will be getting the top 5 institutions by attendance, 
        and then group everyone else into an "Other" category. Will return an
        array of of the form [[QNo1, Name1, Count1], [QNo2, Name2, Count2], 
        [QNo3, Name3, Count3], [QNo4, Name4, Count4], [QNo5, Name5, Count5], 
        [-1, Other, CountOther]]
    """

    top_institutions = queryDatabase("""
        SELECT institution.QNo, institution.Name, 
            COUNT(attending.QNoPerson) as NumberOfPeople
        FROM attending
        JOIN institution ON attending.QNoInstitution = institution.QNo
        GROUP BY institution.QNo
        ORDER BY NumberOfPeople DESC
        LIMIT 5;
    """)          

    other_institutions = queryDatabase("""
        SELECT 'Other' AS QNoEducation, 
            COUNT(attending.QNoPerson) as NumberOfPeople
        FROM attending
        WHERE attending.QNoInstitution NOT IN (
            SELECT institution.QNo
            FROM attending
            JOIN institution ON attending.QNoInstitution = institution.QNo
            GROUP BY institution.QNo
            ORDER BY COUNT(attending.QNoPerson) DESC
            LIMIT 5
        );
    """)[0]

    # Add '-1' to the front of the other_institutions tuple to make it 
    # uniform with the other tuples
    other_institutions = (-1,) + other_institutions

    list_of_institutions = top_institutions + [other_institutions]
    return list_of_institutions

def peopleInstitutionsPieChart():
    data = getData()
    chartEntries = makeChartEntries(data)
    metaData = makeMetadata(chartEntries)
    return metaData