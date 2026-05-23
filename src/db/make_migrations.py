#!/usr/bin/python3

"""Script to make migrations. Put migrations in the migrations directory."""

import os
import sys
import re
import importlib
import time

from argparse import ArgumentParser

import pymysql

MIGRATIONS_MODULE = "migrations"
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), MIGRATIONS_MODULE)
FILE_RE = r"^(\d+).*\.py$"
DEFAULT_MAX_ATTEMPTS = 1


def main(max_attempts: int) -> None:
    """Main method.

    Parameters:
        max_attempts: The maximum number of attempts to make.
    """
    attempts = 0
    conn = None
    while conn is None and attempts < max_attempts:
        try:
            conn = pymysql.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),  # type: ignore
                database=os.getenv("MYSQL_DATABASE"),
                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS,
            )  # type: ignore
        except KeyError as e:
            print("Missing environment variables")
            print(e)
            sys.exit(1)
        except pymysql.err.OperationalError:
            time.sleep(2)
            attempts += 1

    if conn is None:
        print("Could not connect to database.")
        sys.exit(1)

    cur = conn.cursor()

    try:
        cur.execute("SELECT `version` FROM `version` LIMIT 1")
        res = cur.fetchone()
        if res is None:
            raise pymysql.err.ProgrammingError()
        version = res[0]
    except pymysql.err.ProgrammingError:
        # The table version doesn't exist.
        version = -1

    print(f"Current version = {version}", flush=True)

    conn.begin()
    try:
        max_fv = version
        for fname in sorted(os.listdir(MIGRATIONS_DIR)):
            if (m := re.match(FILE_RE, fname)) is not None:
                f_v = int(m.group(1))
                if f_v > version:
                    max_fv = f_v
                    print(f"Executing migration {fname}", flush=True)

                    mig = importlib.import_module(
                        f"{MIGRATIONS_MODULE}.{os.path.splitext(fname)[0]}"
                    )
                    try:
                        mig.make_migration(conn, cur)
                    except AttributeError as e:
                        print(
                            f"{fname}: Malformed migration. Missing make_migration() method.",
                            flush=True,
                        )
                        raise e

        # Update the version.
        if max_fv > version:
            if version == -1:
                cur.execute("INSERT INTO `version`(`version`) VALUES(%s)", (max_fv,))
            else:
                cur.execute(
                    "UPDATE `version` SET `version`=%s WHERE `version`=%s",
                    (max_fv, version),
                )
            print(f"Migrations made. New version = {max_fv}", flush=True)
        else:
            print("Database up to date.", flush=True)

        conn.commit()
    except Exception as e:
        print("Error making migrations: rolling back.")
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-a",
        "--attempts",
        type=int,
        default=DEFAULT_MAX_ATTEMPTS,
        help=f"Max number of attempts to connect to the database. (Default {DEFAULT_MAX_ATTEMPTS})",
    )

    args = parser.parse_args()
    main(args.attempts)
