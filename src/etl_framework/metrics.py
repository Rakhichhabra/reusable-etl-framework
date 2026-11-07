
import time
from datetime import datetime, timezone


class PipelineMetrics:
    """
    Tracks execution metrics and operational details for an ETL pipeline.
    """

    def __init__(self):
        self.start_time = None
        self.end_time = None

        self.started_at = None
        self.ended_at = None
        self.failure_reason = None

        self.metrics = {
            "customers": {
                "input_records": 0,
                "valid_records": 0,
                "rejected_records": 0,
                "loaded_records": 0
            },
            "orders": {
                "input_records": 0,
                "valid_records": 0,
                "rejected_records": 0,
                "loaded_records": 0
            }
        }

        self.status = "NOT_STARTED"

    def start_pipeline(self):
        """Record pipeline start time."""

        self.start_time = time.perf_counter()

        self.started_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.status = "RUNNING"

    def record_dataset(
        self,
        dataset_name,
        input_count,
        valid_count,
        rejected_count,
        loaded_count=0
    ):
        """Record input, valid, rejected and loaded row counts."""

        if dataset_name not in self.metrics:
            raise ValueError(f"Unknown dataset: {dataset_name}")

        if input_count != valid_count + rejected_count:
            raise ValueError(
                "Input records must equal valid + rejected records"
            )

        if loaded_count != valid_count:
            raise ValueError(
                "Loaded records must equal valid records"
            )

        self.metrics[dataset_name] = {
            "input_records": input_count,
            "valid_records": valid_count,
            "rejected_records": rejected_count,
            "loaded_records": loaded_count
        }

    def finish_pipeline(self, status="SUCCESS", failure_reason=None):
        """Record pipeline end time and final status."""

        self.end_time = time.perf_counter()

        self.ended_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.status = status
        self.failure_reason = failure_reason

    def get_summary(self):
        """Return all pipeline execution metrics."""

        duration = None

        if self.start_time is not None and self.end_time is not None:
            duration = round(
                self.end_time - self.start_time, 4
            )

        return {
            "status": self.status,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "duration_seconds": duration,
            "failure_reason": self.failure_reason,
            "datasets": self.metrics
        }
