
import logging
from pathlib import Path


def setup_logger(log_file="data/processed/etl_pipeline.log"):
    """
    Configure logging for the ETL pipeline.
    Logs are written to both a file and the terminal.
    """

    # Create the log directory if it does not exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("etl_framework")
    logger.setLevel(logging.INFO)

    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger

    # Define log message format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    # Save logs in a file
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    # Display logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Attach handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
