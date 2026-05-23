"""Module storing the DBConnector"""

from __future__ import annotations
from typing import Optional

from contextlib import AbstractContextManager
import os
import pymysql
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


FLASK_ENV = os.environ.get("FLASK_ENV", "development")


class Databases:
    """Enum to store the different databases (Legacy)"""

    DEV = os.environ.get("MYSQL_DATABASE")
    PROD = os.environ.get("MYSQL_DATABASE")


class DBConnection(AbstractContextManager):
    """An object representing a connection to the database which is used by the accessors"""

    __HOST = "localhost" if FLASK_ENV == "development" else os.environ.get("DB_HOST")
    __USER = os.environ.get("MYSQL_USER")
    __PSWD = os.environ.get("MYSQL_PASSWORD")
    __PORT = int(os.environ.get("DB_PORT", "3306"))

    database: Optional[Databases]

    def __init__(self, database: Optional[Databases] = None) -> None:
        """Intialise the connection object"""
        if self.__HOST is None:
            raise ValueError("Environment HOST variable not set")

        if self.__USER is None:
            raise ValueError("Environment USER variable not set")

        if self.__PSWD is None:
            raise ValueError("Environment PSWD variable not set")

        self.__conn = None

        self.connect_to_server()
        if database:
            self.connect_to_db(database)

    def __enter__(self) -> DBConnection:
        """Method called when context manager entered"""
        return super().__enter__()

    def __exit__(self, t, v, tb) -> None:
        """Method called when context manager exits"""
        if self.__conn is not None and self.__conn.open:
            self.__conn.close()
        else:
            raise ConnectionError("Connection not open.")

        return None

    def connect_to_server(self) -> None:
        """Connect to the mysql server"""
        self.__conn = pymysql.connect(
            host=self.__HOST,
            user=self.__USER,
            port=self.__PORT,
            password=str(self.__PSWD),
            local_infile=True,
        )

    # Note: pymysql cannot validate in db/table creation/deletion

    def connect_to_db(self, database) -> None:
        """Connect to a database in the server"""
        self.__conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        self.__conn.select_db(database)

    def get_databases(self) -> list:
        """List all databases"""
        cursor = self.__conn.cursor()
        cursor.execute("SHOW DATABASES")
        return [db for db in cursor]

    def get_tables(self) -> list:
        """List all tables in the database"""
        cursor = self.__conn.cursor()
        cursor.execute("SHOW TABLES")
        return [table for table in cursor]

    def describe_table(self, table: str) -> list:
        """Describe a table"""
        cursor = self.__conn.cursor()
        cursor.execute(f"DESCRIBE {table}")
        return [val for val in cursor]

    def drop_table(self, table: str) -> None:
        """Drop a table from the database"""
        self.__conn.cursor().execute(f"DROP TABLE IF EXISTS {table}")

    def create_table(self, table: str, schema_file: str) -> None:
        """Create a table in the database

        Args:
            table (str): the table name
            schema_file (str): path to file storing the schema for the table
        """
        if table == "":
            raise ValueError("Table name is required")
        if schema_file == "":
            raise ValueError("Schema file name is required")

        with open(schema_file, encoding="UTF-8") as f:
            schema = f.read()

        self.__conn.cursor().execute(
            f"CREATE TABLE IF NOT EXISTS {table} (\n{schema});"
        )

    def exec(self, statement, *values) -> list:
        """Execute a query on the connection"""
        cursor = self.__conn.cursor()
        cursor.execute(statement, args=values)
        results_list = cursor.fetchall()
        self.__conn.commit()

        return results_list
