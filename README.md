# Reusable Data Engineering ETL Framework

## 1. Project Overview

The Reusable Data Engineering ETL Framework is a Python-based solution designed to extract, validate, transform, and load data from multiple datasets into a local SQLite database.

The framework demonstrates reusable ETL components using two datasets: Customers and Orders. It includes data quality checks, rejected record quarantine, logging, operational metrics, automated testing, and idempotent database loading.

The project is designed to demonstrate a modular, reproducible, and scalable approach to building data engineering pipelines.

## 2. Project Objectives

- Build reusable and modular ETL components.
- Process multiple datasets using a common framework.
- Define source and target schemas with data types and keys.
- Validate data quality and business rules.
- Preserve invalid records for investigation and traceability.
- Support safe pipeline reruns and recovery after failures.
- Track execution metrics, row counts, and pipeline status.
- Generate reproducible sample data for testing.
- Implement automated tests for positive and negative scenarios.
- Provide reconciliation reports and performance measurements.

## 3. Key Features

- CSV-based data extraction using pandas.
- Required-column and schema validation.
- Business-rule validation and duplicate detection.
- Data cleaning and standardization.
- SQLite database loading using primary-key-based UPSERT.
- Rejected record quarantine with rejection reasons.
- Source file and source row-level traceability.
- Unique pipeline run IDs using UUID.
- Centralized logging and execution metrics.
- Pipeline failure reporting and retry support.
- Reconciliation and performance reports.
- Reproducible synthetic data generation.
- Automated testing using pytest.

## 4. Datasets

The framework uses two synthetic datasets.

### Customers

Contains customer information:

- `customer_id`
- `customer_name`
- `email`
- `city`
- `registration_date`

The `customer_id` field acts as the primary key.

### Orders

Contains order information:

- `order_id`
- `customer_id`
- `order_date`
- `amount`
- `status`

The `order_id` field acts as the primary key, while `customer_id` references the Customers dataset.

### Dataset Relationship

Each order belongs to a customer through `customer_id`.

The relationship between the datasets is:

**Customers (1) → Orders (Many)**

## 5. ETL Architecture

The framework follows a modular ETL workflow:

1. **Extract:** Read customer and order CSV files using pandas. Source file names and row numbers are retained for traceability.
2. **Validate:** Check required fields, duplicate keys, email formats, dates, amounts, order statuses, and customer references.
3. **Quarantine:** Store invalid records with rejection reasons, source metadata, and pipeline run IDs.
4. **Transform:** Clean and standardize valid records, convert data types, and derive additional order attributes.
5. **Load:** Store transformed records in SQLite using primary-key-based UPSERT operations.
6. **Monitor:** Record execution logs, row counts, pipeline status, errors, and execution duration.
7. **Report:** Generate pipeline summary, reconciliation, and performance reports.

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core ETL development |
| pandas | Data extraction and transformation |
| SQLite | Local target database |
| pytest | Automated testing |
| Logging | Pipeline execution and error logging |
| UUID | Unique pipeline run identification |

## 7. Project Structure

```text
reusable-etl-framework/
├── ai_documentation/
│   └── prompts.md
├── data/
│   ├── raw/
│   │   ├── customers.csv
│   │   └── orders.csv
│   ├── processed/
│   └── rejected/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   ├── design_decisions.md
│   └── sample_queries.sql
├── logs/
├── reports/
│   ├── pipeline_summary.json
│   ├── reconciliation_report.csv
│   └── performance_report.md
├── src/
│   └── etl_framework/
│       ├── __init__.py
│       ├── config.py
│       ├── extract.py
│       ├── load.py
│       ├── logger.py
│       ├── metrics.py
│       ├── pipeline.py
│       ├── quarantine.py
│       ├── reporting.py
│       ├── transform.py
│       └── validate.py
├── tests/
│   ├── test_extract.py
│   ├── test_generate_data.py
│   ├── test_load.py
│   ├── test_pipeline.py
│   ├── test_transform.py
│   └── test_validate.py
├── generate_data.py
├── run_pipeline.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 8. Installation and Setup

### Prerequisites

- Python 3.10 or later.
- pip package manager.
- Visual Studio Code or another Python-compatible editor.

### Create a Virtual Environment

```bash
python -m venv .venv
```

### Activate the Virtual Environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Verify Dependencies

```bash
python -m pip check
```

## 9. Generate Sample Data

The project includes a configurable synthetic data generator.

To generate the default sample datasets:

```bash
python generate_data.py
```

The default generator creates approximately:

- 101 customer records.
- 252 order records.

The generated datasets include deliberately introduced data-quality scenarios such as missing values, invalid emails, duplicate identifiers, negative amounts, invalid customer references, and invalid order statuses.

### Generate Large Datasets

The generator also supports larger datasets.

Example:

```bash
python generate_data.py --customers 100000 --orders 250000 --seed 42
```

This generates:

- 100,001 customer records.
- 250,002 order records.

The additional records represent deliberately generated invalid and duplicate scenarios.

A fixed random seed supports reproducibility of generated datasets.

## 10. Run the ETL Pipeline

Execute the following command:

```bash
python run_pipeline.py
```

The pipeline processes both datasets through extraction, validation, quarantine, transformation, and loading.

### Output Locations

- Valid transformed records: `data/processed/etl_database.db`
- Rejected customer records: `data/rejected/rejected_customers.csv`
- Rejected order records: `data/rejected/rejected_orders.csv`
- Execution logs: `logs/etl_pipeline.log`
- Pipeline summary: `reports/pipeline_summary.json`
- Reconciliation report: `reports/reconciliation_report.csv`
- Performance report: `reports/performance_report.md`

## 11. Run Automated Tests

Execute the complete test suite:

```bash
python -m pytest -v
```

### Latest Test Results

The current automated test suite contains 30 tests.

| Test Result | Count |
|---|---:|
| Total Tests | 30 |
| Passed | 30 |
| Failed | 0 |
| Execution Time | 1.14 seconds |

All 30 tests passed during the latest local verification.

## 12. Data Quality and Reconciliation

The framework performs data quality checks across both datasets.

### Validation Rules

**Customers:**

- Required-column validation.
- Customer ID uniqueness.
- Customer name validation.
- Email format validation.
- Registration date validation.

**Orders:**

- Required-column validation.
- Order ID uniqueness.
- Customer reference validation.
- Positive order amount validation.
- Order date validation.
- Allowed order status validation.

### Reconciliation

The framework generates a reconciliation report after each pipeline execution.

The report tracks:

- Input records.
- Valid records.
- Rejected records.
- Loaded records.

The reconciliation rule is:

**Input Records = Valid Records + Rejected Records**

The report is available at:

`reports/reconciliation_report.csv`

Rejected records retain source file names, source row numbers, and rejection reasons for investigation and traceability.

## 13. Idempotency and Recovery

The SQLite loading component uses primary-key-based UPSERT operations.

Reprocessing the same input updates existing records instead of creating unintended duplicate records.

Rejected records are stored with pipeline run IDs. Repeated quarantine entries within the same run are prevented using a unique constraint.

The pipeline supports reruns after failures. A partial failure can be recovered by rerunning the pipeline with the same source files.

The retry behavior is covered through automated pipeline testing.

### Recovery Limitations

- Cross-dataset atomic transactions are not implemented.
- Automatic deletion of target records removed from source files is not supported.
- Automatic schema evolution is not supported.

## 14. Logging and Operational Metrics

The framework records operational information for each pipeline execution.

The tracked information includes:

- Unique pipeline run ID.
- Pipeline start and end timestamps.
- Pipeline execution status.
- Dataset input counts.
- Valid and rejected record counts.
- Loaded record counts.
- Execution duration.
- Failure reason and error details.

The framework generates a JSON pipeline summary and maintains execution logs for troubleshooting.

## 15. Automated Test Coverage

The automated test suite covers the following scenarios:

- Valid CSV extraction.
- Empty CSV file handling.
- Missing source files.
- Malformed CSV input.
- Reserved metadata columns.
- Missing required columns.
- Unexpected additional columns.
- Invalid customer emails.
- Duplicate customer identifiers.
- Negative order amounts.
- Invalid order statuses.
- Empty DataFrame transformations.
- Duplicate primary-key protection.
- Idempotent UPSERT loading.
- End-to-end pipeline execution.
- Empty-batch processing.
- Partial pipeline failure and retry.
- Reproducible sample data generation.
- Late-arriving historical order generation.
- Out-of-order record generation.

The complete suite currently passes all 30 tests.

## 16. Performance Measurement

The framework was tested locally using generated datasets containing:

- 100,001 customer records.
- 250,002 order records.
- 350,003 total input records.

During one recorded execution, the pipeline processed the dataset in approximately 31.06 seconds, with a throughput of approximately 11,270 records per second.

A subsequent execution completed in approximately 22.46 seconds.

These measurements are local execution results and may vary depending on hardware, database state, and system load.

The detailed results are available in:

`reports/performance_report.md`

## 17. Design Decisions and Limitations

### Design Decisions

- **Python:** Selected for reusable ETL development and data processing.
- **pandas:** Used for tabular extraction, validation, and transformation.
- **SQLite:** Selected to keep the framework lightweight and locally executable without external infrastructure.
- **UPSERT:** Used to support safe repeated loading based on primary keys.
- **Quarantine:** Used to preserve rejected records and their rejection reasons.
- **UUID:** Used to identify individual pipeline executions.

### Schema Handling

The framework checks that all required columns are present in the source data.

Additional source columns are allowed and preserved during validation.

Missing required columns cause a validation error. Automatic schema evolution is not supported.

### Data History

The target tables maintain the latest available state of each customer and order through UPSERT operations.

Separate historical versions of updated records are not currently maintained.

### Known Limitations

- Local CSV and SQLite-based processing.
- No automatic source-to-target deletion synchronization.
- No automatic schema evolution.
- No single atomic transaction across both datasets.
- No distributed processing or cloud orchestration.
- Performance measurements are local and are not production-scale benchmarks.

## 18. Future Improvements

- Support additional source formats such as JSON and Parquet.
- Introduce API-based data extraction.
- Add configurable schema definitions.
- Implement incremental data processing.
- Introduce historical data tracking.
- Add distributed processing for larger workloads.
- Support cloud-based storage and orchestration.
- Improve monitoring and alerting capabilities.

## 19. AI Assistance

AI tools were used as development aids for project planning, implementation guidance, debugging, automated test design, and documentation.

Generated suggestions were reviewed, adapted to the assignment requirements, and validated through local execution and automated testing.

A summary of the prompts and areas of AI assistance is available in:

`ai_documentation/prompts.md`

## 20. Conclusion

This project demonstrates a modular and reusable ETL framework using Customers and Orders datasets.

It covers data extraction, schema and business-rule validation, transformation, rejected record quarantine, idempotent database loading, logging, operational metrics, automated testing, reconciliation, and performance measurement.

The implementation provides a reproducible local solution that demonstrates core data engineering practices and can be extended for larger data processing workloads.