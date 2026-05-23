from typing import Any, Union
from dotenv import load_dotenv, find_dotenv

from .db_connector import DBConnection

load_dotenv(find_dotenv())


class OrderDirection:
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class DBAccessor:
    """Generic base class to access the database"""

    __SQL_CMP_OPERATORS = ("=", "<", ">", "<=", ">=", "!=")

    def __init__(self, connection: DBConnection):
        """Initialise the class with a connection"""
        self.conn = connection

    def load_data(self, table: str, csv_file: str) -> None:
        """Load data into the db via the CSV

        Args:
            table (str): the table to load the data into
            csv_file (str): the path to the csv file to use
        """
        query = f"LOAD DATA LOCAL INFILE %s REPLACE INTO TABLE `{table}` FIELDS TERMINATED BY ';';"
        # query = f"""LOAD DATA LOCAL INFILE %s
        # REPLACE INTO TABLE `{table}`
        # FIELDS TERMINATED BY ';'
        # (STATION_ID,NAME,COUNTRY,LATITUDE,LONGITUDE,ELEVATION,@vCAN_ID)
        # SET CAN_ID = NULLIF(@vCAN_ID, '');"""
        self.conn.exec(query, csv_file)

    def insert(self, table: str, data: dict) -> None:
        """Legacy method allowing insertion to a table"""
        columns = "("
        for k in data.keys():
            if columns != "(":
                columns += ", "
            columns += f"`{k}`"
        columns += ")"

        query = f"INSERT INTO `{table}` {columns} VALUES %s;"
        self.conn.exec(query, tuple(data.values()))

    def select(
        self,
        table: str,
        *joint_conditions: tuple[str, Any, str],
        order: Union[tuple[str, OrderDirection], None] = None,
        query_args: list[str],
    ) -> list:
        """Legacy method allowing selection of data from table"""
        if not table:
            raise ValueError("Table name is required: given", table)

        # Initialize an SQL query string
        query = f"SELECT * FROM `{table}` "

        for i in range(len(joint_conditions)):
            if i == 0:
                query += "WHERE "

            (col, val, op) = joint_conditions[i]

            # Check comparison operator is valid ie =,<,>,<=,>=,!=
            if op not in self.__SQL_CMP_OPERATORS:
                raise ValueError(
                    "Comparison operator is not valid: must be one of ",
                    self.__SQL_CMP_OPERATORS,
                )

            # Add conditions to the query
            query += f"{col} {op} %s"
            query_args.append(val)

            # Add 'AND' if there are more conditions to come
            if i < len(joint_conditions) - 1:
                query += " AND "

        # Add sorting if specified
        if order:
            query += f" ORDER BY {order[0]} " + order[1]

        return self.conn.exec(query, *query_args)
