"""Tests du pipeline ETL du MVP (US-04, US-05, US-06)."""

import pandas as pd
import pytest

from open_housing_mvp.etl import (
    EXPECTED_FEATURES,
    SchemaValidationError,
    clean_data,
    validate_schema,
)


def _minimal_valid_df() -> pd.DataFrame:
    row = {col: 1.0 for col in EXPECTED_FEATURES}
    row["medv"] = 24.0
    return pd.DataFrame([row, dict(row)])


def test_validate_schema_passes_on_valid_data():
    validate_schema(_minimal_valid_df())


def test_validate_schema_fails_on_missing_column():
    df = _minimal_valid_df().drop(columns=["rm"])
    with pytest.raises(SchemaValidationError):
        validate_schema(df)


def test_validate_schema_fails_on_non_numeric_column():
    df = _minimal_valid_df()
    df["rm"] = "not-a-number"
    with pytest.raises(SchemaValidationError):
        validate_schema(df)


def test_clean_data_removes_duplicates_and_creates_price_usd():
    df = _minimal_valid_df()
    cleaned = clean_data(df)
    assert len(cleaned) == 1
    assert "price_usd" in cleaned.columns
    assert cleaned["price_usd"].iloc[0] == 24000.0
    assert cleaned.isna().sum().sum() == 0
