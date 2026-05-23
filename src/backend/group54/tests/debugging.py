import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)) + "/src")

import cacheMaintainance
import voronoiVisualisation.voronoiVisualisationFunctions as v
import sqlite3

def testQuery():
    cacheMaintainance.init()
    query = """
        SELECT * FROM satelliteEvent
    """
    conn = sqlite3.connect(cacheMaintainance.DATABASE_PATH)
    cur = conn.cursor()
    ret = cur.execute(query)
    res = ret.fetchall()
    print(*res, sep="\n")
    print(len(res))
    cur.close()
    conn.close()


def testWikidataTimer():
    import time

    import numpy
    import queries
    import wikidataQuerying

    times = []
    for i in range(10):
        # print(f"running query {i}")
        startime = time.time()
        wikidataQuerying.SPARQLquery(queries.universityQueryPeople())
        times.append(time.time() - startime)

    arr = numpy.array(times)
    print(f"mean: {round(numpy.average(arr),5)}, var: {round(numpy.var(arr),5)}")


def testSQLQueryTime():
    import sqlite3
    import time

    import cacheMaintainance
    import numpy

    cacheMaintainance.init()
    query = """
        SELECT *
        FROM attending
    """
    conn = sqlite3.connect(cacheMaintainance.DATABASE_PATH)
    cur = conn.cursor()

    times = []
    for i in range(100):
        # print(f"running query {i}")
        startime = time.time()
        ret = cur.execute(query)
        res = ret.fetchall()
        times.append(time.time() - startime)

    cur.close()
    conn.close()

    arr = numpy.array(times)
    print(f"mean: {round(numpy.average(arr),5)}, var: {round(numpy.var(arr),5)}")
  
def getPersonDetails(QNo):
    with sqlite3.connect(cacheMaintainance.DATABASE_PATH) as conn:
        cur = conn.cursor()
        ret = cur.execute(f"""SELECT name, dob, location, dod, sex_or_gender, image_url
                        FROM person 
                        WHERE qNo = {QNo};""")
        data = ret.fetchall()
    return data[0]

def getAwards(QNo):
    with sqlite3.connect(cacheMaintainance.DATABASE_PATH) as conn:
        cur = conn.cursor()
        ret = cur.execute(f"""SELECT award.name
            FROM award, received
            WHERE received.QNoPerson = {QNo} and award.QNo = received.QNoAward;""")
        data = ret.fetchall()
    return data

def getOrganisationNames(QNo):
    with sqlite3.connect(cacheMaintainance.DATABASE_PATH) as conn:
        cur = conn.cursor()
        ret = cur.execute(f"""SELECT society.name
            FROM society, membership
            WHERE membership.QNoPerson = {QNo} and society.QNo = membership.QNoGroup;""")
        data = ret.fetchall()
    return data

def getInstitutions(QNo, isEducation = True):
    conn = sqlite3.connect(cacheMaintainance.DATABASE_PATH)
    cur = conn.cursor()
    ret = cur.execute(f"""SELECT institution.name
        FROM institution, attending
        WHERE attending.QNoPerson = {QNo}
        AND attending.QNoInstitution = institution.QNo
        AND {'NOT' if not isEducation else ''} attending.isEducation;""")
    data = ret.fetchall()
    cur.close()
    conn.close()
    return [item[0] for item in data]

def generateHTMLBiography(QNo: int) -> str:
    name, dob, location, dod, sex_or_gender, image_url = getPersonDetails(QNo)
    educationNames = getInstitutions(QNo) # list of singles
    otherAffiliations = getInstitutions(QNo, False) # list of singles
    awardNames = getAwards(QNo)
    societies = getOrganisationNames(QNo)
    
    image = f'<img src = "{image_url}">' if image_url != None else ''
    deathNote = f"and died on {dod.split('T')[0]}" if dod else ''
    
    educationString = f"{', '.join(educationNames[:-1])}, and {educationNames[-1]}" \
        if len(educationNames) > 1 else educationNames[0] if len(educationNames) == 1 else ''
    
    employerString = f"{', '.join(otherAffiliations[:-1])}, and {otherAffiliations[-1]}" \
        if len(otherAffiliations) > 1 else otherAffiliations[0] if len(otherAffiliations) == 1 else ''
    
    pronoun = 'He' if sex_or_gender == 'male' else 'She' if sex_or_gender == 'female' else 'They'
    
    awardString = f"""received the following awards:
        <ul>{"".join([f'<li>{awardName[0]}</li>' for awardName in awardNames])}</ul>""" \
            if len(awardNames) > 0 else ''
    
    societyString = f"""{'and' if awardString != '' else ''} was a member of the following groups:
        <ul>{"".join([f'<li>{society[0]}</li>' for society in societies])}</ul>""" \
            if len(societies) > 0 else ''
    
    htmlContent = f"""
        <h1>{name}</h1>
        {image}
        <p>Born in {location} on {dob.split('T')[0]} {deathNote} 
        {f', {name}' if educationString != '' or employerString != '' else ''} 
        {f'studied at {educationString}' if educationString != '' else '.' }
        {'; and' if educationString != '' and employerString != '' else '.' if educationString != '' else ''} 
        {f'was employed by {employerString}.' if employerString != '' else ''}
        
        {pronoun if societyString != '' or awardString != '' else ''} {awardString} 
        {societyString}
        </p>
    """
    return htmlContent

def main():
    # print(cacheMaintainance.__toStructureGroup({'group':{'value':'Q3'}, 'groupLabel':{'value':'Joe and the Rats'}}))
    testQuery()
    # print(v.getVoronoiPart("1900-11-16T00:00:00Z,2000-11-16T00:00:00Z;7.3325,53.0533;10.0"))
    # print(generateHTMLBiography(724095))


if __name__ == "__main__":
    main()
