"""Module to test db_connector"""

from group52.db_accessor.db_connector import DBConnection, Databases

# pylint: disable=no-member


def test_can_connect():
    """Test connect works"""
    with DBConnection() as conn:
        print(conn, conn._DBConnection__conn)
        assert conn._DBConnection__conn.open


def test_can_disconnect():
    """Test disconnect works"""
    with DBConnection() as conn:
        pass
    assert not conn._DBConnection__conn.open


def test_show_db_exists_not_connected():
    """Test weather db exists using a connection which is not connected to db"""
    with DBConnection() as conn:
        assert ("weather",) in conn.get_databases()


def test_get_tables_works():
    """Test that we can find which tables are in the db"""
    with DBConnection(Databases.DEV) as conn:
        assert ("station",) in conn.get_tables()


def test_describe_table_works():
    """Test tables can be described"""
    with DBConnection(Databases.DEV) as conn:
        assert ("station_id", "char(20)", "NO", "PRI", None, "") in conn.describe_table(
            "station"
        )


def test_create_table_works():
    """Test table can be created using a schema"""
    with DBConnection(Databases.DEV) as conn:
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )
        assert ("test_table",) in conn.get_tables()


def test_create_duplicate_table_works():
    """Test table creation can handle duplicate creation"""
    with DBConnection(Databases.DEV) as conn:
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )
        assert ("test_table",) in conn.get_tables()


def test_drop_table_works():
    """Test table can be dropped via the connector"""
    with DBConnection(Databases.DEV) as conn:
        conn.drop_table("test_table")
        assert ("test_table",) not in conn.get_tables()


def test_exec_can_execute_query():
    """Test connection can execute an arbitrary query"""
    with DBConnection(Databases.DEV) as conn:
        conn.create_table(
            "test_table", "group52/db_accessor/test/integration/test_schema.txt"
        )
        conn.exec("INSERT INTO test_table(COLUMN_NAME) VALUES (1), (42);")
        assert (42,) in conn.exec("SELECT * FROM test_table;")
