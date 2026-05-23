import json
import os
import sqlite3
import sys
import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from cacheMaintainance import queryDatabase

def getPersonDetails(QNo):
    res = queryDatabase("""SELECT name, dob, location, dod, sex_or_gender, 
        image_url
        FROM person 
        WHERE qNo = ?;""", [QNo])
    return res[0] 

def getInstitutions(QNo, isEducation = True):
    res = queryDatabase(f"""SELECT institution.name
        FROM institution, attending
        WHERE attending.QNoPerson = ?
        AND attending.QNoInstitution = institution.QNo
        AND {'NOT' if not isEducation else ''} attending.isEducation;""", 
            [QNo])
    return [item[0] for item in res]

def getAwards(QNo):
    res = queryDatabase("""SELECT award.name
        FROM award, received
        WHERE received.QNoPerson = ? and award.QNo = received.QNoAward;""", 
            [QNo])
    return [item[0] for item in res]

def getOrganisationNames(QNo):
    res = queryDatabase("""SELECT society.name
        FROM society, membership
        WHERE membership.QNoPerson = ? 
        AND society.QNo = membership.QNoGroup;""", [QNo])
    return [item[0] for item in res]

def generateHTMLBiography(QNo: int) -> str:
    name, dob, location, dod, sex_or_gender, image_url = getPersonDetails(QNo)
    educationNames = getInstitutions(QNo) # list of singles
    otherAffiliations = getInstitutions(QNo, False) # list of singles
    awardNames = getAwards(QNo)
    societies = getOrganisationNames(QNo)
    
    image = f'<img src = "{image_url}">' if image_url != None else ''
    deathNote = f"and died on {dod.split('T')[0]}" if dod else ''
    
    educationString \
        = f"{', '.join(educationNames[:-1])}, and {educationNames[-1]}" \
        if len(educationNames) > 1 else educationNames[0] \
        if len(educationNames) == 1 else ''
    
    employerString \
        = f"{', '.join(otherAffiliations[:-1])}, and {otherAffiliations[-1]}"\
        if len(otherAffiliations) > 1 else otherAffiliations[0] \
        if len(otherAffiliations) == 1 else ''
    
    pronoun \
        = 'He' if sex_or_gender == 'male' else 'She' \
        if sex_or_gender == 'female' else 'They'
    
    awardString \
        = f"""received the following awards:
        <ul>{"".join([f'<li>{awardName}</li>' 
            for awardName in awardNames])}</ul>""" \
        if len(awardNames) > 0 else ''
    
    societyString \
        = f"""<p>{'and' if awardString != '' else ''} 
        was a member of the following groups:</p>
        <ul>{"".join([f'<li>{society}</li>' 
            for society in societies])}</ul>""" \
        if len(societies) > 0 else ''
    
    htmlContent = f"""
        <html><body>
        <h1>{name}</h1>
        {image}
        <p>Born in {location} on {dob.split('T')[0]} {deathNote} 
        {f', {name}' if educationString != '' or employerString != '' else ''} 
        {f'studied at {educationString}' if educationString != '' else '.' }
        {'; and' if educationString != '' and employerString != '' else '.' 
            if educationString != '' else ''} 
        {f'was employed by {employerString}.' if employerString != '' else ''}
        
        {pronoun if societyString != '' or awardString != '' else ''} 
        {awardString} 
        {societyString}
        </p>
        </body></html>
    """
    return htmlContent

def getJsonForPoints(startDate: str, endDate: str, isSexSegregated: bool = False):
    """
    Queries the database for the persons and returns a json object
    already formatted for the Map + Points protocol, as found at
    https://gitlab.cs.st-andrews.ac.uk/cs3099sg5/project-code/-/wikis/Protocol
    on 2/11/2023
    """

    lifeExpectancy = 72

    res = queryDatabase(f"""SELECT qNo, name, dob, sex_or_gender,dod, 
        latitude, longitude
        FROM person 
        WHERE (date(dob) <= ? 
        AND (date(IFNULL(dod, DATE(dob, '+{lifeExpectancy} years'))) >= ?));""",
        (endDate, startDate))

    coords = []
    ids = []
    labels = []
    series = []
    
    sexSeries = {"male":0, "female":1}

    for row in res:
        qNo, name, dob, sex, dod, latitude, longitude = row
        lifePeriod = cleanLifePeriod(dob, dod, lifeExpectancy)

        coords.append((longitude, latitude))
        ids.append(qNo)
        labels.append(f"{name}, {lifePeriod}")
        if isSexSegregated:
            series.append(sexSeries[sex] if sex in sexSeries else 2)

    # create json object for the whole data
    json_data = {
        "coords": coords,
        "ids": ids,
        "labels": labels,
        "clustering": True,
        "clickable": True
    }
    
    if isSexSegregated:
        json_data['series'] = series
        json_data['seriesLegend'] = [{
            "name": "male",
            "colour": "red",
            "shape": "circle"
        },
        {
            "name": "female",
            "colour": "blue",
            "shape": "circle"
        },
        {
            "name": "other",
            "colour": "green",
            "shape": "circle"
        }]

    return json_data


def cleanDoB(dob):
    """
    Takes in a string of the date of birth and returns a string of the date of
    birth in the format of YYYY-MM-DD.
    """
    return dob.split("T")[0]

def cleanLifePeriod(dob, dod, averageLifeExpectancy):
    """
    Formats the life period, assuming an average life expectancy of 72 years 
    for those without a dod.
    """
    dobFormatted = dob.split("T")[0]
    yearOfBirth = int(dobFormatted.split("-")[0])
    
    if dod:
        dodFormatted = dod.split("T")[0]
    else:
        # For individuals still alive, display "Currently alive"
        dodFormatted = "Currently alive"
        # Additionally, for individuals born before 100 years ago without a DOD, 
        # calculate an assumed DOD
        if yearOfBirth < datetime.date.today().year - 100:
            dodAssumed = datetime.datetime.strptime(dobFormatted, "%Y-%m-%d")\
                    + datetime.timedelta(days=averageLifeExpectancy*365.25)
            # Use assumed DOD
            dodFormatted = "assumed death: " + dodAssumed.strftime("%Y-%m-%d")
        
    return f"{dobFormatted} - {dodFormatted}"