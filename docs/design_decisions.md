# Design Decisions and Trade-offs

## 1. Overview

This document explains the major technical decisions and trade-offs made while developing the Reusable Data Engineering ETL Framework.

The primary goal was to build a modular, maintainable, testable, and locally executable ETL solution within the assignment timeline.

The design prioritizes data quality, record traceability, reproducibility, idempotent loading, and operational visibility.

## 2. Technology Selection

| Technology | Purpose | Reason for Selection |
|---|---|---|
| Python | Core implementation | Simple, reusable, and widely used in data engineering |
| pandas | Data processing | Provides convenient CSV reading and tabular transformations |
| SQLite | Target storage | Lightweight database that does not require a separate server |
| pytest | Automated testing | Supports isolated unit tests and end-to-end testing |
| Python Logging | Operational logging | Provides application logs and error tracking |
| UUID | Pipeline run identification | Generates unique identifiers for pipeline executions |

## 3. Modular Architecture

The framework separates responsibilities into individual components:

- `config.py`: Centralizes project paths and configuration.
- `extract.py`: Reads source files and adds source metadata.
- `validate.py`: Applies schema and business-rule checks.
- `transform.py`: Cleans and standardizes valid records.
- `load.py`: Loads valid data into SQLite.
- `quarantine.py`: Preserves invalid records.
- `logger.py`: Records execution activities and errors.
- `metrics.py`: Tracks pipeline counts, duration, and status.
- `reporting.py`: Generates pipeline, reconciliation, and performance reports.
- `pipeline.py`: Orchestrates the complete workflow.

**Decision:** Keep each ETL responsibility independent.

**Benefits:**
- Individual components can be tested independently.
- Components can be maintained and reused.
- Changes in one component have limited impact on others.
- The architecture can be extended to support additional datasets.

**Trade-off:** More modules and interfaces need to be maintained than in a single-file implementation.

## 4. CSV and pandas for Extraction

**Decision:** Use pandas to read CSV source files.

**Reason:**

The assignment requires a local and reproducible implementation. CSV files provide simple sample inputs, while pandas supports convenient tabular processing.

The extraction component also adds source filename and source row number metadata for traceability.

**Benefits:**
- Simple source ingestion.
- Convenient tabular data processing.
- Easy integration with validation and transformation components.

**Trade-off:**

The current implementation loads entire datasets into memory. Chunk-based processing or distributed processing may be required for significantly larger workloads.

## 5. SQLite for Target Storage

**Decision:** Use SQLite as the local target database.

**Reasons:**
- No external database server is required.
- Easy to configure and reproduce.
- Supports primary-key constraints and SQL queries.
- Suitable for the scope of this assignment.

**Benefits:**

The database provides persistent local storage for valid customer records, order records, and quarantined records.

**Trade-off:**

SQLite is not intended for high-concurrency enterprise data workloads or distributed data processing.

## 6. Data Validation and Quarantine

**Decision:** Separate valid and rejected records.

**Reason:**

Invalid records should not silently disappear or enter the target tables.

The framework validates required fields, duplicate identifiers, data formats, business rules, and customer references.

Rejected records retain:

- Source filename.
- Source row number.
- Rejection reason.
- Pipeline run ID.
- Original record content.
- Quarantine timestamp.

**Benefits:**
- Invalid records remain available for investigation.
- Data quality issues can be traced to their original source.
- Rejected records are not silently discarded.

**Trade-off:**

Quarantine storage requires additional disk space and retention management.

## 7. Idempotent Loading Using UPSERT

**Decision:** Use SQLite UPSERT operations based on primary keys.

**Reason:**

Reprocessing the same source records should not create unintended duplicate rows.

**Benefits:**
- New records are inserted.
- Existing records are updated.
- Repeated processing of the same records does not create duplicate primary-key entries.

**Trade-offs:**
- The current implementation does not synchronize source deletions with the target database.
- Separate historical versions of updated records are not maintained.
- Schema evolution is not automatically supported.

## 8. Pipeline Run Identification

**Decision:** Generate a UUID for every pipeline execution.

**Reason:**

A unique run ID helps associate rejected records, metrics, and execution information with a particular pipeline run.

**Benefits:**
- Improves traceability.
- Helps investigate pipeline failures.
- Associates quarantine records with their execution context.

## 9. Logging and Metrics

**Decision:** Use Python logging and a dedicated metrics component.

**Reason:**

Operators need visibility into pipeline progress, errors, record counts, execution duration, and final status.

The framework tracks:

- Pipeline run ID.
- Pipeline start and end timestamps.
- Input record counts.
- Valid and rejected record counts.
- Loaded record counts.
- Execution duration.
- Pipeline execution status.
- Failure details.

**Benefits:**

Makes pipeline execution easier to monitor and troubleshoot.

**Trade-off:**

The current implementation uses local logs and in-memory metrics rather than a centralized monitoring platform.

## 10. Automated Testing

**Decision:** Use pytest for component-level and end-to-end testing.

**Reason:**

Each major ETL component should be verified independently, while integration tests check the complete workflow.

The test suite covers:

- Valid and invalid input records.
- Empty and malformed CSV files.
- Missing required columns.
- Unexpected additional columns.
- Duplicate identifiers.
- Invalid data values.
- Empty-batch processing.
- Idempotent database loading.
- Partial pipeline failure and retry.
- Reproducible data generation.
- Late-arriving and out-of-order records.

**Benefits:**

Automated tests help detect regressions and verify expected pipeline behaviour.

The latest complete test execution passed all 28 tests.

## 11. Recovery and Failure Handling

The pipeline generates a new run ID for each execution.

Database UPSERT operations make retries of the same valid input safer.

Rejected records are associated with the run ID to preserve execution history.

If one dataset fails after another dataset has already loaded successfully, the pipeline can be rerun using the same source files.

**Benefits:**
- Supports recovery through pipeline reruns.
- Prevents unintended duplicate records during repeated loading.
- Preserves failure information for investigation.

**Current limitations:**

Customers and Orders are not loaded as one atomic transaction. If a failure occurs between the two loads, one dataset may already have been committed.

Rerunning the pipeline can safely upsert the same valid records, but full transactional recovery is not implemented.

## 12. Performance Considerations

The current implementation uses pandas and SQLite to keep the solution simple and locally executable.

Performance was tested using generated datasets containing:

- 100,001 customer records.
- 250,002 order records.
- 350,003 total input records.

One recorded execution completed in approximately 31.06 seconds, with throughput of approximately 11,270 records per second.

A subsequent execution completed in approximately 22.46 seconds.

These measurements are local execution results and may vary depending on hardware, database state, and system load.

The performance results are documented in:

`reports/performance_report.md`

**Potential optimization:**

Chunk-based CSV processing could reduce memory consumption for larger datasets.

Further performance improvements should be measured and validated before introducing additional processing complexity.

## 13. Schema Change Handling

The framework validates that all required columns are present in the source data.

Additional source columns are allowed and preserved during validation.

If a required column is missing, the pipeline raises a validation error.

Automatic schema evolution is not supported.

**Decision:** Allow additional columns while enforcing required-column validation.

**Trade-off:** Changes to required fields or target database structures need manual updates to the framework.

## 14. Retry and Recovery

The pipeline can be rerun using the same source files.

The target tables use primary-key-based UPSERT operations, so rerunning the same data does not create duplicate primary-key records.

If one dataset fails after another dataset has loaded successfully, the pipeline can be rerun to recover the failed dataset.

Rejected records are associated with pipeline run IDs, allowing records from separate executions to be distinguished.

The partial-failure and retry behaviour is covered by automated testing.

## 15. Data History and Late-Arriving Records

The target tables maintain the latest available state of each customer and order using UPSERT operations.

Separate historical versions of updated records are not currently maintained.

The synthetic data generator includes an older historical order date to demonstrate late-arriving data. It also shuffles generated order records to simulate out-of-order arrival.

The current framework validates records based on their data quality and business rules. It does not implement event-time watermarking or a separate arrival-time tracking mechanism.

**Trade-off:** Historical event versions and detailed arrival-time analysis would require additional data model and processing support.

## 16. Known Limitations

- Local CSV-based ingestion only.
- Entire datasets are processed in memory.
- No automatic schema evolution.
- No source deletion synchronization.
- No atomic transaction across both dataset loads.
- No historical version tracking for updated customer or order records.
- No event-time watermarking.
- No distributed processing.
- No centralized monitoring platform.

## 17. Future Improvements

- Add API and database source connectors.
- Support configurable schemas and validation rules.
- Introduce chunk-based processing.
- Add transactional recovery.
- Implement incremental processing and backfill support.
- Add historical data tracking.
- Introduce event-time and arrival-time tracking.
- Integrate cloud storage and orchestration tools.
- Add centralized monitoring and alerting.

## 18. Conclusion

The selected architecture prioritizes correctness, modularity, reproducibility, and ease of testing.

Python, pandas, SQLite, and pytest provide a lightweight foundation for demonstrating reusable ETL engineering concepts while keeping the implementation easy to run and review.

The framework demonstrates data quality validation, rejected record traceability, idempotent loading, failure recovery, automated testing, reconciliation, and local performance measurement.