
import pandas as pd


def transform_customers(customers):
    """
    Clean and standardize valid customer records.
    """

    data = customers.copy().reset_index(drop=True)

    if data.empty:
        return data

    # Remove validation-only column if present
    data = data.drop(
        columns=["rejection_reason"],
        errors="ignore"
    )

    # Remove unwanted whitespace
    data["customer_id"] = (
        data["customer_id"].astype(str).str.strip()
    )

    data["customer_name"] = (
        data["customer_name"].astype(str).str.strip()
    )

    # Standardize email
    data["email"] = (
        data["email"].astype(str).str.strip().str.lower()
    )

    # Standardize city; preserve missing optional city as NULL
    data["city"] = (
        data["city"].astype(str).str.strip()
        .replace("", None)
    )

    # Standardize registration date
    data["registration_date"] = pd.to_datetime(
        data["registration_date"],
        errors="raise"
    ).dt.strftime("%Y-%m-%d")

    return data


def transform_orders(orders):
    """
    Clean and prepare valid order records.
    """

    data = orders.copy().reset_index(drop=True)

    if data.empty:
        return data

    # Remove validation-only column if present
    data = data.drop(
        columns=["rejection_reason"],
        errors="ignore"
    )

    # Standardize IDs
    data["order_id"] = (
        data["order_id"].astype(str).str.strip()
    )

    data["customer_id"] = (
        data["customer_id"].astype(str).str.strip()
    )

    # Convert amount into numeric format
    data["amount"] = pd.to_numeric(
        data["amount"],
        errors="raise"
    ).round(2)

    # Standardize status
    data["status"] = (
        data["status"].astype(str).str.strip().str.title()
    )

    # Standardize order date
    dates = pd.to_datetime(
        data["order_date"],
        errors="raise"
    )

    data["order_date"] = dates.dt.strftime("%Y-%m-%d")

    # Create analytical derived fields
    data["order_year"] = dates.dt.year
    data["order_month"] = dates.dt.month

    return data
