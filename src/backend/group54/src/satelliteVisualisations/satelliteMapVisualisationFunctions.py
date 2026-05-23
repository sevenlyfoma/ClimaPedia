import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cacheMaintainance import queryDatabase
import auxiliaryFunctions

TIMELINE_PATH = '/timeline?views=group54.satelliteTimelines'

def makeMapMetadata():
    data = queryDatabase("SELECT DISTINCT date FROM satelliteEvent ORDER BY date ASC")
    dates = [item[0] for item in data]
        
    period = {
        "unit": "day",
        "value": 1
    }
    
    metadata = {
        "timeData": {
            "times": dates,
            "range": (auxiliaryFunctions.incrementYearDate(-5, dates[0]),
                      auxiliaryFunctions.incrementYearDate(5, dates[-1])),
            "period": period,
            "batchLoad": False,
            "persistent": False
        }
    }
    
    return metadata

def getMapJsonForPoints(startDate, endDate):
    data = queryDatabase("""SELECT DISTINCT QNo, name, latitude, longitude
        FROM satellite
            
        WHERE EXISTS (SELECT date 
            FROM satelliteEvent
            WHERE QNo = satelliteEvent.QNoSatellite
            AND (date(date) BETWEEN ? AND ?))
            
        OR (EXISTS (SELECT date 
            FROM satelliteEvent
            WHERE QNo = satelliteEvent.QNoSatellite
            AND (date(date) > ?))
            
            AND EXISTS (SELECT date 
            FROM satelliteEvent
            WHERE QNo = satelliteEvent.QNoSatellite
            AND (date(date) < ?)));""", 
            [startDate, endDate, endDate, startDate])
    
    coords, ids, labels = [],[],[]
    for Qno, name, latitude, longitude in data:
        ids.append(Qno)
        coords.append((longitude, latitude))
        labels.append(name)
    
    json_data = {
        "coords": coords,
        "ids": ids,
        "labels": labels,
        "clustering": True,
        "clickable": True
    }

    return json_data

def getListEvents(satelliteID):
    data = queryDatabase("""SELECT DISTINCT satelliteEvent.name, date
            FROM satelliteEvent
            WHERE QNoSatellite = ? 
            ORDER BY date ASC;""",[satelliteID])
    return data

def getSatelliteInfo(satelliteID):
    data = queryDatabase(f"""SELECT DISTINCT name, image_url
            FROM satellite
            WHERE QNo = ?;""", [satelliteID])
    return data

def partHTML(satelliteID):
    events = getListEvents(satelliteID)
    if len(events) == 0:
        return None
    satelliteInfo = getSatelliteInfo(satelliteID)[0]

    image = f'<img src="{satelliteInfo[1]}">' if satelliteInfo[1] else ''
    return f"""<html><body>
    <div>
    <h1>{satelliteInfo[0]}</h1>{image}
    <ol><li> {'</li><li>'.join(list(map(lambda x:f'{x[0]} on {x[1]}',events)))} 
    </li></ol>
    <p><a href='{TIMELINE_PATH}'>View as timeline</a></p>
    </div></body></html>"""