from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from open_housing.config import METRICS_PATH, MODEL_PATH, TEST_DATA_PATH, TRAIN_DATA_PATH


def train_model() -> Pipeline:
    """Train a baseline regression pipeline and save artifacts."""
    train_df = __import__("pandas").read_csv(TRAIN_DATA_PATH)
    test_df = __import__("pandas").read_csv(TEST_DATA_PATH)

    X_train = train_df.drop(columns=["MEDV"])
    y_train = train_df["MEDV"]
    X_test = test_df.drop(columns=["MEDV"])
    y_test = test_df["MEDV"]

    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", RandomForestRegressor(n_estimators=200, random_state=42)),
        ]
    )

    pipeline.fit(X_train, y_train)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    metrics = {
        "r2": float(pipeline.score(X_test, y_test)),
        "rmse": float(__import__("numpy").sqrt(__import__("sklearn.metrics").metrics.mean_squared_error(y_test, pipeline.predict(X_test)))),
        "mae": float(__import__("sklearn.metrics").metrics.mean_absolute_error(y_test, pipeline.predict(X_test))),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))
    return pipeline
