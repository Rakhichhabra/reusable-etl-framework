
import json
import sqlite3
from pathlib import Path
from uuid import uuid4


def save_rejected_records(
    rejected_data,
    dataset_name,
    database_path="data/processed/etl_database.db",
    run_id=None,
    rejected_dir="data/rejected"
):
    """
    Save rejected records into SQLite quarantine table
    and export them as dataset-specific CSV files.

    Re-running the same batch with the same run_id
    will not create duplicate database records.
    """

    # Step 1: Check whether rejected data is empty
    if rejected_data.empty:
        print(f"No rejected records for {dataset_name}")
        return 0

    # Step 2: Check rejection_reason column
    if "rejection_reason" not in rejected_data.columns:
        raise ValueError("Missing rejection_reason column")

    # Step 3: Generate a unique run ID if not provided
    run_id = run_id or str(uuid4())

    # Step 4: Create database directory
    Path(database_path).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 5: Prepare records for SQLite insertion
    records = []

    for _, row in rejected_data.iterrows():

        record = row.to_dict()

        rejection_reason = str(
            record.pop("rejection_reason")
        )

        source_file = record.get("source_file")
        source_row_number = record.get("source_row_number")

        records.append((
            run_id,
            dataset_name,
            source_file,
            source_row_number,
            rejection_reason,
            json.dumps(record, default=str)
        ))

    # Step 6: Connect to SQLite database
    with sqlite3.connect(database_path) as connection:

        # Create quarantine table if it does not exist
        connection.execute("""
            CREATE TABLE IF NOT EXISTS rejected_records (
                quarantine_id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                dataset_name TEXT NOT NULL,
                source_file TEXT,
                source_row_number INTEGER,
                rejection_reason TEXT NOT NULL,
                raw_record TEXT NOT NULL,
                quarantined_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Step 7: Prevent duplicate quarantine records
        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_quarantine_unique_record
            ON rejected_records (
                run_id,
                dataset_name,
                source_file,
                source_row_number,
                rejection_reason
            )
        """)

        # Count database changes before insertion
        changes_before = connection.total_changes

        # Insert rejected records into SQLite
        connection.executemany("""
            INSERT OR IGNORE INTO rejected_records (
                run_id,
                dataset_name,
                source_file,
                source_row_number,
                rejection_reason,
                raw_record
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, records)

        # Calculate inserted records
        inserted_count = (
            connection.total_changes - changes_before
        )

    # Step 8: Calculate skipped duplicate records
    skipped_count = len(records) - inserted_count

    # Step 9: Create rejected folder
    rejected_path = Path(rejected_dir)

    rejected_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Step 10: Generate dataset-specific CSV filename
    rejected_file = (
        rejected_path / f"rejected_{dataset_name}.csv"
    )

    # Step 11: Export rejected records into CSV
    rejected_data.to_csv(
        rejected_file,
        index=False,
        encoding="utf-8-sig"
    )

    # Step 12: Display execution summary
    print(
        f"{dataset_name}: "
        f"{inserted_count} inserted into quarantine database, "
        f"{skipped_count} duplicate records skipped"
    )

    print(
        f"Rejected CSV exported successfully: {rejected_file}"
    )

    return inserted_count
