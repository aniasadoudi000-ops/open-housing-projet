from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from open_housing.config import MODEL_PATH


class PredictRequest(BaseModel):
    CRIM: float = Field(..., description="Per-capita crime rate by town")
    ZN: float = Field(..., description="Proportion of residential land zoned for lots over 25k sq.ft")
    INDUS: float = Field(..., description="Proportion of non-retail business acres per town")
    CHAS: float = Field(..., description="Charles River dummy variable")
    NOX: float = Field(..., description="Nitric oxides concentration")
    RM: float = Field(..., description="Average number of rooms per dwelling")
    AGE: float = Field(..., description="Proportion of owner-occupied units built prior to 1940")
    DIS: float = Field(..., description="Weighted mean of distances to five Boston employment centers")
    RAD: float = Field(..., description="Index of accessibility to radial highways")
    TAX: float = Field(..., description="Full-value property-tax rate per $10,000")
    PTRATIO: float = Field(..., description="Pupil-teacher ratio by town")
    B: float = Field(..., description="Proportion of Black residents by town")
    LSTAT: float = Field(..., description="Lower status of the population")


class PredictResponse(BaseModel):
    predicted_price: float


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_loaded = MODEL_PATH.exists()
    yield


app = FastAPI(title="OpenHousing API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, bool | str]:
    model_loaded = MODEL_PATH.exists()
    status_code = 200 if model_loaded else 503
    return {"status": "ok" if model_loaded else "error", "model_loaded": model_loaded}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if not MODEL_PATH.exists():
        raise RuntimeError("Model is not available yet")
    return PredictResponse(predicted_price=0.0)
