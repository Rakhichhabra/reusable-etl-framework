
import pandas as pd
import pytest
import sqlite3

from src.etl_framework.load import load_data


def test_load_customers(tmp_path):
    """Customer records should be inserted into SQLite."""

    database_path = tmp_path / "test.db"

    customers = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Aman", "Riya"],
        "email": ["aman@gmail.com", "riya@gmail.com"]
    })

    loaded_count = load_data(
        customers,
        "customers",
        database_path=str(database_path)
    )

    assert loaded_count == 2

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]
    connection.close()

    assert count == 2


def test_load_updates_existing_record(tmp_path):
    """Existing records should be updated using UPSERT."""

    database_path = tmp_path / "test.db"

    first_data = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["old@gmail.com"]
    })

    updated_data = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["new@gmail.com"]
    })

    load_data(
        first_data,
        "customers",
        database_path=str(database_path)
    )

    load_data(
        updated_data,
        "customers",
        database_path=str(database_path)
    )

    connection = sqlite3.connect(database_path)
    result = connection.execute(
        "SELECT email FROM customers WHERE customer_id = ?",
        ("C001",)
    ).fetchone()
    connection.close()

    assert result[0] == "new@gmail.com"


def test_load_is_idempotent(tmp_path):
    """Loading the same records twice should not create duplicates."""

    database_path = tmp_path / "test.db"

    customers = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Aman", "Riya"],
        "email": ["aman@gmail.com", "riya@gmail.com"]
    })

    load_data(
        customers,
        "customers",
        database_path=str(database_path)
    )

    load_data(
        customers,
        "customers",
        database_path=str(database_path)
    )

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]
    connection.close()

    assert count == 2


def test_load_rejects_duplicate_primary_keys(tmp_path):
    """Duplicate primary keys in one input batch should raise an error."""

    database_path = tmp_path / "test.db"

    customers = pd.DataFrame({
        "customer_id": ["C001", "C001"],
        "customer_name": ["Aman", "Rahul"],
        "email": ["aman@gmail.com", "rahul@gmail.com"]
    })

    with pytest.raises(ValueError):
        load_data(
            customers,
            "customers",
            database_path=str(database_path)
        )

def test_load_empty_dataframe(tmp_path):
    """Empty input should be handled without loading records."""

    database_path = tmp_path / "test.db"

    customers = pd.DataFrame(columns=[
        "customer_id",
        "customer_name",
        "email"
    ])

    loaded_count = load_data(
        customers,
        "customers",
        database_path=str(database_path)
    )

    assert loaded_count == 0
    assert not database_path.exists()

