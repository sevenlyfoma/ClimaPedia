import json
import os
import sqlite3
import threading
import time
from logging import DEBUG, INFO, Logger
from typing import List, Tuple

import queries
import wikidataQuerying
from auxiliaryFunctions import (
    createLogger,
    extractCoords,
    extractQNumberFromURL,
    maybeLog,
)

FLUSH_TIMEOUT_PATH \
    = f"{os.path.dirname(os.path.dirname(__file__))}/data/flush.tmp"
DATABASE_PATH \
    = f"{os.path.dirname(os.path.dirname(__file__))}/data/database.db"
ONE_HOUR = 60 * 60                            # one hour in seconds
EDUCATION_PROP = 69

def queryDatabase(SQLquery, params = []):
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    ret = cur.execute(SQLquery, params)
    res = ret.fetchall()
    cur.close()
    conn.close()
    return res

###############################################################
#   SQL for creating the tables in the database               #
###############################################################

def __InstitutionTable() -> None:
    return """CREATE TABLE institution(
        QNo integer PRIMARY KEY,
        name varchar(255) NOT NULL,
        latitude float NOT NULL,
        longitude float NOT NULL
    );"""
    
def __AttendingTable() -> None:
    return """CREATE TABLE attending(
        QNoInstitution integer REFERENCES institution(QNo),
        QNoPerson integer REFERENCES person(QNo),
        isEducation boolean NOT NULL,
        PRIMARY KEY (QNoInstitution, QNoPerson, isEducation)
    );"""

def __PersonTable() -> None:
    return """CREATE TABLE person(
        QNo integer PRIMARY KEY,
        name varchar(255) NOT NULL,
        DOB varchar(255) NOT NULL,
        latitude float NOT NULL,
        longitude float NOT NULL,
        location varchar(255) NOT NULL,
        occupation varchar(255) NOT NULL,
        
        DOD varchar(255),
        image_url varchar(100000),
        sex_or_gender varchar(255)
    );"""
    
def __AwardTable() -> None:
    return """CREATE TABLE award(
        QNo integer PRIMARY KEY,
        name varchar(255) NOT NULL
    );"""

def __ReceivedTable() -> None:
    return """CREATE TABLE received(
        QNoAward integer REFERENCES award(QNo),
        QNoPerson integer REFERENCES person(QNo),
        PRIMARY KEY (QNoAward, QNoPerson)
    );"""
    
def __GroupTable() -> None:
    return """CREATE TABLE society(
        QNo integer PRIMARY KEY,
        name varchar(255) NOT NULL
    );"""

def __MembershipTable() -> None:
    return """CREATE TABLE membership(
        QNoGroup integer REFERENCES society(QNo),
        QNoPerson integer REFERENCES person(QNo),
        PRIMARY KEY (QNoGroup, QNoPerson)
    );"""
    
def __SatelliteTable() -> None:
    return """CREATE TABLE satellite(
        QNo integer PRIMARY KEY,
        name varchar(255) NOT NULL,
        latitude float NOT NULL,
        longitude float NOT NULL,
        image_url varchar(100000)
    );"""
    
def __SatelliteEventTable() -> None:
    return """CREATE TABLE satelliteEvent(
        EventID integer PRIMARY KEY,
        QNoSatellite integer REFERENCES satellite(QNo),
        name varchar(255) NOT NULL,
        date varchar(255) NOT NULL,
        isEnd boolean NOT NULL 
    );"""
    
def __createTables() -> None:
    """creates tables in specified database.

    Args:
        cur (sqlite3.Cursor): cursor to make changes to database.
    """
    # people and institutions
    tableSQLs = [
        __InstitutionTable(),
        __PersonTable(),
        __AttendingTable(),
        
        # awards and societies
        __AwardTable(),
        __ReceivedTable(),
        __GroupTable(),
        __MembershipTable(),

        # satellites
        __SatelliteTable(),
        __SatelliteEventTable()
    ]
    
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    for SQL in tableSQLs:
        cur.execute(SQL)
    conn.commit()
    cur.close()
    conn.close()
    
def __createFunctions() -> None:
    """create functions for use in queries
    """
    ...
    
###############################################################
#    Functions for restructuring wikidata data to database    #
###############################################################
        
def toStructurePerson(jsonDict):
    personQ = extractQNumberFromURL(jsonDict['person']['value'])
    name = jsonDict['personLabel']['value'].replace('\'', '\'\'')
    dob = jsonDict['borndate']['value'].replace('\'', '\'\'')
    lat, long = extractCoords(jsonDict['coordPerson']['value'])
    location = jsonDict['locLabel']['value'].replace('\'', '\'\'')
    occupation = jsonDict['occLabel']['value'].replace('\'', '\'\'')

    dod = jsonDict['deathDate']['value'].replace('\'', '\'\'') if 'deathDate' in jsonDict else None
    imageUrl = jsonDict['imageLabel']['value'].replace('\'', '\'\'') if 'imageLabel' in jsonDict else None
    sex = jsonDict['sexLabel']['value'].replace('\'', '\'\'') if 'sexLabel' in jsonDict else None
    return (personQ, name, dob, lat, long, location, occupation, dod, imageUrl, sex)
    
def toStructureInstitution(line:dict) -> Tuple[int, str, str]:
    """creates record to insert into institution table from JSON.

    Args:
        line (dict): JSON object representing a person attending a institution.

    Returns:
        Tuple[int, str, str]: record of a institution.
    """
    # TODO tidy up this mess and prevent SQL injection
    QNo = extractQNumberFromURL(line["educationOrEmployment"]["value"])
    name = line["educationOrEmploymentLabel"]["value"].replace("'", "''")
    lat, long = extractCoords(line["coordUni"]["value"])
    return (QNo, name, lat, long)
    
def toStructureAttending (line:dict) -> Tuple[int, int, bool]:
    """creates record to insert into attending table from JSON.

    Args:
        line (dict): JSON object representing a person attending a university.

    Returns:
        Tuple[int, int, bool]: record of a person attending a university.
    """
    #TODO tidy up this mess and prevent SQL injection
    QNoPerson = extractQNumberFromURL(
        line['person']['value'])
    QNoUniversity = extractQNumberFromURL(
        line['educationOrEmployment']['value'])
    isEducation = extractQNumberFromURL(line['educatePred']['value']) == EDUCATION_PROP
    return (QNoUniversity, QNoPerson, isEducation)
    
def toStructureReceived(jsonDict):
    personQ = extractQNumberFromURL(jsonDict['person']['value'])
    awardQ = extractQNumberFromURL(jsonDict['award']['value'])
    return (awardQ, personQ)
    
def toStructureAward(jsonDict):
    awardQ = extractQNumberFromURL(jsonDict['award']['value'])
    name = jsonDict['awardLabel']['value']
    return(awardQ, name)
    
def toStructureMembership(jsonDict):
    personQ = extractQNumberFromURL(jsonDict['person']['value'])
    groupQ = extractQNumberFromURL(jsonDict['group']['value'])
    return (groupQ, personQ)
    
def toStructureGroup(jsonDict):
    groupQ = extractQNumberFromURL(jsonDict['group']['value'])
    name = jsonDict['groupLabel']['value']
    return(groupQ, name)
    
def toStructureSatellite(jsonDict):
    satelliteQ = extractQNumberFromURL(jsonDict['satellite']['value'])
    name = jsonDict['satelliteLabel']['value']
    lat, long = extractCoords(jsonDict['coords']['value'])
    imagePath = jsonDict['imageLabel']['value'] if 'imageLabel' in jsonDict else None
    return (satelliteQ, name, lat, long, imagePath)
    
#indexed table
def toStructureSatelliteEvent(data):
    jsonDict, i = data
    satelliteQ = extractQNumberFromURL(jsonDict['satellite']['value'])
    name = jsonDict['eventLabel']['value']
    date = jsonDict['eventTime']['value']
    isEnd = jsonDict['end']['value']
    return (i, satelliteQ, name, date, isEnd)

###############################################################
#     Functions for adding wikidata data to the database      #
###############################################################

def __fillPersonTable() -> None:
    return toStructurePerson, \
        """INSERT OR REPLACE INTO person VALUES 
        (?,?,?,?,?,?,?,?,?,?)"""

def __fillInstitutionTable() -> None:
    return toStructureInstitution, \
        'INSERT OR IGNORE INTO institution VALUES (?,?,?,?)'

def __fillAttendingTable() -> None:
    return toStructureAttending, \
        """INSERT OR IGNORE INTO attending(QNoInstitution, 
        QNoPerson, isEducation) VALUES (?,?,?)"""

def __fillReceivedTable() -> None:
    return toStructureReceived, \
        """INSERT OR IGNORE INTO received(QNoAward, 
        QNoPerson) VALUES (?,?)"""

def __fillAwardTable() -> None:
    return toStructureAward, \
        """INSERT OR IGNORE INTO award(QNo, 
        name) VALUES (?,?)"""

def __fillMembershipTable() -> None:
    return toStructureMembership, \
        """INSERT OR IGNORE INTO membership(QNoGroup, 
        QNoPerson) VALUES (?,?)"""

def __fillGroupTable() -> None:
    return toStructureGroup, \
        """INSERT OR IGNORE INTO society(QNo, 
        name) VALUES (?,?)"""

def __fillSatelliteTable() -> None:
    return toStructureSatellite, \
        """INSERT OR IGNORE INTO satellite(QNo, 
        name, latitude, longitude, image_url) VALUES (?,?,?,?,?)"""

def __fillSatelliteEventTable() -> None:
    return toStructureSatelliteEvent, \
        """INSERT OR IGNORE INTO satelliteEvent(EventID, QNoSatellite, 
        name, date, isEnd) VALUES (?,?,?,?,?)"""
    
def __fillTable(resJson, SqlQuery, structureFunc, indexesNeeded = False):
    if not indexesNeeded:
        lines = list(map(structureFunc, resJson['results']['bindings']))
    else:
        lines = list(map(structureFunc, list(zip(\
                resJson['results']['bindings'],
                list(range(len(resJson['results']['bindings'])))))))
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    cur.executemany(SqlQuery,lines)
    conn.commit()
    cur.close()
    conn.close()
    
###############################################################
#   functions for running and maintaining the cache           #
###############################################################

def __refreshCache(logger: Logger = None) -> None:
    """refreshes the cache in the database accessed by conn and cur.

    Args:
        conn (sqlite3.Connection): connection to the database.
        cur (sqlite3.Cursor): cursor to make changes to the database.
        logger (Logger, optional): logger to use. Defaults to None.
    """
    maybeLog("Innovations and People - refreshing cache", logger)
    #TODO test for SQL injections
    
    conn = sqlite3.connect(DATABASE_PATH)
    cur = conn.cursor()
    for tableName in ["person", "institution", "attending", "award", "received",
            "society", "membership", "satellite", "satelliteEvent"]:
        cur.execute(f"DELETE FROM {tableName}")
    conn.commit()
    cur.close()
    conn.close()
    
    wikidataRes = [
        wikidataQuerying.SPARQLquery(queries.universityQueryPeople()),#people
        wikidataQuerying.SPARQLquery(queries.awardsQueryPeople()),#awards
        wikidataQuerying.SPARQLquery(queries.membershipQueryPeople()),#society
        wikidataQuerying.SPARQLquery(queries.satellitesQuery())#satellites
    ]
    
    tableInsertions = [
        (0, __fillPersonTable, False),
        (0, __fillInstitutionTable, False),
        (0, __fillAttendingTable, False),
        
        (1, __fillAwardTable, False),
        (1,__fillReceivedTable, False),
        
        (2, __fillGroupTable, False),
        (2, __fillMembershipTable, False),
        
        (3, __fillSatelliteTable, False),
        (3, __fillSatelliteEventTable, True)
    ]
    
    for dataIndex, sqlFunc, needsIndex in tableInsertions:
        structureFunc, sqlQuery = sqlFunc()
        __fillTable(wikidataRes[dataIndex], sqlQuery, structureFunc, needsIndex)

def __cacheFlusher(logger: Logger = None, freq: float = 0.2) -> None:
    """function to be run by the thread which manages the freshness of the
    cache.

    Args:
        logger (Logger, optional): logger to use. Defaults to None.
        freq (float, optional): number of times to refresh per hour. Defaults
        to 1.0.
    """
    maybeLog("Innovations and People - cache flushing thread started", logger)
    
    flushTimeFile = open(FLUSH_TIMEOUT_PATH, "r+")
    while True:
        timeDiff = time.time() - float(flushTimeFile.read())
        flushTimeFile.seek(0)
        if timeDiff > (ONE_HOUR / freq):
            maybeLog(f"""Innovations and People - {timeDiff} s have passed 
                     since last refresh - refreshing""",logger)
            __refreshCache(logger)
            flushTimeFile.write(str(time.time()))
            flushTimeFile.seek(0)
            maybeLog("Innovations and People - cache has been renewed", logger)
        time.sleep(ONE_HOUR / freq)
        
def __initDatabase(logger: Logger = None) -> None:
    """creates the database and cache timeout file, then populates the 
    database.

    Args:
        logger (Logger, Optional): logger to use. Defaults to None.
    """
    flushFile = open(FLUSH_TIMEOUT_PATH, "w")
    flushFile.write(str(time.time()))
    __createTables()
    __createFunctions()
    flushFile.close()
    maybeLog("Innovations and People - successfully rebuilt database", logger)
    __refreshCache(logger)
        
def init(logger: Logger = None, freq: float = 1.0):
    """initialises database and thread to manage it.

    Args:
        logger (Logger, optional): logger to use. Defaults to None.
        freq (float, optional): number of times to refresh the database per
        hour. Defaults to 1.0.
    """
    maybeLog("Innovations and People - starting init", logger)
    if not os.path.isdir("group54/data"):
        maybeLog("Innovations and People - data directory missing...", logger)
        os.mkdir("group54/data")
    if not os.path.isfile(DATABASE_PATH):
        maybeLog("""Innovations and People - database files missing, 
                attempting to rebuild...""", logger)
        __initDatabase(logger)
    # start cache maintainer thread
    cacheMaintainer = threading.Thread(target = __cacheFlusher, 
            args = [logger, freq])
    cacheMaintainer.start()