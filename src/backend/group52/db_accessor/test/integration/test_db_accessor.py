"""Tester for db_accessor"""

import csv
import pytest
import pymysql
from group52.db_accessor.db_connector import DBConnection, Databases
from group52.db_accessor.db_accessor import DBAccessor

# pylint: disable=no-member


def write_csv_file(csvFile, data):
    """Writes data into a CSV file.

    Args:
        csvFile: the CSV file to write into.
        data: the data to write into the CSV file.
    """
    with open(csvFile, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)


def test_insert_data():
    """Tests inserting data into a table by CSV file."""
    testCSV = "test.csv"
    # Setting up mock database data
    test_basic = {"insert_data": [(1,)], "queryCol": "COLUMN_NAME", "expected": ((1,),)}
    test_negative = {
        "insert_data": [(-1,)],
        "queryCol": "COLUMN_NAME",
        "expected": ((-1,),),
    }
    test_multiple_rows = {
        "insert_data": [(-1,), (1,), (42,)],
        "queryCol": "COLUMN_NAME",
        "expected": (
            (-1,),
            (1,),
            (42,),
        ),
    }
    tests = [test_basic, test_negative, test_multiple_rows]
    with DBConnection(Databases.DEV) as conn:
        for t in tests:
            write_csv_file(testCSV, t.get("insert_data"))
            conn.drop_table("test_table")
            conn.create_table(
                "test_table", "group52/db_accessor/test/integration/test_schema.txt"
            )

            accessor = DBAccessor(conn)
            queryCol = t.pop("queryCol")
            expected = t.pop("expected")
            accessor.load_data("test_table", testCSV)
            table_contents = conn.exec(f"SELECT {queryCol} FROM test_table;")
            assert table_contents == expected


def test_duplicate_insert():
    """Tests inserting duplicated data into a table by CSV file."""
    testCSV = "test.csv"

    # Put duplicated data into the csv
    data = [((1,),), ((1,),)]
    write_csv_file(testCSV, data)

    with DBConnection(Databases.DEV) as conn:
        conn.drop_table("test_table")
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )

        accessor = DBAccessor(conn)
        with pytest.raises(pymysql.err.DataError):
            accessor.load_data("test_table", testCSV)
        # table_contents = conn.exec(
        #     f"SELECT * FROM test_table;"
        # )
        # assert table_contents == ((1),)


def test_insert_empty_csv():
    """Tests inserting data into a table by an empty CSV file."""
    testCSV = "test.csv"
    # truncate
    f = open(testCSV, "w+")
    f.close()

    with DBConnection(Databases.DEV) as conn:
        conn.drop_table("test_table")
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )

        accessor = DBAccessor(conn)
        # The CSV function in pymysql does not throw an exception if there is a duplicate. It just ignores it.
        accessor.load_data("test_table", testCSV)
        table_contents = conn.exec("SELECT * FROM test_table;")
        assert table_contents == ()
