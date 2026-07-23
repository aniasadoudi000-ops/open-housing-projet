from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from open_housing.config import (
    RAW_DATA_PATH,
    TEST_DATA_PATH,
    TRAIN_DATA_PATH,
)

FEATURE_COLUMNS = [
    "CRIM",
    "ZN",
    "INDUS",
    "CHAS",
    "NOX",
    "RM",
    "AGE",
    "DIS",
    "RAD",
    "TAX",
    "PTRATIO",
    "B",
    "LSTAT",
]
TARGET_COLUMN = "MEDV"


def fetch_raw_data(url: str, destination: Path = RAW_DATA_PATH) -> Path:
    """Download the raw dataset to the expected location."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Placeholder: real implementation to be completed in the ETL phase.
    if not destination.exists():
        raise FileNotFoundError(f"Raw dataset not available at {destination}")
    return destination


def clean_dataset(raw_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load, clean and normalize a raw dataset."""
    df = pd.read_csv(raw_path)
    df = df.dropna().astype(float)
    return df


def split_dataset(df: pd.DataFrame, random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into train and test sets."""
    train_df, test_df = train_test_split(
        df,
        test_size=0.2,
        random_state=random_state,
    )
    return train_df, test_df


def run_etl(url: str, random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run the ETL pipeline end-to-end."""
    raw_path = fetch_raw_data(url)
    df = clean_dataset(raw_path)
    train_df, test_df = split_dataset(df, random_state=random_state)

    TRAIN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_DATA_PATH, index=False)
    test_df.to_csv(TEST_DATA_PATH, index=False)
    return train_df, test_df
