"""Pipeline ETL du MVP (US-04, US-05, US-06).

Reprend la logique validée dans le notebook POC, sous forme de script
exécutable et testable :
- US-04 : pipeline unique déclenchable en CLI (`python -m open_housing_mvp.etl`)
- US-05 : validation du schéma des 13 features, échec explicite sinon
- US-06 : split train/test reproductible (random_state=42), versionné dans data/processed/
"""

from __future__ import annotations

import io
import logging
import ssl
from pathlib import Path
from urllib.request import Request, urlopen

import certifi
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from . import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# NOTE éthique : 'b' (proportion de population noire par quartier) est une
# variable connue comme problématique, retirée de scikit-learn depuis 2020.
# Conservée ici tant qu'elle n'a pas été explicitement tranchée avec le
# business — voir BACKLOG_PRODUIT_v2.md, section "Out of Scope".
EXPECTED_FEATURES = [
    "crim", "zn", "indus", "chas", "nox", "rm", "age",
    "dis", "rad", "tax", "ptratio", "b", "lstat",
]
TARGET_RAW_COL = "medv"


class SchemaValidationError(Exception):
    """Levée quand le dataset brut ne respecte pas le schéma attendu (US-05)."""


def fetch_data(data_url: str = config.DATA_URL) -> pd.DataFrame:
    logger.info("Récupération du dataset depuis %s", data_url)
    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        request = Request(data_url, headers={"User-Agent": "open-housing-projet/1.0"})
        with urlopen(request, context=ssl_context) as response:
            content = response.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001 — on veut échouer bruyamment avec contexte
        raise RuntimeError(f"Impossible de récupérer le dataset depuis {data_url}: {exc}") from exc
    logger.info("Dataset récupéré : %d lignes, %d colonnes", *df.shape)
    return df


def validate_schema(df: pd.DataFrame) -> None:
    """US-05 : les 13 colonnes de features + la cible doivent être présentes et numériques."""
    expected = EXPECTED_FEATURES + [TARGET_RAW_COL]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise SchemaValidationError(f"Colonne(s) manquante(s) dans le dataset : {missing}")

    non_numeric = [c for c in expected if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise SchemaValidationError(f"Colonne(s) censée(s) être numérique(s) et ne le sont pas : {non_numeric}")

    logger.info("Schéma validé : %d colonnes attendues présentes.", len(expected))


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage : dédoublonnage, imputation médiane, conversion price_usd."""
    before = len(df)
    df = df.drop_duplicates().copy()

    num_cols = df.select_dtypes(include=[np.number]).columns
    n_missing = int(df[num_cols].isna().sum().sum())
    if n_missing:
        logger.warning("Imputation de %d valeurs manquantes par la médiane.", n_missing)
        df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    df["price_usd"] = df[TARGET_RAW_COL] * 1000
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].astype("float64")

    logger.info("Nettoyage : %d -> %d lignes (doublons supprimés : %d)", before, len(df), before - len(df))
    assert df.isna().sum().sum() == 0, "Il reste des valeurs manquantes après nettoyage"
    return df


def split_and_save(df: pd.DataFrame, output_dir: Path = config.PROCESSED_DIR) -> tuple[Path, Path]:
    """US-06 : split reproductible, versionné dans data/processed/."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = train_test_split(
        df, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE
    )

    train_path = output_dir / "train.csv"
    test_path = output_dir / "test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    logger.info("Train (%d lignes) -> %s", len(train_df), train_path)
    logger.info("Test (%d lignes) -> %s", len(test_df), test_path)
    return train_path, test_path


def run_etl(
    data_url: str = config.DATA_URL,
    output_dir: Path = config.PROCESSED_DIR,
) -> tuple[Path, Path]:
    """Pipeline ETL complet, déclenchable en CLI (US-04)."""
    df = fetch_data(data_url)
    validate_schema(df)
    df = clean_data(df)
    return split_and_save(df, output_dir)


if __name__ == "__main__":
    run_etl()
