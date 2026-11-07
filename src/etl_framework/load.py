
import sqlite3
import re
from pathlib import Path

import pandas as pd


def load_data(
    data,
    table_name,
    database_path="data/processed/etl_database.db"
):
    """
    Incrementally load records into SQLite.

    New primary keys are inserted.
    Existing primary keys are updated.
    Unchanged records remain unchanged.
    """

    primary_keys = {
        "customers": "customer_id",
        "orders": "order_id"
    }

    if table_name not in primary_keys:
        raise ValueError(f"Unsupported table: {table_name}")

    if not isinstance(data, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame")

    if data.empty:
        print(f"No records to load into {table_name}")
        return 0

    primary_key = primary_keys[table_name]

    if primary_key not in data.columns:
        raise ValueError(f"Missing primary key: {primary_key}")

    if data[primary_key].isna().any():
        raise ValueError("Primary key cannot contain null values")

    if data[primary_key].duplicated().any():
        raise ValueError("Duplicate primary keys found before loading")

    # Validate SQL identifiers
    for column in data.columns:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", column):
            raise ValueError(f"Invalid column name: {column}")

    Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(database_path) as connection:

        columns = list(data.columns)

        # Check whether an existing table has a primary key
        existing_info = connection.execute(
            f'PRAGMA table_info("{table_name}")'
        ).fetchall()

        if existing_info:
            has_primary_key = any(
                column_info[5] == 1
                and column_info[1] == primary_key
                for column_info in existing_info
            )

            if not has_primary_key:
                print(
                    f"Migrating old {table_name} table: "
                    "adding primary key constraint"
                )
                connection.execute(
                    f'DROP TABLE "{table_name}"'
                )

        # Create table if it does not already exist
        column_definitions = []

        for column in columns:
            if column == primary_key:
                sql_type = "TEXT PRIMARY KEY"
            elif pd.api.types.is_integer_dtype(data[column]):
                sql_type = "INTEGER"
            elif pd.api.types.is_numeric_dtype(data[column]):
                sql_type = "REAL"
            else:
                sql_type = "TEXT"

            column_definitions.append(
                f'"{column}" {sql_type}'
            )

        create_sql = (
            f'CREATE TABLE IF NOT EXISTS "{table_name}" '
            f'({", ".join(column_definitions)})'
        )

        connection.execute(create_sql)

        # Prepare UPSERT statement
        placeholders = ", ".join(["?"] * len(columns))
        column_names = ", ".join(f'"{col}"' for col in columns)

        update_columns = [
            col for col in columns if col != primary_key
        ]

        if update_columns:
            update_clause = ", ".join(
                f'"{col}" = excluded."{col}"'
                for col in update_columns
            )

            conflict_action = (
                f"DO UPDATE SET {update_clause}"
            )
        else:
            conflict_action = "DO NOTHING"

        insert_sql = (
            f'INSERT INTO "{table_name}" ({column_names}) '
            f'VALUES ({placeholders}) '
            f'ON CONFLICT("{primary_key}") {conflict_action}'
        )

        # Convert pandas missing values into SQLite NULL
        records = []

        for row in data.itertuples(index=False, name=None):
            clean_row = tuple(
                None if pd.isna(value) else value
                for value in row
            )
            records.append(clean_row)

        connection.executemany(insert_sql, records)

    print(
        f"Successfully upserted {len(data)} records "
        f"into {table_name}"
    )

    return len(data)
