
import pandas as pd

from src.etl_framework.validate import (
    validate_customers,
    validate_orders
)


def test_validate_customers_valid_records():
    """Valid customer records should be accepted."""

    customers = pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Aman", "Riya"],
        "email": ["aman@gmail.com", "riya@gmail.com"],
        "city": ["Delhi", "Noida"],
        "registration_date": ["2026-01-10", "2026-02-15"],
        "source_file": ["customers.csv", "customers.csv"],
        "source_row_number": [2, 3]
    })

    valid, rejected = validate_customers(customers)

    assert len(valid) == 2
    assert len(rejected) == 0


def test_validate_customers_invalid_email():
    """Customer with invalid email should be rejected."""

    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["invalid-email"],
        "city": ["Delhi"],
        "registration_date": ["2026-01-10"],
        "source_file": ["customers.csv"],
        "source_row_number": [2]
    })

    valid, rejected = validate_customers(customers)

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "rejection_reason" in rejected.columns


def test_validate_customers_duplicate_ids():
    """All records with duplicate customer IDs should be rejected."""

    customers = pd.DataFrame({
        "customer_id": ["C001", "C001"],
        "customer_name": ["Aman", "Rahul"],
        "email": ["aman@gmail.com", "rahul@gmail.com"],
        "city": ["Delhi", "Noida"],
        "registration_date": ["2026-01-10", "2026-02-15"],
        "source_file": ["customers.csv", "customers.csv"],
        "source_row_number": [2, 3]
    })

    valid, rejected = validate_customers(customers)

    assert len(valid) == 0
    assert len(rejected) == 2


def test_validate_orders_valid_records():
    """Valid order records should be accepted."""

    orders = pd.DataFrame({
        "order_id": ["O001", "O002"],
        "customer_id": ["C001", "C002"],
        "order_date": ["2026-03-01", "2026-03-02"],
        "amount": ["500", "1200"],
        "status": ["Delivered", "Pending"],
        "source_file": ["orders.csv", "orders.csv"],
        "source_row_number": [2, 3]
    })

    valid_customer_ids = {"C001", "C002"}

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids
    )

    assert len(valid) == 2
    assert len(rejected) == 0


def test_validate_customers_missing_required_column():
    """Customers with a missing required column should raise an error."""

    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["aman@gmail.com"],
        "city": ["Delhi"],
        # registration_date is missing
        "source_file": ["customers.csv"],
        "source_row_number": [2]
    })

    try:
        validate_customers(customers)
        assert False, "Expected missing-column validation error"
    except ValueError as error:
        assert "registration_date" in str(error)


def test_validate_orders_negative_amount():
    """Orders with negative amounts should be rejected."""

    orders = pd.DataFrame({
        "order_id": ["O001"],
        "customer_id": ["C001"],
        "order_date": ["2026-03-01"],
        "amount": ["-500"],
        "status": ["Delivered"],
        "source_file": ["orders.csv"],
        "source_row_number": [2]
    })

    valid, rejected = validate_orders(orders, {"C001"})

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "rejection_reason" in rejected.columns


def test_validate_orders_invalid_status():
    """Orders with an unsupported status should be rejected."""

    orders = pd.DataFrame({
        "order_id": ["O001"],
        "customer_id": ["C001"],
        "order_date": ["2026-03-01"],
        "amount": ["500"],
        "status": ["UnknownStatus"],
        "source_file": ["orders.csv"],
        "source_row_number": [2]
    })

    valid, rejected = validate_orders(orders, {"C001"})

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "rejection_reason" in rejected.columns


def test_validate_customers_unexpected_extra_column():
    """Unexpected extra columns should not break validation."""

    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": ["aman@gmail.com"],
        "city": ["Delhi"],
        "registration_date": ["2026-01-10"],
        "source_file": ["customers.csv"],
        "source_row_number": [2],
        "unexpected_column": ["extra_value"]
    })

    valid, rejected = validate_customers(customers)

    assert len(valid) == 1
    assert len(rejected) == 0
    assert valid.iloc[0]["customer_id"] == "C001"
    assert valid.iloc[0]["unexpected_column"] == "extra_value"


def test_validate_orders_invalid_customer_reference():
    """Orders referencing non-existent customers should be rejected."""

    orders = pd.DataFrame({
        "order_id": ["O001"],
        "customer_id": ["C999"],
        "order_date": ["2026-03-01"],
        "amount": ["500"],
        "status": ["Delivered"],
        "source_file": ["orders.csv"],
        "source_row_number": [2]
    })

    valid_customer_ids = {"C001", "C002"}

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids
    )

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "rejection_reason" in rejected.columns


def test_validate_customers_null_required_email():
    """Customers with null email should be rejected."""

    customers = pd.DataFrame({
        "customer_id": ["C001"],
        "customer_name": ["Aman"],
        "email": [None],
        "city": ["Delhi"],
        "registration_date": ["2026-01-10"],
        "source_file": ["customers.csv"],
        "source_row_number": [2]
    })

    valid, rejected = validate_customers(customers)

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "rejection_reason" in rejected.columns
