# ETL Pipeline Performance Report

- Run ID: a640ea05-29ef-4144-a409-7e554f2cb623
- Pipeline Status: SUCCESS
- Total Input Records: 4
- Started At (UTC): 2026-11-07T19:15:56.617576+00:00
- Ended At (UTC): 2026-11-07T19:15:56.674347+00:00
- Failure Reason: None
- Total Loaded Records: 2
- Total Rejected Records: 2
- Execution Duration: 0.0568 seconds
- Processing Throughput: 70.42 records/second

## Dataset Performance

### Customers

- Input: 2
- Valid: 1
- Rejected: 1
- Loaded: 1

### Orders

- Input: 2
- Valid: 1
- Rejected: 1
- Loaded: 1

## Reconciliation

- Input reconciliation: True
- Load reconciliation: True
- Overall status: PASS

## Optimization

The pipeline uses vectorized pandas operations to perform data cleaning and transformation without row-by-row Python loops. These operations include vectorized string standardization, numeric conversion, datetime parsing, and extraction of order year and month.

For database loading, SQLite UPSERT operations support idempotent inserts and updates, while executemany is used for efficient multiple-record loading.

The pipeline processed 4 input records in 0.0568 seconds, achieving a throughput of 70.42 records/second.

Note: A separate before-and-after benchmark was not performed, so no specific percentage improvement is claimed.
