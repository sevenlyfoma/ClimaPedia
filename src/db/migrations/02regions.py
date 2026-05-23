"""Add the ca_station_map table for regions of CA weather stations."""

import sys

from SPARQLWrapper import SPARQLWrapper, JSON

SCHEMA = """
DROP TABLE IF EXISTS ca_station_map;
CREATE TABLE ca_station_map(
    station_id CHAR(7) PRIMARY KEY,
    province CHAR(2) NOT NULL
);
"""


def make_migration(conn, cur):
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/sparql",
        f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}",
    )
    sparql.setReturnFormat(JSON)

    sparql.setQuery(
        """
        SELECT ?regionName ?stationId WHERE {
        ?item (wdt:P31/(wdt:P279)) wd:Q190107 ;
                wdt:P17 wd:Q16 ;
                wdt:P131 ?region.

        ?region wdt:P300 ?regionName.
        ?item wdt:P6242 ?stationId.
        }
        """
    )

    res = sparql.queryAndConvert()

    data = [
        (e["stationId"]["value"], e["regionName"]["value"][-2:])
        for e in res["results"]["bindings"]
    ]

    cur.execute(SCHEMA)
    cur.executemany("INSERT INTO ca_station_map VALUES(%s, %s)", data)


if __name__ == "__main__":
    make_migration(None, None)
