
import re
import pandas as pd


# Common helper: add validation errors to records
def _finalize_validation(data, errors):
    result = data.copy()

    result["rejection_reason"] = [
        "; ".join(row_errors) for row_errors in errors
    ]

    rejected_mask = result["rejection_reason"] != ""

    valid_records = result.loc[~rejected_mask].copy()
    rejected_records = result.loc[rejected_mask].copy()

    return valid_records, rejected_records


# Common helper: check required columns
def _check_schema(data, required_columns, dataset_name):
    missing_columns = set(required_columns) - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name}: Missing required columns: "
            f"{sorted(missing_columns)}"
        )


# -------------------------------------------------
# 1. CUSTOMER VALIDATION
# -------------------------------------------------

def validate_customers(customers):

    required_columns = [
        "customer_id",
        "customer_name",
        "email",
        "city",
        "registration_date",
        "source_file",
        "source_row_number"
    ]

    _check_schema(customers, required_columns, "Customers")

    data = customers.copy().reset_index(drop=True)

    if data.empty:
        return _finalize_validation(data, [])

    errors = [[] for _ in range(len(data))]

    # Clean whitespace for validation
    customer_ids = data["customer_id"].fillna("").astype(str).str.strip()
    names = data["customer_name"].fillna("").astype(str).str.strip()
    emails = data["email"].fillna("").astype(str).str.strip()

    # Required customer ID
    for i in range(len(data)):
        if not customer_ids.iloc[i]:
            errors[i].append("Missing customer_id")

    # Duplicate customer IDs: reject every occurrence
    duplicate_ids = (
        customer_ids.ne("") &
        customer_ids.duplicated(keep=False)
    )

    for i in range(len(data)):
        if duplicate_ids.iloc[i]:
            errors[i].append("Duplicate customer_id")

    # Customer name is mandatory
    for i in range(len(data)):
        if not names.iloc[i]:
            errors[i].append("Missing customer_name")

    # Email is mandatory and must have valid format
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    for i in range(len(data)):
        if not emails.iloc[i]:
            errors[i].append("Missing email")
        elif not re.match(email_pattern, emails.iloc[i]):
            errors[i].append("Invalid email format")

    # Registration date must be valid
    dates = pd.to_datetime(
        data["registration_date"],
        errors="coerce"
    )

    for i in range(len(data)):
        if pd.isna(dates.iloc[i]):
            errors[i].append("Invalid registration_date")

    # City is optional
    data["city"] = data["city"].fillna("").astype(str).str.strip()

    data["customer_id"] = customer_ids
    data["customer_name"] = names
    data["email"] = emails.str.lower()

    return _finalize_validation(data, errors)


# -------------------------------------------------
# 2. ORDER VALIDATION
# -------------------------------------------------

def validate_orders(orders, valid_customer_ids):

    required_columns = [
        "order_id",
        "customer_id",
        "order_date",
        "amount",
        "status",
        "source_file",
        "source_row_number"
    ]

    _check_schema(orders, required_columns, "Orders")

    data = orders.copy().reset_index(drop=True)

    if data.empty:
        return _finalize_validation(data, [])

    errors = [[] for _ in range(len(data))]

    order_ids = data["order_id"].fillna("").astype(str).str.strip()
    customer_ids = data["customer_id"].fillna("").astype(str).str.strip()
    statuses = data["status"].fillna("").astype(str).str.strip().str.title()

    # Required order ID
    for i in range(len(data)):
        if not order_ids.iloc[i]:
            errors[i].append("Missing order_id")

    # Duplicate order IDs
    duplicate_ids = (
        order_ids.ne("") &
        order_ids.duplicated(keep=False)
    )

    for i in range(len(data)):
        if duplicate_ids.iloc[i]:
            errors[i].append("Duplicate order_id")

    # Customer reference validation
    valid_customer_ids = set(valid_customer_ids)

    for i in range(len(data)):
        if not customer_ids.iloc[i]:
            errors[i].append("Missing customer_id")
        elif customer_ids.iloc[i] not in valid_customer_ids:
            errors[i].append("Invalid customer reference")

    # Amount must be numeric and positive
    amounts = pd.to_numeric(data["amount"], errors="coerce")

    for i in range(len(data)):
        if pd.isna(amounts.iloc[i]):
            errors[i].append("Invalid or missing amount")
        elif amounts.iloc[i] <= 0:
            errors[i].append("Amount must be greater than zero")

    # Allowed order statuses
    allowed_statuses = {
        "Pending",
        "Cancelled",
        "Shipped",
        "Delivered"
    }

    for i in range(len(data)):
        if statuses.iloc[i] not in allowed_statuses:
            errors[i].append("Invalid order status")

    # Order date validation
    dates = pd.to_datetime(data["order_date"], errors="coerce")

    for i in range(len(data)):
        if pd.isna(dates.iloc[i]):
            errors[i].append("Invalid order_date")

    # Apply normalized values
    data["order_id"] = order_ids
    data["customer_id"] = customer_ids
    data["status"] = statuses
    data["amount"] = amounts

    return _finalize_validation(data, errors)
