"""Entraînement du modèle du MVP (US-25, artefacts consommés par l'API).

Hypothèse assumée : le modèle retenu (Gradient Boosting) est celui qui a
gagné la comparaison faite dans le notebook POC (US-07) — ce script ne
recompare pas les 4 modèles, il consolide la décision déjà prise. Si cette
décision doit être revalidée (nouvelles données, dérive de performance),
c'est ce fichier qu'il faut étendre pour réintroduire la comparaison.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from . import config
from .etl import run_etl

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

FEATURE_COLUMNS = [
    "crim", "zn", "indus", "chas", "nox", "rm", "age",
    "dis", "rad", "tax", "ptratio", "b", "lstat",
]
TARGET_COLUMN = "price_usd"


def _load_or_build_processed_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    train_path = config.PROCESSED_DIR / "train.csv"
    test_path = config.PROCESSED_DIR / "test.csv"
    if not train_path.exists() or not test_path.exists():
        logger.info("Données transformées introuvables : lancement de l'ETL.")
        train_path, test_path = run_etl()
    return pd.read_csv(train_path), pd.read_csv(test_path)


def train_model() -> dict:
    """Entraîne le modèle retenu en POC et sauvegarde artefacts + métriques (US-25)."""
    train_df, test_df = _load_or_build_processed_data()

    X_train, y_train = train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df[TARGET_COLUMN]

    model = GradientBoostingRegressor(random_state=config.RANDOM_STATE)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    metrics = {
        "model": "Gradient Boosting",
        "rmse_usd": float(mean_squared_error(y_test, y_pred) ** 0.5),
        "mae_usd": float(mean_absolute_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, config.MODEL_PATH)
    joblib.dump(FEATURE_COLUMNS, config.FEATURES_PATH)
    with open(config.METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Modèle entraîné et sauvegardé -> %s", config.MODEL_PATH)
    logger.info("Métriques : %s", metrics)
    return metrics


if __name__ == "__main__":
    train_model()
