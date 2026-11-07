
import pandas as pd
import pytest

from src.etl_framework.extract import extract_data


def test_extract_valid_csv(tmp_path):
    """Test extraction of a valid CSV file."""

    file_path = tmp_path / "customers.csv"

    pd.DataFrame({
        "customer_id": ["C001", "C002"],
        "customer_name": ["Aman", "Riya"]
    }).to_csv(file_path, index=False)

    result = extract_data(file_path)

    assert len(result) == 2
    assert "source_file" in result.columns
    assert "source_row_number" in result.columns

    assert result["customer_id"].tolist() == ["C001", "C002"]
    assert result["source_file"].tolist() == [
        "customers.csv", "customers.csv"
    ]
    assert result["source_row_number"].tolist() == [2, 3]


def test_extract_empty_csv(tmp_path):
    """Test extraction of an empty CSV file."""

    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    result = extract_data(file_path)

    assert result.empty
    assert "source_file" in result.columns
    assert "source_row_number" in result.columns


def test_extract_missing_file(tmp_path):
    """Test that a missing source file raises an error."""

    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        extract_data(file_path)


def test_extract_malformed_csv(tmp_path):
    """Test that malformed CSV input raises an error."""

    file_path = tmp_path / "malformed.csv"

    file_path.write_text(
        "customer_id,customer_name\n"
        "C001,Aman\n"
        "C002,Riya,ExtraValue\n",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unable to parse source file"):
        extract_data(file_path)


def test_extract_reserved_metadata_columns(tmp_path):
    """Test that source files cannot contain reserved metadata columns."""

    file_path = tmp_path / "reserved.csv"

    pd.DataFrame({
        "customer_id": ["C001"],
        "source_file": ["old_file.csv"]
    }).to_csv(file_path, index=False)

    with pytest.raises(
        ValueError,
        match="reserved metadata columns"
    ):
        extract_data(file_path)
