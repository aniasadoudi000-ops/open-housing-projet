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
