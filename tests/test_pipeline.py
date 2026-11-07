
import logging
import sqlite3
import json
import pytest
import pandas as pd

import src.etl_framework.pipeline as pipeline


def test_run_pipeline_end_to_end(tmp_path, monkeypatch):
    """
    Test the complete ETL pipeline using temporary files
    and a temporary SQLite database.
    """

    # STEP 1: Create temporary input CSV files
    customers_file = tmp_path / "customers.csv"
    orders_file = tmp_path / "orders.csv"

    customers = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Aman", "Riya"],
        "email": ["aman@gmail.com", "invalid-email"],
        "city": ["Delhi", "Noida"],
        "registration_date": ["2026-01-10", "2026-02-15"]
    })

    orders = pd.DataFrame({
        "order_id": ["O001", "O002"],
        "customer_id": ["C001", "C999"],
        "order_date": ["2026-03-01", "2026-03-02"],
        "amount": ["500", "700"],
        "status": ["Delivered", "Pending"]
    })

    customers.to_csv(customers_file, index=False)
    orders.to_csv(orders_file, index=False)

    # STEP 2: Create temporary database and rejected folder
    database_path = tmp_path / "etl_database.db"
    rejected_dir = tmp_path / "rejected"

    # STEP 3: Replace original pipeline paths with temporary paths
    monkeypatch.setattr(
        pipeline, "CUSTOMERS_FILE", customers_file
    )
    monkeypatch.setattr(
        pipeline, "ORDERS_FILE", orders_file
    )
    monkeypatch.setattr(
        pipeline, "DATABASE_PATH", database_path
    )
    monkeypatch.setattr(
        pipeline, "REJECTED_DATA_DIR", rejected_dir
    )

    # STEP 4: Use a test logger instead of the project logger
    test_logger = logging.Logger("test_pipeline")
    monkeypatch.setattr(
        pipeline, "setup_logger", lambda log_file=None: test_logger
    )

    # STEP 5: Execute the complete ETL pipeline
    summary = pipeline.run_pipeline()

    # STEP 6: Verify pipeline execution status
    assert summary["status"] == "SUCCESS"

    # STEP 7: Verify database records
    connection = sqlite3.connect(database_path)

    customer_count = connection.execute(
        "SELECT COUNT(*) FROM customers"
    ).fetchone()[0]

    order_count = connection.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    rejected_count = connection.execute(
        "SELECT COUNT(*) FROM rejected_records"
    ).fetchone()[0]

    connection.close()

    assert customer_count == 1
    assert order_count == 1
    assert rejected_count == 2

    # STEP 8: Verify rejected CSV files
    assert (rejected_dir / "rejected_customers.csv").exists()
    assert (rejected_dir / "rejected_orders.csv").exists()

    # STEP 9: Verify metrics contain both datasets
    assert "customers" in summary["datasets"]
    assert "orders" in summary["datasets"]

    
def test_run_pipeline_empty_batch(tmp_path, monkeypatch):
    """Verify that the pipeline handles empty CSV batches."""

    # Create CSV files with headers but no records
    customers_file = tmp_path / "customers.csv"
    orders_file = tmp_path / "orders.csv"

    customers_file.write_text(
        "customer_id,customer_name,email,city,registration_date\n",
        encoding="utf-8"
    )

    orders_file.write_text(
        "order_id,customer_id,order_date,amount,status\n",
        encoding="utf-8"
    )

    # Create temporary paths
    database_path = tmp_path / "etl_database.db"
    rejected_dir = tmp_path / "rejected"
    report_dir = tmp_path / "reports"

    # Replace pipeline paths
    monkeypatch.setattr(pipeline, "CUSTOMERS_FILE", customers_file)
    monkeypatch.setattr(pipeline, "ORDERS_FILE", orders_file)
    monkeypatch.setattr(pipeline, "DATABASE_PATH", database_path)
    monkeypatch.setattr(pipeline, "REJECTED_DATA_DIR", rejected_dir)
    monkeypatch.setattr(pipeline, "REPORT_DIR", report_dir)

    # Use a test logger
    test_logger = logging.Logger("test_empty_pipeline")
    monkeypatch.setattr(
        pipeline, "setup_logger", lambda log_file=None: test_logger
    )

    # Execute pipeline
    summary = pipeline.run_pipeline()

    # Verify successful execution
    assert summary["status"] == "SUCCESS"

    # Verify zero records for both datasets
    for dataset in ["customers", "orders"]:
        assert summary["datasets"][dataset]["input_records"] == 0
        assert summary["datasets"][dataset]["valid_records"] == 0
        assert summary["datasets"][dataset]["rejected_records"] == 0
        assert summary["datasets"][dataset]["loaded_records"] == 0

    # Verify that no database records were created
    # for the empty batch
    if database_path.exists():
        with sqlite3.connect(database_path) as connection:
            tables = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                """
            ).fetchall()

        assert tables == []
    else:
        assert not database_path.exists()


def test_pipeline_partial_failure_and_retry(tmp_path, monkeypatch):
    """Pipeline should recover safely after a partial load failure."""

    # Create input CSV files
    customers_file = tmp_path / "customers.csv"
    orders_file = tmp_path / "orders.csv"

    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["aman@gmail.com"],
        "city": ["Delhi"],
        "registration_date": ["2026-01-10"]
    })

    orders = pd.DataFrame({
        "order_id": ["O001"],
        "customer_id": ["C001"],
        "order_date": ["2026-03-01"],
        "amount": ["500"],
        "status": ["Delivered"]
    })

    customers.to_csv(customers_file, index=False)
    orders.to_csv(orders_file, index=False)

    # Temporary paths
    database_path = tmp_path / "etl_database.db"
    rejected_dir = tmp_path / "rejected"
    report_dir = tmp_path / "reports"

    monkeypatch.setattr(pipeline, "CUSTOMERS_FILE", customers_file)
    monkeypatch.setattr(pipeline, "ORDERS_FILE", orders_file)
    monkeypatch.setattr(pipeline, "DATABASE_PATH", database_path)
    monkeypatch.setattr(pipeline, "REJECTED_DATA_DIR", rejected_dir)
    monkeypatch.setattr(pipeline, "REPORT_DIR", report_dir)

    # Use a test logger
    test_logger = logging.Logger("test_retry_pipeline")
    monkeypatch.setattr(
        pipeline, "setup_logger", lambda log_file=None: test_logger
    )

    # Keep the original load function
    original_load_data = pipeline.load_data

    # Simulate failure only once while loading orders
    failure_state = {"should_fail": True}

    def load_with_temporary_failure(
        data, table_name, database_path="data/processed/etl_database.db"
    ):
        if table_name == "orders" and failure_state["should_fail"]:
            failure_state["should_fail"] = False
            raise RuntimeError("Simulated orders load failure")

        return original_load_data(
            data,
            table_name,
            database_path=database_path
        )

    monkeypatch.setattr(
        pipeline, "load_data", load_with_temporary_failure
    )

    # First execution should fail
    with pytest.raises(RuntimeError, match="Simulated orders load failure"):
        pipeline.run_pipeline()

    # Verify failure report
    failure_report = report_dir / "pipeline_summary.json"
    assert failure_report.exists()

    with open(failure_report, encoding="utf-8") as file:
        failed_summary = json.load(file)

    assert failed_summary["status"] == "FAILED"
    assert "Simulated orders load failure" in failed_summary["failure_reason"]

    # Second execution should succeed
    retry_summary = pipeline.run_pipeline()

    assert retry_summary["status"] == "SUCCESS"

    # Verify final database records
    with sqlite3.connect(database_path) as connection:
        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        order_count = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

    # Customers should not be duplicated after retry
    assert customer_count == 1
    assert order_count == 1
