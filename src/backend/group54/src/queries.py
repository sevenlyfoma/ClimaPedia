def universityQueryPeople(n: int = -1) -> str:
    query = f"""SELECT DISTINCT ?person ?personLabel ?loc ?locLabel
                ?coordPerson ?educatePred ?educationOrEmployment 
                ?educationOrEmploymentLabel ?coordUni ?borndate ?occLabel
                ?imageLabel ?deathDate ?sexLabel
    WHERE {{
    {{SELECT DISTINCT ?person ?personLabel ?educatePred 
         (SAMPLE (?sex) AS ?sex)
         (SAMPLE (?image) AS ?image)
         (SAMPLE (?loc) AS ?loc) 
         (SAMPLE (?coordPerson) AS ?coordPerson) 
         ?educationOrEmployment
         (SAMPLE (?coordUni) AS ?coordUni) 
         (SAMPLE (?borndate) AS ?borndate)
         (SAMPLE (?deathDate) AS ?deathDate)
         (SAMPLE (?occ) as ?occ)
    WHERE {{
        ?person wdt:P106 ?occ;
                ?locator ?loc;
                wdt:P569 ?borndate;
                ?educatePred ?educationOrEmployment.
        ?occ wdt:P279* wd:Q17276189.
        ?loc wdt:P625 ?coordPerson.
        ?educationOrEmployment wdt:P625 ?coordUni.
      
        OPTIONAL {{?person wdt:P18 ?image.}}
        OPTIONAL {{?person wdt:P570 ?deathDate.}}
        OPTIONAL {{?person wdt:P21 ?sex.}}
        OPTIONAL {{?sex wdt:label ?sexLabel.}}
    
        FILTER (?educatePred IN (wdt:P69, wdt:P108))
        FILTER (?locator IN (wdt:P19))
        FILTER (datatype(?borndate) = xsd:dateTime)
    }} GROUP BY ?person ?personLabel ?educationOrEmployment ?educatePred}}
    SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    {f'LIMIT {n}' if n > 0 else ""}"""
    return query

def awardsQueryPeople(n: int = -1) -> str:
    query = f"""SELECT DISTINCT ?person ?award ?awardLabel
        WHERE {{
            ?person wdt:P106 ?occ.
            ?occ wdt:P279* wd:Q17276189.
            ?person wdt:P166 ?award.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    {f'LIMIT {n}' if n > 0 else ""}"""
    return query

def membershipQueryPeople(n: int = -1) -> str:
    query = f"""SELECT DISTINCT ?person ?group ?groupLabel
        WHERE {{
            ?person wdt:P106 ?occ.
            ?occ wdt:P279* wd:Q17276189.
            ?person wdt:P463 ?group.
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    {f'LIMIT {n}' if n > 0 else ""}"""
    return query

def satellitesQuery(n: int = -1) -> str:
    query = f"""SELECT DISTINCT ?satellite ?satelliteLabel ?eventLabel 
            ?eventTime ?coords ?end ?imageLabel
        WHERE {{
            SELECT DISTINCT ?satellite ?satelliteLabel ?eventLabel ?eventTime
                ?imageLabel (SAMPLE (?coords) AS ?coords) 
                (BOUND (?isEnd) AS ?end) WHERE {{
            ?satellite wdt:P31 wd:Q209363.
            ?satellite wdt:P1427 ?startPoint.
            ?startPoint wdt:P625 ?coords.

            ?satellite p:P793 ?eventS.
            ?eventS ps:P793 ?event.
            ?eventS pq:P585 ?eventTime.
            OPTIONAL {{
                ?event wdt:P279 wd:Q12769393.
                BIND (true as ?isEnd)
            }}
            OPTIONAL {{?satellite wdt:P18 ?image.}}
            SERVICE wikibase:label 
                {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            }} GROUP BY ?satellite ?satelliteLabel ?eventLabel ?eventTime 
                ?isEnd ?imageLabel
        }}
    {f'LIMIT {n}' if n > 0 else ""}"""
    return query
