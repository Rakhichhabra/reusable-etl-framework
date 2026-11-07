
import csv
import json
from pathlib import Path


def generate_reports(summary, run_id, output_dir="reports"):
    """
    Generate pipeline summary, reconciliation, and performance reports.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    datasets = summary["datasets"]

    # Calculate totals across all datasets
    total_input = sum(
        data["input_records"] for data in datasets.values()
    )

    total_valid = sum(
        data["valid_records"] for data in datasets.values()
    )

    total_rejected = sum(
        data["rejected_records"] for data in datasets.values()
    )

    total_loaded = sum(
        data["loaded_records"] for data in datasets.values()
    )

    # Reconciliation checks
    input_reconciled = total_input == total_valid + total_rejected
    load_reconciled = total_loaded == total_valid

    reconciliation_status = (
        "PASS" if input_reconciled and load_reconciled else "FAIL"
    )

    # 1. PIPELINE SUMMARY JSON
    report_data = {
        "run_id": run_id,
        "status": summary["status"],
        "started_at": summary["started_at"],
        "ended_at": summary["ended_at"],
        "duration_seconds": summary["duration_seconds"],
        "failure_reason": summary["failure_reason"],
        "datasets": datasets,
        "totals": {
            "input_records": total_input,
            "valid_records": total_valid,
            "rejected_records": total_rejected,
            "loaded_records": total_loaded
        },
        "reconciliation": {
            "input_equals_valid_plus_rejected": input_reconciled,
            "loaded_equals_valid": load_reconciled,
            "status": reconciliation_status
        }
    }

    summary_file = output_path / "pipeline_summary.json"

    with open(summary_file, "w", encoding="utf-8") as file:
        json.dump(report_data, file, indent=4)

    # 2. RECONCILIATION CSV
    reconciliation_file = output_path / "reconciliation_report.csv"

    with open(
        reconciliation_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "dataset",
            "input_records",
            "valid_records",
            "rejected_records",
            "loaded_records",
            "input_reconciliation",
            "load_reconciliation",
            "status"
        ])

        for dataset_name, data in datasets.items():

            input_check = (
                data["input_records"]
                == data["valid_records"] + data["rejected_records"]
            )

            load_check = (
                data["loaded_records"] == data["valid_records"]
            )

            status = "PASS" if input_check and load_check else "FAIL"

            writer.writerow([
                dataset_name,
                data["input_records"],
                data["valid_records"],
                data["rejected_records"],
                data["loaded_records"],
                input_check,
                load_check,
                status
            ])

        writer.writerow([
            "TOTAL",
            total_input,
            total_valid,
            total_rejected,
            total_loaded,
            input_reconciled,
            load_reconciled,
            reconciliation_status
        ])

    # 3. PERFORMANCE REPORT
    duration = summary["duration_seconds"]

    throughput = (
        total_input / duration if duration > 0 else 0
    )

    performance_file = output_path / "performance_report.md"

    with open(performance_file, "w", encoding="utf-8") as file:

        file.write("# ETL Pipeline Performance Report\n\n")

        file.write(f"- Run ID: {run_id}\n")
        file.write(f"- Pipeline Status: {summary['status']}\n")
        file.write(f"- Total Input Records: {total_input}\n")
        file.write(f"- Started At (UTC): {summary['started_at']}\n")
        file.write(f"- Ended At (UTC): {summary['ended_at']}\n")
        file.write(f"- Failure Reason: {summary['failure_reason'] or 'None'}\n")
        file.write(f"- Total Loaded Records: {total_loaded}\n")
        file.write(f"- Total Rejected Records: {total_rejected}\n")
        file.write(f"- Execution Duration: {duration} seconds\n")
        file.write(
            f"- Processing Throughput: {throughput:.2f} records/second\n\n"
        )

        file.write("## Dataset Performance\n\n")

        for dataset_name, data in datasets.items():

            file.write(f"### {dataset_name.title()}\n\n")
            file.write(f"- Input: {data['input_records']}\n")
            file.write(f"- Valid: {data['valid_records']}\n")
            file.write(f"- Rejected: {data['rejected_records']}\n")
            file.write(f"- Loaded: {data['loaded_records']}\n\n")

        file.write("## Reconciliation\n\n")
        file.write(f"- Input reconciliation: {input_reconciled}\n")
        file.write(f"- Load reconciliation: {load_reconciled}\n")
        file.write(f"- Overall status: {reconciliation_status}\n\n")

        file.write("## Optimization\n\n")
        file.write(
            "The pipeline uses vectorized pandas operations to perform "
            "data cleaning and transformation without row-by-row Python loops. "
            "These operations include vectorized string standardization, "
            "numeric conversion, datetime parsing, and extraction of "
            "order year and month.\n\n"
        )
        file.write(
            "For database loading, SQLite UPSERT operations support "
            "idempotent inserts and updates, while executemany is used "
            "for efficient multiple-record loading.\n\n"
        )
        file.write(
            "The pipeline processed "
            f"{total_input} input records in {duration:.4f} seconds, "
            f"achieving a throughput of {throughput:.2f} records/second.\n\n"
        )
        file.write(
            "Note: A separate before-and-after benchmark was not performed, "
            "so no specific percentage improvement is claimed.\n"
        )


    print("\nReports generated successfully:")
    print(f"- {summary_file}")
    print(f"- {reconciliation_file}")
    print(f"- {performance_file}")

    return report_data
