"""
Code which drops the current tables and recreates them with the schemas
"""

# pylint: disable=duplicate-code, no-member

import sys
from group52.db_accessor.db_connector import DBConnection, Databases
from group52.db_accessor.group52 import (
    Tables,
    STATIONS_SCHEMA,
    HISTORY_SCHEMA,
    EVENTS_SCHEMA,
    TYPES_SCHEMA,
    COUNTRIES_SCHEMA,
    EVENT_TYPES_SCHEMA,
    EVENT_COUNTRIES_SCHEMA,
    ReportAccessor,
)


def drop_and_create_tables(database_to_use: Databases):
    """Drops and recreates the stations and history table

    Args:
        database_to_use (Database): the databse (either dev or prod) to upload the data to

    """

    # Open connection and drop and recreate databases
    print("Settinng up DB and stations table...", end="")
    sys.stdout.flush()
    with DBConnection(database_to_use) as conn:
        # Have to drop the table to remove foreign key problems
        conn.drop_table(Tables.HISTORY)
        conn.drop_table(Tables.STATIONS)

        conn.drop_table(Tables.EVENT_COUNTRIES)
        conn.drop_table(Tables.EVENT_TYPES)
        conn.drop_table(Tables.COUNTRIES)
        conn.drop_table(Tables.TYPES)
        conn.drop_table(Tables.EVENTS)

        conn.create_table(Tables.STATIONS, STATIONS_SCHEMA)
        conn.create_table(Tables.HISTORY, HISTORY_SCHEMA)

        conn.create_table(Tables.EVENTS, EVENTS_SCHEMA)
        conn.create_table(Tables.TYPES, TYPES_SCHEMA)
        conn.create_table(Tables.COUNTRIES, COUNTRIES_SCHEMA)
        conn.create_table(Tables.EVENT_TYPES, EVENT_TYPES_SCHEMA)
        conn.create_table(Tables.EVENT_COUNTRIES, EVENT_COUNTRIES_SCHEMA)

        accessor = ReportAccessor(conn)
        accessor.create_index_on_date()

        print("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("drop_and_create_tables: requires 1 positional argument")

    if sys.argv[1] != "DEV" and sys.argv[1] != "PROD":
        raise SystemExit(
            "drop_and_create_tables: database must either be 'DEV' or 'PROD'"
        )

    print("drop_and_create_tables will use '" + sys.argv[1] + "' as the db")

    if sys.argv[1] == "DEV":
        drop_and_create_tables(Databases.DEV)
    if sys.argv[1] == "PROD":
        drop_and_create_tables(Databases.PROD)
