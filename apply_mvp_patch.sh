#!/usr/bin/env bash
set -e

# Run this from the ROOT of open-housing-projet (where pyproject.toml already lives).

mkdir -p .github/workflows mvp/src/open_housing_mvp mvp/src/open_housing_mvp/app mvp/tests poc

cat > pyproject.toml << 'OPENHOUSING_EOF'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "open-housing-projet"
version = "0.1.0"
description = "OpenHousing price prediction API and ML pipeline"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.30",
    "pandas>=2.2",
    "numpy>=1.26",
    "scikit-learn>=1.5",
    "joblib>=1.4",
    "pydantic>=2.8",
    "pytest>=8.2",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
testpaths = ["mvp/tests"]

[tool.setuptools]
package-dir = {"" = "mvp/src"}

[tool.setuptools.packages.find]
where = ["mvp/src"]
OPENHOUSING_EOF

cat > requirements.txt << 'OPENHOUSING_EOF'
fastapi>=0.111
uvicorn[standard]>=0.30
pandas>=2.2
numpy>=1.26
scikit-learn>=1.5
joblib>=1.4
pydantic>=2.8
pytest>=8.2
httpx>=0.27
OPENHOUSING_EOF

cat > README.md << 'OPENHOUSING_EOF'
# OpenHousing

Proof-of-concept and MVP project for estimating real estate prices from the Boston Housing dataset.

## Objective

This project aims to:
- prepare data through an ETL pipeline,
- train a regression model,
- expose a REST API with FastAPI,
- package the application in Docker,
- prepare CI/CD automation and cloud deployment.

## Architecture

```text
open-housing-projet/
├── notebooks/
│   └── OpenHousing_POC_EN.ipynb        # POC = this notebook only (see poc/README.md)
├── poc/
│   └── README.md
├── mvp/
│   ├── README.md
│   ├── src/open_housing_mvp/
│   │   ├── __init__.py
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py        # FastAPI: /predict, /health
│   │   │   ├── schemas.py     # Pydantic request/response models
│   │   │   └── security.py    # API key check
│   │   ├── config.py
│   │   ├── etl.py             # US-04, 05, 06
│   │   └── train.py           # trains + saves the model (US-25)
│   └── tests/
│       ├── test_smoke.py
│       ├── test_etl.py
│       └── test_api.py
├── data/
│   ├── raw/
│   └── processed/
├── models/                    # model.pkl, metrics.json (git-ignored, generated locally)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/
    ├── ci.yml                 # tests on push (main, DEV_Schama) and PRs
    └── cd.yml                 # build + push Docker image on push to main
```

### POC / MVP separation

- **POC** = the Jupyter notebook only (`notebooks/OpenHousing_POC_EN.ipynb`). No API, no Docker, no CI/CD at this phase — see `poc/README.md` and `BACKLOG_PRODUIT_v2.md`.
- **MVP** (`mvp/`) = the product version: automated ETL, FastAPI service, containerization, CI/CD, observability.

## Tech stack

- Python 3.11+
- FastAPI, Pydantic
- scikit-learn, pandas, joblib
- pytest
- Docker / Docker Compose

## Useful commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# 1. Run the ETL pipeline (fetch + clean + split -> data/processed/)
python -m open_housing_mvp.etl

# 2. Train the model and save it to models/ (needed before the API can predict)
python -m open_housing_mvp.train

# 3. Start the API
cp .env.example .env   # set your own API_KEY
uvicorn open_housing_mvp.app.main:app --reload

# Run tests
pytest

# Docker (also runs ETL/train once inside the container if models/ is empty — see below)
docker compose up --build
```

**Note on Docker + model artifacts**: `models/` and `data/processed/` are git-ignored (see `.gitignore`) — they are generated, not committed. `docker-compose.yml` mounts them as volumes, so `/health` will return `503` until you've run `python -m open_housing_mvp.train` at least once, either on the host or inside the running container:

```bash
docker compose exec api python -m open_housing_mvp.train
```

## Known limitations (documented, not hidden)

- **No confirmed accuracy threshold from the business** — the client said "I want it to be precise" with no number. The model in `train.py` is the one selected in the POC notebook (Gradient Boosting), not re-validated against a business-approved target.
- **Model selection is not re-compared in the MVP.** `train.py` trains only Gradient Boosting, consolidating the POC's comparison result rather than repeating it. No cross-validation or hyperparameter tuning is performed — acceptable for a course MVP under deadline, not for production.
- **The `b` (ethically problematic) feature is still in the model.** Not resolved with the business — see `BACKLOG_PRODUIT_v2.md`, "Out of Scope".
- **CD stops at pushing the Docker image to GHCR** — it does not deploy to a real cloud host, because no cloud account/credentials exist for this project. See the comment header in `.github/workflows/cd.yml`.
- **Scaling strategy (US-23, Low priority) is documented, not implemented**: given a real cloud target, the recommended approach is horizontal autoscaling on request latency/CPU, with the model loaded read-only per replica (no shared mutable state — `ml_models` is per-process). No autoscaling config exists yet because there is no cloud target to configure it for.
- **Rollback strategy (US-21)**: each image pushed by `cd.yml` is tagged `v<run_number>` in addition to `latest`. To roll back, redeploy the previous `v<run_number>` tag from the registry — there is no automated rollback trigger, this is a manual, documented procedure.

## Phase

- POC: technical validation of the model (notebook only).
- MVP: robustness, data validation, containerization, automation — in progress.
OPENHOUSING_EOF

cat > poc/README.md << 'OPENHOUSING_EOF'
# POC

Le POC est **uniquement** le notebook Jupyter : [`../notebooks/OpenHousing_POC_EN.ipynb`](../notebooks/OpenHousing_POC_EN.ipynb).

Objectif : prouver la faisabilité technique — ETL (chargement, nettoyage, EDA) et comparaison de 4 modèles de régression (Linear Regression, Ridge, Random Forest, Gradient Boosting) — sans API, sans Docker, sans CI/CD à ce stade. Voir `BACKLOG_PRODUIT_v2.md` pour le détail des user stories couvertes (US-01, 02, 03, 07, 08, 09) et la Definition of Done spécifique à la phase POC.

Ce dossier ne contient volontairement plus de code (`src/`, `tests/`) : l'ancien scaffold ici correspondait à une version antérieure du backlog où l'API faisait encore partie du scope POC. Depuis la correction du backlog, tout le code de production vit dans `mvp/`.
OPENHOUSING_EOF

cat > Dockerfile << 'OPENHOUSING_EOF'
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# curl is only needed for the docker-compose healthcheck (US-18)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY mvp/src ./mvp/src

RUN pip install --upgrade pip && pip install -e .

EXPOSE 8000

CMD ["uvicorn", "open_housing_mvp.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
OPENHOUSING_EOF

cat > docker-compose.yml << 'OPENHOUSING_EOF'
services:
  api:
    build: .
    container_name: openhousing-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
OPENHOUSING_EOF

cat > .github/workflows/ci.yml << 'OPENHOUSING_EOF'
name: CI

on:
  push:
    branches: [main, DEV_Schama]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
      - name: Run tests
        run: pytest -q
OPENHOUSING_EOF

cat > .github/workflows/cd.yml << 'OPENHOUSING_EOF'
name: CD

# CD ne se déclenche que sur `main` (pas sur DEV_Schama) : la branche de dev
# fait tourner la CI seule, `main` déclenche la publication de l'image.
#
# LIMITE ASSUMÉE (US-20/US-21) : ce workflow build + push l'image Docker vers
# GitHub Container Registry (ghcr.io), taguée `v<run_number>` pour permettre
# un rollback (US-21 : redéployer le tag précédent). Il ne va PAS jusqu'au
# déploiement sur un hébergeur cloud réel (Render/Railway/AWS/etc.) car
# aucun compte cloud ni secret d'accès n'a été fourni pour ce projet. Ajouter
# une étape de déploiement ici dès que la cible d'hébergement est choisie.

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:v${{ github.run_number }}
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/__init__.py << 'OPENHOUSING_EOF'

OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/config.py << 'OPENHOUSING_EOF'
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
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/etl.py << 'OPENHOUSING_EOF'
"""Pipeline ETL du MVP (US-04, US-05, US-06).

Reprend la logique validée dans le notebook POC, sous forme de script
exécutable et testable :
- US-04 : pipeline unique déclenchable en CLI (`python -m open_housing_mvp.etl`)
- US-05 : validation du schéma des 13 features, échec explicite sinon
- US-06 : split train/test reproductible (random_state=42), versionné dans data/processed/
"""

from __future__ import annotations

import logging
from pathlib import Path

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
        df = pd.read_csv(data_url)
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
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/train.py << 'OPENHOUSING_EOF'
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
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/app/__init__.py << 'OPENHOUSING_EOF'

OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/app/main.py << 'OPENHOUSING_EOF'
"""Point d'entrée API du MVP (US-10, 11, 12, 13, 14, 15, 24)."""

from __future__ import annotations

import json
import logging
import time
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status

from .. import config
from .schemas import HealthResponse, HouseFeatures, PredictionResponse
from .security import verify_api_key

logger = logging.getLogger("open_housing_mvp.api")
logging.basicConfig(level=logging.INFO)

ml_models: dict = {"model": None, "features": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ml_models["model"] = joblib.load(config.MODEL_PATH)
        ml_models["features"] = joblib.load(config.FEATURES_PATH)
        logger.info("Modèle chargé depuis %s", config.MODEL_PATH)
    except FileNotFoundError:
        ml_models["model"] = None
        ml_models["features"] = None
        logger.warning(
            "Aucun modèle trouvé à %s — /predict et /health renverront 503 tant que "
            "`python -m open_housing_mvp.train` n'a pas été exécuté.",
            config.MODEL_PATH,
        )
    yield
    ml_models["model"] = None
    ml_models["features"] = None


app = FastAPI(title="Open Housing MVP", lifespan=lifespan)


@app.middleware("http")
async def log_predict_requests(request: Request, call_next):
    """US-24 : logging JSON de chaque requête /predict (entrée, sortie, durée)."""
    body_bytes = await request.body()

    async def receive():
        return {"type": "http.request", "body": body_bytes}

    request._receive = receive  # noqa: SLF001 — nécessaire pour relire le body après l'avoir consommé

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    if request.url.path == "/predict":
        try:
            input_payload = json.loads(body_bytes) if body_bytes else None
        except json.JSONDecodeError:
            input_payload = None
        logger.info(json.dumps({
            "timestamp": time.time(),
            "path": request.url.path,
            "input": input_payload,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        }))
    return response


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Open Housing MVP API"}


@app.get("/health", response_model=HealthResponse)
def health(response: Response) -> HealthResponse:
    """US-12 : 200 si le modèle est chargé, 503 sinon."""
    model_loaded = ml_models.get("model") is not None
    if not model_loaded:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status="ok" if model_loaded else "unavailable", model_loaded=model_loaded)


@app.post("/predict", response_model=PredictionResponse, dependencies=[Depends(verify_api_key)])
def predict(features: HouseFeatures) -> PredictionResponse:
    """US-10 (predict), US-13 (validation Pydantic automatique -> 422), US-14 (erreurs), US-15 (clé API)."""
    model = ml_models.get("model")
    feature_order = ml_models.get("features")

    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle non chargé — lancez `python -m open_housing_mvp.train` avant d'appeler /predict",
        )

    try:
        row = pd.DataFrame([features.model_dump()])[feature_order]
        predicted_price = float(model.predict(row)[0])
    except Exception as exc:  # noqa: BLE001 — on renvoie un 500 explicite plutôt qu'un crash silencieux
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prédiction : {exc}",
        ) from exc

    return PredictionResponse(predicted_price=predicted_price)
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/app/schemas.py << 'OPENHOUSING_EOF'
"""Schémas Pydantic de l'API MVP (US-13)."""

from pydantic import BaseModel, ConfigDict, Field


class HouseFeatures(BaseModel):
    crim: float = Field(..., description="Taux de criminalité par habitant")
    zn: float = Field(..., description="Proportion de terrain résidentiel zoné grandes parcelles")
    indus: float = Field(..., description="Proportion d'acres commerciaux non liés au détail")
    chas: int = Field(..., ge=0, le=1, description="Bordure de la rivière Charles (1) ou non (0)")
    nox: float = Field(..., description="Concentration en oxydes d'azote")
    rm: float = Field(..., gt=0, description="Nombre moyen de pièces par logement")
    age: float = Field(..., ge=0, description="Proportion de logements occupés construits avant 1940")
    dis: float = Field(..., gt=0, description="Distance pondérée aux centres d'emploi")
    rad: float = Field(..., description="Indice d'accessibilité aux autoroutes radiales")
    tax: float = Field(..., description="Taux de taxe foncière")
    ptratio: float = Field(..., description="Ratio élèves/enseignant")
    b: float = Field(
        ...,
        description=(
            "Variable socio-démographique du dataset d'origine — limite éthique connue, "
            "non arbitrée avec le business (voir BACKLOG_PRODUIT_v2.md)"
        ),
    )
    lstat: float = Field(..., description="Pourcentage de population à statut socio-économique inférieur")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "crim": 0.00632, "zn": 18.0, "indus": 2.31, "chas": 0, "nox": 0.538,
                "rm": 6.575, "age": 65.2, "dis": 4.09, "rad": 1, "tax": 296,
                "ptratio": 15.3, "b": 396.9, "lstat": 4.98,
            }
        }
    )


class PredictionResponse(BaseModel):
    predicted_price: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
OPENHOUSING_EOF

cat > mvp/src/open_housing_mvp/app/security.py << 'OPENHOUSING_EOF'
"""Sécurité API par clé (US-15)."""

import os

from fastapi import Header, HTTPException, status

from .. import config


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = os.environ.get(config.API_KEY_ENV_VAR, "change-me")
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API invalide ou manquante (en-tête X-API-Key requis)",
        )
OPENHOUSING_EOF

cat > mvp/tests/test_smoke.py << 'OPENHOUSING_EOF'
def test_mvp_smoke() -> None:
    assert True
OPENHOUSING_EOF

cat > mvp/tests/test_etl.py << 'OPENHOUSING_EOF'
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
OPENHOUSING_EOF

cat > mvp/tests/test_api.py << 'OPENHOUSING_EOF'
"""Tests de l'API MVP (US-10 à 15)."""

import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor

from open_housing_mvp.app.main import app, ml_models

FEATURES = [
    "crim", "zn", "indus", "chas", "nox", "rm", "age",
    "dis", "rad", "tax", "ptratio", "b", "lstat",
]

VALID_PAYLOAD = {
    "crim": 0.00632, "zn": 18.0, "indus": 2.31, "chas": 0, "nox": 0.538,
    "rm": 6.575, "age": 65.2, "dis": 4.09, "rad": 1, "tax": 296,
    "ptratio": 15.3, "b": 396.9, "lstat": 4.98,
}


@pytest.fixture(autouse=True)
def _fake_model(monkeypatch):
    """Injecte un faux modèle pour ne pas dépendre d'un entraînement réel en CI."""
    model = DummyRegressor(strategy="constant", constant=250000.0)
    model.fit([[0] * len(FEATURES)], [250000.0])
    ml_models["model"] = model
    ml_models["features"] = FEATURES
    monkeypatch.setenv("API_KEY", "test-key")
    yield
    ml_models["model"] = None
    ml_models["features"] = None


client = TestClient(app)


def test_health_ok_when_model_loaded():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_health_unavailable_when_model_missing():
    ml_models["model"] = None
    response = client.get("/health")
    assert response.status_code == 503


def test_predict_requires_api_key():
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_predict_rejects_wrong_api_key():
    response = client.post("/predict", json=VALID_PAYLOAD, headers={"x-api-key": "wrong"})
    assert response.status_code == 401


def test_predict_with_valid_key_returns_price():
    response = client.post("/predict", json=VALID_PAYLOAD, headers={"x-api-key": "test-key"})
    assert response.status_code == 200
    assert "predicted_price" in response.json()


def test_predict_invalid_payload_returns_422():
    bad_payload = dict(VALID_PAYLOAD)
    del bad_payload["rm"]
    response = client.post("/predict", json=bad_payload, headers={"x-api-key": "test-key"})
    assert response.status_code == 422


def test_predict_returns_503_when_model_not_loaded():
    ml_models["model"] = None
    response = client.post("/predict", json=VALID_PAYLOAD, headers={"x-api-key": "test-key"})
    assert response.status_code == 503
OPENHOUSING_EOF

echo "All files written."