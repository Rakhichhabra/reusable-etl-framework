
from generate_data import generate_customers, generate_orders


def test_generator_creates_late_arriving_order():
    """Late historical orders should be generated and preserved."""

    _, valid_customer_ids = generate_customers(
        count=20,
        seed=42
    )

    orders = generate_orders(
        customer_ids=valid_customer_ids,
        count=20,
        seed=42
    )

    late_order = orders[
        orders["order_date"] == "2024-01-01"
    ]

    assert len(late_order) == 1
    assert late_order.iloc[0]["amount"] == 1500.00
    assert late_order.iloc[0]["status"] == "Delivered"
    assert late_order.iloc[0]["customer_id"] in valid_customer_ids


def test_generator_is_reproducible():
    """Same seed should generate identical datasets."""

    customers_1, customer_ids_1 = generate_customers(
        count=20,
        seed=42
    )

    customers_2, customer_ids_2 = generate_customers(
        count=20,
        seed=42
    )

    orders_1 = generate_orders(customer_ids_1, count=20, seed=42)
    orders_2 = generate_orders(customer_ids_2, count=20, seed=42)

    assert customers_1.equals(customers_2)
    assert customer_ids_1 == customer_ids_2
    assert orders_1.equals(orders_2)


def test_generator_shuffles_order_records():
    """Generated orders should simulate out-of-order arrival."""

    _, valid_customer_ids = generate_customers(
        count=20,
        seed=42
    )

    orders = generate_orders(
        customer_ids=valid_customer_ids,
        count=20,
        seed=42
    )

    arrival_order = orders["order_id"].tolist()

    sorted_order = sorted(
        arrival_order,
        key=lambda order_id: int(order_id[1:])
    )

    assert arrival_order != sorted_order
