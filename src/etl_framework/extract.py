
from pathlib import Path

import pandas as pd


def extract_data(file_path: str | Path) -> pd.DataFrame:
    """
    Reusable CSV extraction component.

    Reads a CSV file and adds source metadata
    for record-level traceability.
    """

    file_path = Path(file_path)

    # Check whether source file exists.
    if not file_path.exists():
        raise FileNotFoundError(
            f"Source file not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Source path is not a file: {file_path}"
        )

    try:
        # Read all columns as strings initially.
        # This preserves IDs and their leading zeros.
        df = pd.read_csv(
            file_path,
            dtype=str,
            keep_default_na=False,
            on_bad_lines="error"
        )

    except pd.errors.EmptyDataError:
        # Handle a completely empty CSV file.
        print(f"WARNING: Empty source file: {file_path}")

        return pd.DataFrame(
            columns=["source_file", "source_row_number"]
        )

    except (
        pd.errors.ParserError,
        UnicodeDecodeError
    ) as error:
        raise ValueError(
            f"Unable to parse source file "
            f"{file_path.name}: {error}"
        ) from error

    # Prevent conflicts with framework metadata.
    reserved_columns = {
        "source_file",
        "source_row_number"
    }

    if reserved_columns.intersection(df.columns):
        raise ValueError(
            "Source CSV contains reserved metadata columns."
        )

    # Add source information to every record.
    df["source_file"] = file_path.name

    # CSV header is on line 1, so records start on line 2.
    df["source_row_number"] = range(
        2,
        len(df) + 2
    )

    print(
        f"Extracted {len(df)} records "
        f"from {file_path.name}"
    )

    return df
