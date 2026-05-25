"""Code to get weather station data from WikiData
"""

import sys
import json
import os
from pathlib import Path
import requests
from SPARQLWrapper import SPARQLWrapper, JSON


ENDPOINT_URL = "https://query.wikidata.org/sparql"


def get_results(query: str) -> object:
    """Get results from wikidata as a python object

    Args:
        query (str): the SPARQL query to be sent

    Returns:
        object: a python object representing the query results
    """
    # user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    user_agent = "Group52WeatherApp/1.0 (https://github.com/sevenlyfoma/ClimaPedia; 7lyfoma@gmail.com) Python/3.11"
    sparql = SPARQLWrapper(ENDPOINT_URL, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()  # if json is invalid, this step will fail


def get_weather_history(results: object):
    """Get weather history for all the entries in results

    Args:
        results (object): The results of the SPARQL query
                          containing a column of links to weather history tables
    """
    headers = set()
    i = 0
    for result in results:
        i += 1
        print(i, end=". ")
        print(result["weather_history"]["value"])
        try:
            r = requests.get(result["weather_history"]["value"], timeout=10)
            table = r.json()

            type_str = "M" if "Month" in result["weather_history"]["value"] else "A"

            result["weather_history"] = table  # to write to file
            json_object = json.dumps(result, indent=4)

            # # Added by max
            # # old writing didnt work so i added this version
            # # example data is hard coded which is a problem
            if not os.path.exists("example_data"):
                os.makedirs("example_data")

            filename = (
                "example_data"
                + result["item"]["value"][
                    result["item"]["value"].rfind("/") :  # noqa: E203
                ]
                + type_str
                + ".json"
            )
            print(filename)

            with open(filename, "w+", encoding="utf-8") as outfile:
                outfile.write(json_object)

            # #Ends here

            # with open(f"../weather_tables/\
            #           {result['item']['value'][result['item']['value'].rfind('/'):]}\
            #           {type_str}.json", "w+", encoding="utf-8") as outfile:
            #     outfile.write(json_object)

            for field in table["schema"]["fields"]:
                headers.add(field["name"])

        except requests.exceptions.Timeout as e:
            print("Request for weather history timed out")
            raise SystemExit(e) from e
        except requests.exceptions.RequestException as e:
            # catchall for any other exceptions in getting the data
            print("Problem getting weather history...")
            raise SystemExit(e) from e
        except ValueError as e:
            print("Incorrect JSON syntax for weather history")
            raise SystemExit(e) from e

    print(headers)


def get_data(filename: str, get_hist: bool):
    """Get the query results and write to file

    Args:
        filename (str): the file to write to
        get_hist (bool): whether the history for each station should be fetched
    """
    query = """
    # Every weather station in Wikidata
    #defaultView:Table
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

    if get_hist:
        get_weather_history(results["results"]["bindings"])


def get_data_with_limit(filename: str, get_hist: bool, limit: int):
    """Get the query results and write to file
       Only gets a specified number of stations
       Added by mv54

    Args:
        filename (str): the file to write to
        get_hist (bool): whether the history for each station should be fetched

    """

    # Added by mv54
    # Query limited to 2 to get just sample data
    query = """
    # Every weather station in Wikidata
    #defaultView:Table
    SELECT ?item ?itemLabel ?country ?countryLabel ?code ?coord ?altitude ?weather_history WHERE {
    ?item (wdt:P31/(wdt:P279*)) wd:Q190107;
                                wdt:P4150 ?weather_history.
    ?item wdt:P2044 ?altitude.
    ?item wdt:P17 ?country.
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    OPTIONAL { ?country wdt:P298 ?code. }
    OPTIONAL { ?item wdt:P625 ?coord. }
    }
    LIMIT
    """

    query = query + str(limit)

    # End

    results = get_results(query)

    json_object = json.dumps(results["results"]["bindings"], indent=4)

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open(mode="w", encoding="utf-8") as f:
        f.write(json_object)

    if get_hist:
        get_weather_history(results["results"]["bindings"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Invalid arguments, please specify filename")
    user_filename = sys.argv[1]
    get_histories = len(sys.argv) == 3 and sys.argv[2] == "--history"
    get_data(user_filename, get_histories)
