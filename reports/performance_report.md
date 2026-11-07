# ETL Pipeline Performance Report

- Run ID: 4edf9eac-027a-4d64-a344-e035178b56ff
- Pipeline Status: SUCCESS
- Total Input Records: 350003
- Started At (UTC): 2026-11-07T20:00:46.154622+00:00
- Ended At (UTC): 2026-11-07T20:01:01.620702+00:00
- Failure Reason: None
- Total Loaded Records: 349993
- Total Rejected Records: 10
- Execution Duration: 15.4661 seconds
- Processing Throughput: 22630.33 records/second

## Dataset Performance

### Customers

- Input: 100001
- Valid: 99997
- Rejected: 4
- Loaded: 99997

### Orders

- Input: 250002
- Valid: 249996
- Rejected: 6
- Loaded: 249996

## Reconciliation

- Input reconciliation: True
- Load reconciliation: True
- Overall status: PASS

## Optimization

The pipeline uses vectorized pandas operations to perform data cleaning and transformation without row-by-row Python loops. These operations include vectorized string standardization, numeric conversion, datetime parsing, and extraction of order year and month.

For database loading, SQLite UPSERT operations support idempotent inserts and updates, while executemany is used for efficient multiple-record loading.

The pipeline processed 350003 input records in 15.4661 seconds, achieving a throughput of 22630.33 records/second.

Note: A separate before-and-after benchmark was not performed, so no specific percentage improvement is claimed.
