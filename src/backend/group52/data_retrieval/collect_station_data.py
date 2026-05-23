"""Code to get weather station data from WikiData, but not the histories
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON

# pylint: disable=duplicate-code, consider-using-with, too-many-locals


ENDPOINT_URL = "https://query.wikidata.org/sparql"


def get_results(query: str) -> object:
    """Get results from wikidata as a python object

    Args:
        query (str): the SPARQL query to be sent

    Returns:
        object: a python object representing the query results
    """
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    sparql = SPARQLWrapper(ENDPOINT_URL, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()  # if json is invalid, this step will fail


def collect_station_data(filename: str, last_accessed_filepath: str):
    """Get the query results and write to file

    Args:
        filename (str): the file to write to
        last_accessed_filepath: the file with the date wikidata was last queried
    """
    # Time to store for the next query
    time_of_query = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Get last accessed time
    time_f = open(last_accessed_filepath, mode="r", encoding="utf-8")
    time_of_prev_query = time_f.readline()
    time_f.close()
    # Set to first time possible if file is empty
    if time_of_prev_query == "":
        time_of_prev_query = "1970-01-01T00:00:00Z"

    if time_of_prev_query[-1] == "\n":
        time_of_prev_query = time_of_prev_query[
            0 : len(time_of_prev_query) - 1  # noqa: E203
        ]

    time_of_prev_query = '"' + time_of_prev_query + '"'

    query = (
        (
            """
    # Every weather station in Wikidata
    #defaultView:Table
    SELECT ?item ?itemLabel ?country ?countryLabel ?code ?coord ?altitude ?weather_history ?station_id WHERE {
    ?item (wdt:P31/(wdt:P279*)) wd:Q190107;
                                schema:dateModified ?item_modified.

    ?item wdt:P2044 ?altitude.
    ?item wdt:P17 ?country.
    BIND(?item_modified as ?date) FILTER (?date >=%s^^xsd:dateTime)
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    OPTIONAL { ?country wdt:P298 ?code. }
    OPTIONAL { ?item wdt:P625 ?coord. }
    OPTIONAL { ?item wdt:P6242 ?station_id. }
    }
    """
        )
        % time_of_prev_query.strip()
    )
    results = get_results(query)

    json_object = json.dumps(results["results"]["bindings"], indent=4)

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open(mode="w", encoding="utf-8") as f:
        f.write(json_object)

    # Save new accessed time
    time_f = open(last_accessed_filepath, mode="w", encoding="utf-8")
    time_f.write(time_of_query)
    time_f.close()


def collect_station_data_with_history(filename: str):
    """Get the query results and write to file. Gets only stations that have a history

    Args:
        filename (str): the file to write to
        last_accessed_filepath: the file with the date wikidata was last queried
    """
    query = """
    SELECT ?item ?itemLabel ?country ?countryLabel ?code ?coord ?altitude ?weather_history WHERE {
        ?item (wdt:P31/(wdt:P279*)) wd:Q190107;
                                    wdt:P4150 ?weather_history.

        ?item wdt:P2044 ?altitude.
        ?item wdt:P17 ?country.
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        OPTIONAL { ?country wdt:P298 ?code. }
        OPTIONAL { ?item wdt:P625 ?coord. }

    }
    """

    results = get_results(query)

    json_object = json.dumps(results["results"]["bindings"], indent=4)

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open(mode="w", encoding="utf-8") as f:
        f.write(json_object)


def collect_station_data_with_limit(filename: str, limit: int):
    """Get the query results and write to file
       Only gets a specified number of stations

    Args:
        filename (str): the file to write to
        limit (int): number of lines to be fecthed

    """
    query = """
    # Every weather station in Wikidata
    #defaultView:Table
    SELECT ?item ?itemLabel ?country ?item_modified ?history_modified ?countryLabel ?code ?coord ?altitude ?weather_history WHERE {
    ?item (wdt:P31/(wdt:P279*)) wd:Q190107;
                                wdt:P4150 ?weather_history;
                                schema:dateModified ?item_modified.


    ?item wdt:P2044 ?altitude.
    ?item wdt:P17 ?country.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    OPTIONAL { ?country wdt:P298 ?code. }
    OPTIONAL { ?item wdt:P625 ?coord. }
    }
    LIMIT
    """

    query = query + str(limit)

    results = get_results(query)

    json_object = json.dumps(results["results"]["bindings"], indent=4)

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open(mode="w", encoding="utf-8") as f:
        f.write(json_object)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Invalid arguments, please specify filename")
    user_filename = sys.argv[1]
    # collect_station_data_with_limit(user_filename, 5)
    collect_station_data(user_filename, sys.argv[2])
