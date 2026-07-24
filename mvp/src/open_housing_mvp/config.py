"""Configuration du MVP."""

import os
from pathlib import Path

APP_NAME = "open-housing-mvp"

DATA_URL = os.environ.get(
    "DATA_URL",
    "https://raw.githubusercontent.com/selva86/datasets/master/BostonHousing.csv",
)

DATA_DIR = Path(os.environ.get("DATA_DIR", "data"))
PROCESSED_DIR = DATA_DIR / "processed"

MODELS_DIR = Path(os.environ.get("MODELS_DIR", "models"))
MODEL_PATH = MODELS_DIR / "model.pkl"
FEATURES_PATH = MODELS_DIR / "model_features.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.2

API_KEY_ENV_VAR = "API_KEY"
