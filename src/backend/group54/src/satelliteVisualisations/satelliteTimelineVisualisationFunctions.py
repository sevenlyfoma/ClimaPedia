import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cacheMaintainance import queryDatabase
import auxiliaryFunctions
import satelliteVisualisations.satelliteMapVisualisationFunctions as sat

END_COLOUR = 'red'
NON_END_COLOUR = 'blue'

def getEventsOfSatellites(startdate, enddate):
    res = queryDatabase ("""SELECT DISTINCT QNoSatellite, satellite.name, 
                satelliteEvent.name, date, isEnd, EventID
            FROM satellite, satelliteEvent
            WHERE satellite.QNo = satelliteEvent.QNoSatellite
            ORDER BY date ASC;""")
    
    entries = dict()
    
    minDate, maxDate = None, None
    for [satelliteID, satelliteName, eventName, date, isEnd, eventID] in res:
        entry = {
                "label": f'{satelliteName} {eventName}',
                "id": f'{eventID}',
                "point": date,
                "subentries":[],
                "defaultColour":END_COLOUR if isEnd == 'true' 
                    else NON_END_COLOUR
                }
        if f'{satelliteID} {satelliteName}' in entries:
            entries[f'{satelliteID} {satelliteName}'].append(entry)
        else:
            entries[f'{satelliteID} {satelliteName}'] = [entry]
            
        if minDate == None or minDate > date:
            minDate = date
        if maxDate == None or maxDate < date:
            maxDate = date
            
    out = []
    for key in entries:
        ended = any(list(map(lambda x: x['defaultColour'] == END_COLOUR, 
            entries[key])))
        endDate = entries[key][-1]['point'] if ended else maxDate
        out.append({
            "label":key.split(" ")[1],
            "id":key.split(" ")[0],
            "range":[entries[key][0]['point'], endDate],
            "subentries":entries[key],
            "defaultColour": "green" if not ended else 'purple'
        })
    
    jsonRetVal = {
        "entries":out,
        "clickable":True,
        "range": [minDate, maxDate]
    }
    
    return jsonRetVal

def partHTML(idval):
    res = sat.partHTML(idval)
    if res != None:
        return res
        
    res = queryDatabase("""SELECT DISTINCT name, date, isEnd
        FROM satelliteEvent
        WHERE EventID = ?;""", [idval])[0]
    
    return f"""<html><body><p>{res[0]} on {res[1]}{' terminated its service' 
        if res[2] == 'true' else ''}</p></body></html>"""