# Product Backlog — OpenHousing
**Housing Observatory — Real Estate Price Estimation (USD) — POC & MVP**  
**Date:** 2026-07-23 | **Client:** OpenHousing (single internal user) | **Source:** SME Interview + Technical Review

**POC scope = the Jupyter notebook only** (ETL + ML: data ingestion, cleaning, EDA, model training, evaluation, artifact saving). No API, Docker, CI/CD, or Observability story belongs to the POC phase — those workstreams only exist to turn the proven notebook logic into a usable product for the MVP. If it isn't executed inside the notebook, it isn't POC.

Project management / cadrage is intentionally **not** tracked as a backlog epic, per instructor guidance — it is handled separately (meeting notes, roles, sprint planning).

---

## Context & Constraints (from SME Interview)

| Item | Detail |
|---|---|
| User | 1 internal user (the client) |
| Usage frequency | Daily |
| Existing solution | None — built from scratch |
| Interface | FastAPI (client requirement) |
| Dashboard / BI | Not needed |
| Data | Boston Housing socioeconomic dataset |
| Success criteria | Client said "I want my model to be precise" — **no numeric accuracy target was given.** No RMSE/R² threshold is confirmed by the business. Any number in this backlog (e.g. an R² target) is an internal engineering assumption, not a client requirement, and must be validated with the business before being treated as a gate. |
| Response time | Client said "fast response time" — **no numeric SLA was given.** Same caveat as above applies to any latency figure below. |
| Business risk | Wrong prediction = wrong house pricing = lost clients & lost profit |
| Regulatory constraints | None stated — not yet explicitly checked against the dataset's known ethical issue (the `black` feature); to confirm separately from "regulatory" |

---

## Epics

| ID | Epic | Description |
|---|---|---|
| E1 | ETL — Data Pipeline | Acquire, clean and prepare the Boston Housing dataset |
| E2 | ML — Prediction Model | Train, evaluate and save a price prediction model |
| E3 | API — REST Service | Expose the model via a FastAPI interface |
| E4 | Containerization | Package the API and model in Docker |
| E5 | CI/CD & Cloud Deployment | Automate testing, deployment and rollback |
| E6 | Observability | Track prediction accuracy, speed and request logs |

---

## E1 — ETL — Data Pipeline
Ingestion, cleaning and preparation of the Boston Housing dataset.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-01 | Fetch the Boston Housing CSV from the remote URL | POC | Highest | Dataset downloaded from GitHub URL and loaded in the notebook |
| US-02 | Clean the raw data | POC | High | Missing values handled, all columns cast to `float64`, no nulls in output |
| US-03 | Perform Exploratory Data Analysis (EDA) | POC | Medium | Distributions, correlations and target variable analysed and documented in the POC notebook |
| US-04 | Automate the full ETL pipeline | MVP | High | Single script `src/etl.py` runs all steps end-to-end; can be triggered from CLI |
| US-05 | Validate input data quality | MVP | High | All 13 feature columns present and schema-validated at runtime; script fails loudly if not |
| US-06 | Version the transformed data | MVP | Medium | Train/test CSVs saved to `data/processed/` with `random_state=42`; split is reproducible |

---

## E2 — ML — Prediction Model
Training, evaluation and saving of the price prediction model, entirely inside the POC notebook.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-07 | Train and compare a baseline model against an advanced model | POC | Highest | A `LinearRegression` baseline **and** a `RandomForestRegressor` are both trained on the processed data and compared on the test set. No accuracy threshold is enforced as a hard gate (none was given by the business) — the model with the lower RMSE is retained, and both results are documented in the notebook. |
| US-08 | Evaluate the model (RMSE / MAE / R²) | POC | Highest | RMSE, MAE, R² printed in the notebook and saved to `models/metrics.json` with a timestamp, for both models compared |
| US-09 | Save the trained model | POC | High | Best model serialized to `models/model.pkl` via `joblib`; loadable in a fresh process. *(MVP follow-up: wrap in a full `Pipeline` with a scaler once the API needs it — not required for the POC notebook itself.)* |

---

## E3 — API — REST Service (FastAPI)
Exposing the model through a FastAPI REST interface. Entirely MVP: nothing here runs inside the POC notebook.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-10 | Create the `POST /predict` endpoint | MVP | Highest | Accepts 13-feature JSON; returns `{"predicted_price": float}` in USD. Response-time target is an internal engineering goal (e.g. sub-second), **not a confirmed client SLA** — flag before treating it as a requirement. |
| US-11 | Test the endpoint via Swagger / Postman | MVP | Medium | Swagger UI accessible at `/docs`; sample request returns a valid predicted price |
| US-12 | Create the `GET /health` endpoint | MVP | High | Returns `{"status": "ok", "model_loaded": true}` with HTTP 200; HTTP 503 if model not loaded |
| US-13 | Validate inputs with Pydantic schemas | MVP | High | Missing or invalid fields return HTTP 422 with a descriptive error message |
| US-14 | Handle errors with explicit HTTP status codes | MVP | High | HTTP 422 for bad input, HTTP 500 for server error, HTTP 503 if model unavailable |
| US-15 | Secure the API (API key / authentication) | MVP | High | Requests without a valid API key return HTTP 401; key configured via environment variable |

---

## E4 — Containerization — Docker
Packaging the API and model as portable containers. Entirely MVP.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-16 | Write a basic Dockerfile for the API | MVP | Medium | `docker build` and `docker run` succeed; API accessible on `localhost:8000` |
| US-17 | Optimise the Docker image | MVP | Medium | Image size ≤ 500MB; `.dockerignore` excludes `poc/`, `data/raw/`, `tests/`; startup ≤ 10s |
| US-18 | Create a full `docker-compose` setup | MVP | Medium | `docker-compose up` starts all services; `/health` returns 200 |

---

## E5 — CI/CD — Cloud Deployment
Continuous integration, continuous deployment and rollback capability. Entirely MVP.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-19 | Set up a CI pipeline (tests + lint) | MVP | High | GitHub Actions runs on every push to `main`; pipeline fails if any test fails |
| US-20 | Set up a CD pipeline to the cloud | MVP | High | Docker image pushed to registry and deployed to cloud after CI passes |
| US-21 | Define a rollback strategy | MVP | Medium | Images tagged `v<run_number>`; rollback to previous version documented in `README.md` |
| US-22 | Configure monitoring and logging | MVP | Medium | Request timing and prediction logs written to stdout in JSON. A latency target (e.g. sub-500ms average) is an internal goal, **not a confirmed client SLA**. |
| US-23 | Define a scaling strategy | MVP | Low | Auto-scaling rules defined in cloud config; documented in runbook |

---

## E6 — Observability
Tracking prediction accuracy, speed and request history. Entirely MVP.

| ID | User Story | Phase | Priority | Acceptance Criteria |
|---|---|---|---|---|
| US-24 | Log each prediction request (input + output + timestamp) | MVP | Medium | Every `/predict` call logged as JSON to stdout: `{timestamp, input, predicted_price, duration_ms}` |
| US-25 | Expose model performance metrics after training | MVP | Medium | `models/metrics.json` updated on each training run with R², RMSE, MAE and `trained_at` timestamp |

---

## Summary

| Phase | Stories |
|---|---|
| POC | US-01, US-02, US-03, US-07, US-08, US-09 |
| MVP | US-04, US-05, US-06, US-10, US-11, US-12, US-13, US-14, US-15, US-16, US-17, US-18, US-19, US-20, US-21, US-22, US-23, US-24, US-25 |
| **Total** | **25 stories** |

---

## Priority Legend

| Priority | Description |
|---|---|
| Highest | Blocking — the project cannot move forward without this story |
| High | Critical for the phase — mandatory delivery |
| Medium | Important but not blocking |
| Low | Future improvement |

---

## Definition of Done — POC (US-01, 02, 03, 07, 08, 09)

A POC story is **Done** when:
1. Code exists and runs top-to-bottom in the Jupyter notebook without error
2. The relevant output (cleaned data, EDA chart, trained model, metrics, or saved artifact) is visible in the notebook's cell outputs
3. Any assumption made (data cleaning choice, model choice, threshold) is documented in a markdown cell

No cloud, Docker, or CI/CD requirement applies to POC stories — that infrastructure doesn't exist yet at this phase.

## Definition of Done — MVP (all other stories)

An MVP story is **Done** when:
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
- No regulatory compliance requirements *(caveat: this was a general question — the dataset's `black` feature was not specifically raised with the client; worth a dedicated follow-up before treating it as cleared)*
