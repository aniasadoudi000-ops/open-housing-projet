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
