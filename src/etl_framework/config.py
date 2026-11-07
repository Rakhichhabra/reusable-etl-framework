
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REJECTED_DATA_DIR = DATA_DIR / "rejected"

# Output directories
LOG_DIR = PROJECT_ROOT / "logs"
REPORT_DIR = PROJECT_ROOT / "reports"
LOG_FILE = LOG_DIR / "etl_pipeline.log"

# Input datasets
CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
ORDERS_FILE = RAW_DATA_DIR / "orders.csv"

# Database configuration
DATABASE_PATH = PROCESSED_DATA_DIR / "etl_database.db"

# Logging configuration
LOG_FILE = LOG_DIR / "etl_pipeline.log"

# Pipeline configuration
DATASETS = ["customers", "orders"]
