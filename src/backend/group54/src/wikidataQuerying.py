# import numpy as np
# import pandas as pd
import json
from logging import DEBUG, INFO
from typing import Tuple

import queries
import requests
from auxiliaryFunctions import createLogger, maybeLog


def infoQNo(QNo: str) -> dict:
    """retrieves information about the object with Q number Qno.

    Args:
        QNo (str): Q number of object to retrieve data about.

    Returns:
        dict: JSON representation of result.
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbgetentities", 
        "format": "json", 
        "ids": QNo, 
        "language": "en"
    }
    return requests.get(url, params=params).json()


def SPARQLquery(query: str) -> dict:
    """function for running SPARQL query on wikidata endpoint.
    see https://www.wikidata.org/wiki/Wikidata:Lists/SPARQL_endpoints for
    endpoint information.

    Args:
        query (str): SPARQl query to run.

    Returns:
        dict: JSON representation of result of query.
    """
    url = 'https://query.wikidata.org/sparql'
    params = {
        'format': 'json',
        'query': query,
        'language': 'en'
    }
    return requests.get(url, params = params).json()