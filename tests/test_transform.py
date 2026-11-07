
import pandas as pd

from src.etl_framework.transform import (
    transform_customers,
    transform_orders
)


def test_transform_customers():
    """Customer data should be cleaned and standardized."""

    customers = pd.DataFrame({
        "customer_id": [" C001 "],
        "customer_name": [" Aman "],
        "email": [" AMAN@GMAIL.COM "],
        "city": [" Delhi "],
        "registration_date": ["2026-01-10"],
        "source_file": ["customers.csv"],
        "source_row_number": [2]
    })

    result = transform_customers(customers)

    assert result.iloc[0]["customer_id"] == "C001"
    assert result.iloc[0]["customer_name"] == "Aman"
    assert result.iloc[0]["email"] == "aman@gmail.com"
    assert result.iloc[0]["city"] == "Delhi"
    assert "rejection_reason" not in result.columns


def test_transform_customers_empty_dataframe():
    """Empty customer data should be handled."""

    customers = pd.DataFrame(columns=[
        "customer_id",
        "customer_name",
        "email",
        "city",
        "registration_date",
        "source_file",
        "source_row_number"
    ])

    result = transform_customers(customers)

    assert result.empty


def test_transform_orders():
    """Order data should be cleaned and standardized."""

    orders = pd.DataFrame({
        "order_id": [" O001 "],
        "customer_id": [" C001 "],
        "order_date": ["2026-03-15"],
        "amount": ["500.567"],
        "status": [" delivered "],
        "source_file": ["orders.csv"],
        "source_row_number": [2]
    })

    result = transform_orders(orders)

    assert result.iloc[0]["order_id"] == "O001"
    assert result.iloc[0]["customer_id"] == "C001"
    assert result.iloc[0]["amount"] == 500.57
    assert result.iloc[0]["status"] == "Delivered"
    assert result.iloc[0]["order_year"] == 2026
    assert result.iloc[0]["order_month"] == 3
    assert "rejection_reason" not in result.columns


def test_transform_orders_empty_dataframe():
    """Empty order data should be handled."""

    orders = pd.DataFrame(columns=[
        "order_id",
        "customer_id",
        "order_date",
        "amount",
        "status",
        "source_file",
        "source_row_number"
    ])

    result = transform_orders(orders)

    assert result.empty
