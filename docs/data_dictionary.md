# Data Dictionary

## 1. Overview

This document describes the source and target data structures used by the Reusable Data Engineering ETL Framework.

The framework processes two related datasets:

1. Customers
2. Orders

Both datasets are provided as CSV files, validated, transformed, and loaded into a local SQLite database.

This document defines dataset entities, data grain, column definitions, logical data types, keys, nullability, relationships, validation rules, transformation rules, and data quality assumptions.

## 2. Customers Dataset

**Source file:** `data/raw/customers.csv`

**Target table:** `customers`

**Description:** Contains customer profile and registration information.

**Grain:** One record represents one unique customer.

**Primary Key:** `customer_id`

### Column Definitions

| Column | Logical Data Type | Nullable | Key | Description |
|---|---|---|---|---|
| customer_id | STRING | No | Primary Key | Unique customer identifier |
| customer_name | STRING | No | None | Customer full name |
| email | STRING | No | None | Customer email address |
| city | STRING | Yes | None | Customer city |
| registration_date | DATE | No | None | Customer registration date |
| source_file | STRING | No | Metadata | Original source filename |
| source_row_number | INTEGER | No | Metadata | Original CSV row number |

### Validation Rules

- `customer_id` must not be missing or empty.
- `customer_id` must be unique.
- `customer_name` must not be missing or empty.
- `email` must have a valid email format.
- `registration_date` must contain a valid date.
- `city` is optional.
- Duplicate customer records are rejected.

### Transformation Rules

- Remove unnecessary whitespace from string values.
- Convert email addresses to lowercase.
- Convert empty city values to NULL.
- Standardize registration dates to `YYYY-MM-DD`.
- Preserve source filename and source row number for traceability.

## 3. Orders Dataset

**Source file:** `data/raw/orders.csv`

**Target table:** `orders`

**Description:** Contains customer order and transaction information.

**Grain:** One record represents one unique order.

**Primary Key:** `order_id`

**Logical Foreign Key:** `customer_id`

### Column Definitions

| Column | Logical Data Type | Nullable | Key | Description |
|---|---|---|---|---|
| order_id | STRING | No | Primary Key | Unique order identifier |
| customer_id | STRING | No | Logical Foreign Key | References a valid customer |
| order_date | DATE | No | None | Date when the order was placed |
| amount | DECIMAL | No | None | Monetary order amount |
| status | STRING | No | None | Current order status |
| source_file | STRING | No | Metadata | Original source filename |
| source_row_number | INTEGER | No | Metadata | Original CSV row number |
| order_year | INTEGER | No | Derived | Year extracted from order_date |
| order_month | INTEGER | No | Derived | Month extracted from order_date |

**Note:** `order_year` and `order_month` are generated during transformation and are not required in the original source CSV.

### Validation Rules

- `order_id` must not be missing or empty.
- `order_id` must be unique.
- `customer_id` must reference an existing valid customer.
- `order_date` must contain a valid date.
- `amount` must be numeric and greater than zero.
- `status` must belong to the supported values:
  - Pending
  - Cancelled
  - Shipped
  - Delivered
- Invalid order records are rejected.

### Transformation Rules

- Remove unnecessary whitespace.
- Convert amount into numeric format and round it to two decimal places.
- Standardize status values.
- Standardize order dates to `YYYY-MM-DD`.
- Derive `order_year` from `order_date`.
- Derive `order_month` from `order_date`.
- Preserve source filename and source row number for traceability.

## 4. Entity Relationships

The Customers and Orders datasets have a one-to-many relationship.

- One customer can have multiple orders.
- Each valid order must reference an existing customer.
- An order with an invalid customer reference is rejected.

**Relationship:**

`customers.customer_id → orders.customer_id`

The framework validates customer references before accepting order records.

This is a logical referential-integrity check performed by the validation component. The current SQLite implementation does not enforce this relationship through a physical database foreign-key constraint.

## 5. Primary Keys and Foreign Keys

| Dataset | Column | Constraint |
|---|---|---|
| Customers | customer_id | Primary Key |
| Orders | order_id | Primary Key |
| Orders | customer_id | Logical Foreign Key |

The primary keys ensure unique customer and order identifiers.

The customer reference check ensures that accepted orders are associated with valid customers from the current processing batch.

## 6. Data Quality and Nullability

The framework applies the following data quality rules:

- Required identifiers cannot be NULL or empty.
- Duplicate primary keys are rejected.
- Required customer and order fields are validated.
- Optional city values can be NULL.
- Invalid dates and numeric values are rejected.
- Invalid customer references are rejected.
- Invalid records retain their rejection reasons.
- Source filename and row number provide record-level traceability.

## 7. Rejected Record Metadata

Rejected records are stored in the SQLite `rejected_records` table.

| Column | Logical Data Type | Nullable | Description |
|---|---|---|---|
| quarantine_id | INTEGER | No | Unique quarantine record identifier |
| run_id | STRING | No | Pipeline execution identifier |
| dataset_name | STRING | No | Name of the source dataset |
| source_file | STRING | Yes | Original CSV filename |
| source_row_number | INTEGER | Yes | Original CSV row number |
| rejection_reason | STRING | No | Reason for rejection |
| raw_record | JSON/TEXT | No | Original rejected record stored as JSON text |
| quarantined_at | TIMESTAMP | Yes | Quarantine timestamp, generated by SQLite |

A unique constraint prevents duplicate quarantine entries for the same run, dataset, source record, and rejection reason.

Rejected CSV files are also generated separately for customers and orders.

## 8. Naming Conventions

- Table and column names use `snake_case`.
- Customer and order identifiers use stable IDs.
- Dates use ISO-style `YYYY-MM-DD` formatting after transformation.
- Each pipeline execution uses a unique `run_id`.
- Source metadata is preserved using `source_file` and `source_row_number`.
- Derived fields use descriptive names.

## 9. Assumptions and Limitations

- Customer and order records are supplied as CSV files.
- Customer IDs are expected to be unique.
- Orders must reference valid customers from the current processing batch.
- The framework uses SQLite for local storage.
- Monetary amounts are converted to numeric values and rounded to two decimal places.
- Additional source columns are allowed and preserved during validation.
- Missing required columns cause a validation error.
- Automatic schema evolution is not supported.
- Automatic source deletion synchronization is not supported.
- The target tables maintain the latest available state through UPSERT operations.
- Separate historical versions of updated records are not maintained.
- The logical customer-to-order relationship is validated by the pipeline rather than enforced by a SQLite foreign-key constraint.

## 10. Data Traceability

The framework maintains record-level traceability through:

- `source_file`: Identifies the original input file.
- `source_row_number`: Identifies the original CSV row.
- `run_id`: Identifies the pipeline execution.
- `rejection_reason`: Explains why a record was rejected.
- `raw_record`: Preserves the original rejected record.

This information helps investigate data quality issues and understand the processing history of rejected records.