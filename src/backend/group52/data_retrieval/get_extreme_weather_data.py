"""Code to get extreme weather data from WikiData """

import sys
import json
from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT_URL = "https://query.wikidata.org/sparql"

QUERY_EXTREME_WEATHER = """
    #defaultView:Table
    SELECT ?item ?itemLabel ?geo ?country ?type ?startTime ?endTime
    WHERE
    {
    ?item wdt:P31/wdt:P279* wd:Q1277161;
            wdt:P31 ?type;
            wdt:P625 ?geo; # geo is not optional since we need it for the map
            OPTIONAL { ?item wdt:P17 ?country. }
            OPTIONAL { ?item wdt:P580 ?startTime. }
            OPTIONAL { ?item wdt:P582 ?endTime. }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
    }
    """
QUERY_NATURAL_DISASTERS = """
    #defaultView:Table
    SELECT ?item ?itemLabel ?geo ?country ?type ?startTime ?endTime
    WHERE
    {
    ?item wdt:P31/wdt:P279* wd:Q8065;
            wdt:P31 ?type;
            wdt:P625 ?geo; # geo is not optional since we need it for the map
            OPTIONAL { ?item wdt:P17 ?country. }
            OPTIONAL { ?item wdt:P580 ?startTime. }
            OPTIONAL { ?item wdt:P582 ?endTime. }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en".}
    }
    """


def get_results(query: str) -> object:
    """Get results from wikidata as a python object

    Args:
        query (str): the SPARQL query to be sent

    Returns:
        object: a python object representing the query results
    """
    # Create a new SPARQL client and set the query
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    sparql = SPARQLWrapper(ENDPOINT_URL, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()  # if json is invalid, this step will fail


def data_to_file(filename: str):
    """Get the query results and write to file

    Args:
        filename (str): the file to write to
        query (str): the SPARQL query to be sent
    """

    # get the results for the two queries
    results_extreme = get_results(QUERY_EXTREME_WEATHER)
    results_disasters = get_results(QUERY_NATURAL_DISASTERS)

    # combine the results
    results = (
        results_extreme["results"]["bindings"]
        + results_disasters["results"]["bindings"]
    )
    json_object = json.dumps(results, indent=4)

    # create the file if it doesn't exist
    with open(file=filename, mode="w", encoding="utf-8") as f:
        f.write(json_object)


# Run the code
if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("get_extreme_weather_data: requires 1 argument")

    data_to_file(sys.argv[1])
