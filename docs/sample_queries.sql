
-- =====================================================
-- REUSABLE ETL FRAMEWORK: SAMPLE SQL QUERIES
-- Database: SQLite
-- Datasets: Customers and Orders
-- =====================================================


-- 1. Total number of customers
SELECT
    COUNT(*) AS total_customers
FROM customers;


-- 2. Total number of orders
SELECT
    COUNT(*) AS total_orders
FROM orders;


-- 3. Customer-wise order count
SELECT
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders
FROM customers c
LEFT JOIN orders o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_name
ORDER BY total_orders DESC;


-- 4. Total order amount by order status
SELECT
    status,
    COUNT(*) AS order_count,
    ROUND(SUM(amount), 2) AS total_amount
FROM orders
GROUP BY status
ORDER BY status;


-- 5. Check orders with invalid customer references
SELECT
    o.order_id,
    o.customer_id
FROM orders o
LEFT JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- 6. Check duplicate customer primary keys
SELECT
    customer_id,
    COUNT(*) AS duplicate_count
FROM customers
GROUP BY customer_id
HAVING COUNT(*) > 1;


-- 7. Check duplicate order primary keys
SELECT
    order_id,
    COUNT(*) AS duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;


-- 8. Check missing customer information
SELECT *
FROM customers
WHERE customer_id IS NULL
   OR customer_name IS NULL
   OR email IS NULL;


-- 9. Check invalid or non-positive order amounts
SELECT *
FROM orders
WHERE amount IS NULL
   OR amount <= 0;


-- 10. Rejected records by dataset and reason
-- Actual database column name is dataset_name
SELECT
    dataset_name,
    rejection_reason,
    COUNT(*) AS rejected_count
FROM rejected_records
GROUP BY
    dataset_name,
    rejection_reason
ORDER BY
    dataset_name,
    rejected_count DESC;


-- 11. Rejected records by pipeline run
SELECT
    run_id,
    dataset_name,
    COUNT(*) AS rejected_count
FROM rejected_records
GROUP BY
    run_id,
    dataset_name
ORDER BY run_id;


-- 12. Inspect rejected record traceability
SELECT
    run_id,
    dataset_name,
    source_file,
    source_row_number,
    rejection_reason,
    raw_record,
    quarantined_at
FROM rejected_records
ORDER BY quarantined_at DESC
LIMIT 20;


-- 13. Monthly order summary
SELECT
    order_year,
    order_month,
    COUNT(*) AS total_orders,
    ROUND(SUM(amount), 2) AS total_revenue
FROM orders
GROUP BY
    order_year,
    order_month
ORDER BY
    order_year,
    order_month;


-- 14. Overall target data quality summary
SELECT
    (SELECT COUNT(*) FROM customers) AS customer_count,
    (SELECT COUNT(*) FROM orders) AS order_count,
    (
        SELECT COUNT(*)
        FROM orders o
        LEFT JOIN customers c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    ) AS orphan_order_count;
