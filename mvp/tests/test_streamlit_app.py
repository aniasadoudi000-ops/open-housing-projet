"""Smoke tests for the Streamlit frontend MVP surface."""

from open_housing_mvp.streamlit_app import DEFAULT_API_URL, build_prediction_payload

FEATURES = [
    "crim", "zn", "indus", "chas", "nox", "rm", "age",
    "dis", "rad", "tax", "ptratio", "b", "lstat",
]


def test_default_api_url_is_configured() -> None:
    assert DEFAULT_API_URL == "http://localhost:8000"


def test_build_prediction_payload_contains_all_expected_features() -> None:
    payload = build_prediction_payload(**{feature: 1.0 for feature in FEATURES})
    assert set(payload) == set(FEATURES)
