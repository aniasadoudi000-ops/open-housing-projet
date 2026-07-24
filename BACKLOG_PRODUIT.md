# Product Backlog — OpenHousing
**Housing Observatory — Real Estate Price Estimation (USD) — POC & MVP**  
**Date:** 2026-07-23 | **Client:** OpenHousing (single internal user) | **Source:** SME Interview + Technical Review

This backlog covers all 6 workstreams of the project (ETL, Machine Learning, REST API, Containerization, CI/CD & Cloud, Observability). Each user story is assigned to a phase: **POC** (proof of technical feasibility) or **MVP** (production-ready version for the client). No CI/CD stories belong to the POC phase — that phase exists solely to validate that the model predicts a price with acceptable accuracy.

---

## Context & Constraints (from SME Interview)

| Item | Detail |
|---|---|
| User | 1 internal user (the client) |
| Usage frequency | Daily |
| Existing solution | None — built from scratch |
| Interface | FastAPI + Streamlit frontend (client requirement) |
| Dashboard / BI | Light manual dashboard UI for demo / local validation |
| Data | Boston Housing socioeconomic dataset |
| Success criteria | Accurate price prediction + fast response time |
| Business risk | Wrong prediction = wrong house pricing = lost clients & lost profit |
| Regulatory constraints | None |

---

## Epics

| ID | Epic | Description |
|---|---|---|
| E1 | ETL — Data Pipeline | Acquire, clean and prepare the Boston Housing dataset |
| E2 | ML — Prediction Model | Train, evaluate and save a price prediction model |
| E3 | API — REST Service | Expose the model via a FastAPI interface |
| E4 | Containerization | Package the API and model in Docker |√
| E5 | Frontend — Streamlit UI | Provide a lightweight UI to submit house features and display a prediction |
| E6 | CI/CD & Cloud Deployment | Automate testing, deployment and rollback |
| E7 | Observability | Track prediction accuracy, speed and request logs |

---

## E1 — ETL — Data Pipeline
Ingestion, cleaning and preparation of the Boston Housing dataset.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-07 | Fetch the Boston Housing CSV from the remote URL | POC | Highest | 1 | Dataset downloaded from GitHub URL and saved to `data/raw/`; script is idempotent |
| US-08 | Clean the raw data | POC | High | 2 | Missing values handled, all columns cast to `float64`, no nulls in output |
| US-09 | Perform Exploratory Data Analysis (EDA) | POC | Medium | 2 | Distributions, correlations and target variable analysed and documented in POC notebook |
| US-10 | Automate the full ETL pipeline | MVP | High | 5 | Single script `src/etl.py` runs all steps end-to-end; can be triggered from CLI |
| US-11 | Validate input data quality | MVP | High | 3 | All 13 feature columns present and schema-validated at runtime; script fails loudly if not |
| US-12 | Version the transformed data | MVP | Medium | 3 | Train/test CSVs saved to `data/processed/` with `random_state=42`; split is reproducible |

---

## E2 — ML — Prediction Model
Training, evaluation and versioning of the price prediction model.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-13 | Train a baseline regression model | POC | Highest | 3 | `RandomForestRegressor` trained on processed data; R² ≥ 0.80 on test set (hard gate) |
| US-14 | Evaluate the model (RMSE / MAE / R²) | POC | Highest | 2 | RMSE, MAE, R² printed to stdout and saved to `models/metrics.json` with timestamp |
| US-15 | Save the trained model | POC | High | 1 | Full `Pipeline` (scaler + model) serialized to `models/model.pkl` via `joblib`; loadable in a fresh process |

---

## E3 — API — REST Service (FastAPI)
Exposing the model through a FastAPI REST interface.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-19 | Create the `POST /predict` endpoint | POC | Highest | 3 | Accepts 13-feature JSON; returns `{"predicted_price": float}` in USD in < 1 second |
| US-20 | Test the endpoint via Swagger / Postman | POC | Medium | 1 | Swagger UI accessible at `/docs`; sample request returns a valid predicted price |
| US-16 | Create the `GET /health` endpoint | POC | High | 1 | Returns `{"status": "ok", "model_loaded": true}` with HTTP 200; HTTP 503 if model not loaded |
| US-21 | Validate inputs with Pydantic schemas | MVP | High | 3 | Missing or invalid fields return HTTP 422 with a descriptive error message |
| US-22 | Handle errors with explicit HTTP status codes | MVP | High | 2 | HTTP 422 for bad input, HTTP 500 for server error, HTTP 503 if model unavailable |
| US-23 | Secure the API (API key / authentication) | MVP | High | 3 | Requests without a valid API key return HTTP 401; key configured via environment variable |

---

## E4 — Containerization — Docker
Packaging the API and model as portable containers.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-25 | Write a basic Dockerfile for the API | POC | Medium | 2 | `docker build` and `docker run` succeed; API accessible on `localhost:8000` |
| US-26 | Optimise the Docker image | MVP | Medium | 3 | Image size ≤ 500MB; `.dockerignore` excludes `poc/`, `data/raw/`, `tests/`; startup ≤ 10s |
| US-27 | Create a full `docker-compose` setup | MVP | Medium | 2 | `docker-compose up` starts all services; `/health` returns 200 |

---

## E5 — Frontend — Streamlit UI
Provide a lightweight UI for demo and manual prediction.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-34 | Create a Streamlit form for all 13 Boston Housing features | MVP | High | 3 | UI renders on `localhost:8501` with a numeric input for each feature |
| US-35 | Send Streamlit form data to the FastAPI `/predict` endpoint | MVP | High | 3 | Valid payload is posted with the API key and the response is displayed in the UI |
| US-36 | Display a clear user-facing error on frontend failures | MVP | Medium | 2 | Connection or validation errors are shown without crashing the app |

---

## E6 — CI/CD — Cloud Deployment
Continuous integration, continuous deployment and rollback capability.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-28 | Set up a CI pipeline (tests + lint) | MVP | High | 5 | GitHub Actions runs on every push to `main`; pipeline fails if any test fails |
| US-29 | Set up a CD pipeline to the cloud | MVP | High | 5 | Docker image pushed to registry and deployed to cloud after CI passes |
| US-24 | Define a rollback strategy | MVP | Medium | 2 | Images tagged `v<run_number>`; rollback to previous version documented in `README.md` |
| US-30 | Configure monitoring and logging | MVP | Medium | 5 | Request timing and prediction logs written to stdout in JSON; average response < 500ms |
| US-31 | Define a scaling strategy | MVP | Low | 3 | Auto-scaling rules defined in cloud config; documented in runbook |

---

## E7 — Observability
Tracking prediction accuracy, speed and request history.

| ID | User Story | Phase | Priority | Points | Acceptance Criteria |
|---|---|---|---|---|---|
| US-32 | Log each prediction request (input + output + timestamp) | MVP | Medium | 2 | Every `/predict` call logged as JSON to stdout: `{timestamp, input, predicted_price, duration_ms}` |
| US-33 | Expose model performance metrics after training | MVP | Medium | 1 | `models/metrics.json` updated on each training run with R², RMSE, MAE and `trained_at` timestamp |

---

## Summary

| Phase | Stories | Total Points |
|---|---|---|
| POC | US-07, US-08, US-09, US-13, US-14, US-15, US-16, US-19, US-20, US-25 | 18 |
| MVP | US-10, US-11, US-12, US-21, US-22, US-23, US-24, US-26, US-27, US-28, US-29, US-30, US-31, US-32, US-33, US-34, US-35, US-36 | 56 |
| **Total** | **28 stories** | **74 points** |

---

## Priority Legend

| Priority | Description |
|---|---|
| Highest | Blocking — the project cannot move forward without this story |
| High | Critical for the phase — mandatory delivery |
| Medium | Important but not blocking |
| Low | Future improvement |

---

## Definition of Done (applies to all stories)

A story is considered **Done** when:
1. Code written and committed on a feature branch
2. Automated tests cover the feature
3. Feature works inside the Docker container
4. CI pipeline passes on push to `main`
5. Feature is accessible on the deployed cloud endpoint

---

## Out of Scope (confirmed by client)

- No PowerBI or visualisation dashboard
- No multi-user access (single user only)
- No support for other datasets (for now)
- No regulatory compliance requirements
