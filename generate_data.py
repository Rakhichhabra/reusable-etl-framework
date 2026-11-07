
import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# Project directory and output location
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"


def random_date(start_date, end_date, rng):
    """Generate a reproducible random date."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=rng.randint(0, total_days)
    )


def generate_customers(count=100, seed=42):
    """Generate customer data with controlled quality issues."""

    rng = random.Random(seed)

    cities = [
        "Delhi",
        "Mumbai",
        "Noida",
        "Pune",
        "Bangalore"
    ]

    records = []

    for i in range(1, count + 1):

        record = {
            "customer_id": f"C{i:05d}",
            "customer_name": f"Customer_{i}",
            "email": f"customer{i}@example.com",
            "city": rng.choice(cities),
            "registration_date": random_date(
                date(2024, 1, 1),
                date(2026, 10, 31),
                rng
            ).isoformat()
        }

        records.append(record)

    # Inject controlled data-quality issues.
    if count >= 10:

        # Missing required customer name
        records[2]["customer_name"] = None

        # Invalid email format
        records[3]["email"] = "invalid-email"

        # City is optional, so this is allowed.
        records[4]["city"] = None

        # Keep IDs of customers with valid required fields.
        invalid_customer_ids = {
            records[0]["customer_id"],
            records[2]["customer_id"],
            records[3]["customer_id"]
        }

        # Duplicate customer primary key
        records.append(records[0].copy())

    else:
        invalid_customer_ids = set()

    valid_customer_ids = [
        record["customer_id"]
        for record in records[:count]
        if record["customer_id"] not in invalid_customer_ids
    ]

    return pd.DataFrame(records), valid_customer_ids


def generate_orders(
    customer_ids,
    count=250,
    seed=42
):
    """Generate order data with controlled business-rule issues."""

    rng = random.Random(seed + 1)

    statuses = [
        "Pending",
        "Shipped",
        "Delivered",
        "Cancelled"
    ]

    records = []

    for i in range(1, count + 1):

        record = {
            "order_id": f"O{i:06d}",
            "customer_id": rng.choice(customer_ids),
            "order_date": random_date(
                date(2025, 1, 1),
                date(2026, 11, 7),
                rng
            ).isoformat(),
            "amount": round(
                rng.uniform(100, 10000), 2
            ),
            "status": rng.choice(statuses)
        }

        records.append(record)

    # Inject controlled edge cases.
    if count >= 10:

        # Negative order amount
        records[0]["amount"] = -500

        # Invalid customer reference
        records[1]["customer_id"] = "C999999"

        # Missing required amount
        records[2]["amount"] = None

        # Invalid order status
        records[3]["status"] = "Unknown"

        # Duplicate order ID
        records.append(records[4].copy())

        # Late-arriving historical order
        records.append({
            "order_id": f"O{count + 1:06d}",
            "customer_id": customer_ids[0],
            "order_date": "2024-01-01",
            "amount": 1500.00,
            "status": "Delivered"
        })

    # Simulate out-of-order arrival.
    rng.shuffle(records)

    return pd.DataFrame(records)


def main():

    parser = argparse.ArgumentParser(
        description="Generate synthetic ETL datasets."
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=100
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=250
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42
    )

    args = parser.parse_args()

    if args.customers < 1 or args.orders < 1:
        parser.error("Record counts must be positive.")

    # Create output directory if it does not exist.
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Generate both datasets.
    customers, valid_customer_ids = generate_customers(
        count=args.customers,
        seed=args.seed
    )

    orders = generate_orders(
        customer_ids=valid_customer_ids,
        count=args.orders,
        seed=args.seed
    )

    # Save datasets as CSV files.
    customers.to_csv(
        RAW_DIR / "customers.csv",
        index=False
    )

    orders.to_csv(
        RAW_DIR / "orders.csv",
        index=False
    )

    print("\nDATA GENERATION SUCCESSFUL")
    print("=" * 40)

    print(f"Customers generated: {len(customers)}")
    print(f"Orders generated: {len(orders)}")

    print(f"Customer file: {RAW_DIR / 'customers.csv'}")
    print(f"Orders file: {RAW_DIR / 'orders.csv'}")

    print(f"Random seed: {args.seed}")


if __name__ == "__main__":
    main()
