from uuid import uuid4

from src.etl_framework.config import (
    LOG_FILE,
    REPORT_DIR,
    CUSTOMERS_FILE,
    ORDERS_FILE,
    DATABASE_PATH,
    REJECTED_DATA_DIR
)

from src.etl_framework.extract import extract_data

from src.etl_framework.validate import (
    validate_customers,
    validate_orders
)

from src.etl_framework.transform import (
    transform_customers,
    transform_orders
)

from src.etl_framework.load import load_data
from src.etl_framework.quarantine import save_rejected_records
from src.etl_framework.logger import setup_logger
from src.etl_framework.metrics import PipelineMetrics
from src.etl_framework.reporting import generate_reports

def run_pipeline():
    """
    Execute the complete ETL pipeline for customers and orders.
    """

    logger = setup_logger(str(LOG_FILE))
    metrics = PipelineMetrics()
    run_id = str(uuid4())

    metrics.start_pipeline()

    logger.info("ETL pipeline started")
    logger.info(f"Pipeline Run ID: {run_id}")

    try:
        # STEP 1: EXTRACT
        logger.info("Starting data extraction")

        customers = extract_data(CUSTOMERS_FILE)
        orders = extract_data(ORDERS_FILE)

        # STEP 2: VALIDATE CUSTOMERS
        logger.info("Validating customers dataset")

        valid_customers, rejected_customers = (
            validate_customers(customers)
        )

        # STEP 3: VALIDATE ORDERS
        logger.info("Validating orders dataset")

        valid_customer_ids = set(
            valid_customers["customer_id"]
        )

        valid_orders, rejected_orders = validate_orders(
            orders,
            valid_customer_ids
        )

        # STEP 4: QUARANTINE REJECTED RECORDS
        logger.info("Saving rejected records")

        save_rejected_records(
            rejected_customers,
            "customers",
            database_path=str(DATABASE_PATH),
            run_id=run_id,
            rejected_dir=str(REJECTED_DATA_DIR)
        )

        save_rejected_records(
            rejected_orders,
            "orders",
            database_path=str(DATABASE_PATH),
            run_id=run_id,
            rejected_dir=str(REJECTED_DATA_DIR)
        )

        # STEP 5: TRANSFORM
        logger.info("Transforming valid datasets")

        transformed_customers = transform_customers(
            valid_customers
        )

        transformed_orders = transform_orders(
            valid_orders
        )

        # STEP 6: LOAD
        logger.info("Loading customers into SQLite")

        loaded_customers = load_data(
            transformed_customers,
            "customers",
            database_path=str(DATABASE_PATH)
        )

        logger.info("Loading orders into SQLite")

        loaded_orders = load_data(
            transformed_orders,
            "orders",
            database_path=str(DATABASE_PATH)
        )

        # STEP 7: RECORD METRICS
        metrics.record_dataset(
            "customers",
            input_count=len(customers),
            valid_count=len(valid_customers),
            rejected_count=len(rejected_customers),
            loaded_count=loaded_customers
        )

        metrics.record_dataset(
            "orders",
            input_count=len(orders),
            valid_count=len(valid_orders),
            rejected_count=len(rejected_orders),
            loaded_count=loaded_orders
        )

        metrics.finish_pipeline("SUCCESS")

        summary = metrics.get_summary()

        # STEP 8: GENERATE REPORTS
        logger.info("Generating pipeline reports")

        generate_reports(
            summary,
            run_id,
            output_dir=str(REPORT_DIR)
        )

        logger.info("Pipeline reports generated successfully")

        logger.info("ETL pipeline completed successfully")
        logger.info(f"Pipeline metrics: {summary}")

        print("\n========== ETL PIPELINE SUMMARY ==========")
        print(f"Run ID: {run_id}")
        print(f"Status: {summary['status']}")
        print(
            f"Duration: {summary['duration_seconds']} seconds"
        )

        for dataset_name, dataset_metrics in (
            summary["datasets"].items()
        ):
            print(f"\n{dataset_name.upper()}")
            for metric_name, value in dataset_metrics.items():
                print(f"{metric_name}: {value}")

        print("\n==========================================")

        return summary

    except Exception as exc:
        metrics.finish_pipeline(
            status="FAILED",
            failure_reason=str(exc)
        )

        logger.exception("ETL pipeline failed")

        failure_summary = metrics.get_summary()

        try:
            generate_reports(
                failure_summary,
                run_id,
                output_dir=str(REPORT_DIR)
            )
        except Exception:
            logger.exception("Failed to generate failure reports")

        raise


if __name__ == "__main__":
    run_pipeline()
