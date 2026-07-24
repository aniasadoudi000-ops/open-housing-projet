# OpenHousing

Proof-of-concept and MVP project for estimating real estate prices from the Boston Housing dataset.

## Objective

This project aims to:
- prepare data through an ETL pipeline,
- train a regression model,
- expose a REST API with FastAPI,
- package the application in Docker,
- prepare CI/CD automation and cloud deployment.

## Global Data Flow Architecture

```mermaid
flowchart TD
    subgraph SOURCE["📦 Data Source"]
        A["🌐 GitHub CSV\nBoston Housing\n(506 rows × 14 cols)"]
    end

    subgraph ETL["⚙️ ETL Pipeline — src/etl.py"]
        B["Extract\npandas.read_csv(url)"]
        C["Validate\n13 features present\nno nulls / correct types"]
        D["Transform\nCast to float64\nHandle missing values"]
        E["Split\ntrain 80% / test 20%\nrandom_state=42"]
        F["Load\ndata/processed/\ntrain.csv + test.csv\n+ metadata.json"]
    end

    subgraph TRAIN["🧠 Training Pipeline — src/train.py"]
        G["Load\ntrain.csv"]
        H["Scale\nStandardScaler\n(fit on train only)"]
        I["Train\nRandomForestRegressor\nrandom_state=42"]
        J["Evaluate\nR² / RMSE / MAE\non test.csv"]
        K["Save\nmodels/model.pkl\nmodels/metrics.json"]
    end

    subgraph API["🚀 REST API — src/open_housing/app/main.py"]
        L["Startup\nLoad model.pkl into memory"]
        M["GET /health\n→ 200 OK\n{status, model_loaded}"]
        N["POST /predict\nAccept JSON\n13 house features"]
        O["Pydantic\nInput Validation\nHTTP 422 if invalid"]
        P["Predict\npipeline.predict(input)"]
        Q["Response\n{predicted_price: float}\nin USD"]
    end

    subgraph INFRA["🐳 Infrastructure"]
        R["Docker\nDockerfile\ndocker-compose.yml"]
        S["CI/CD\nGitHub Actions\nci.yml + cd.yml"]
        T["☁️ Cloud\nAzure / Render\nLive endpoint"]
    end

    subgraph USER["👤 Client — OpenHousing"]
        U["Daily Use\nSend house features\nGet predicted price"]
    end

    A --> B
    B --> C --> D --> E --> F
    F --> G
    G --> H --> I --> J --> K

    K --> L
    L --> M
    L --> N
    N --> O --> P --> Q

    Q --> U
    U --> N

    TRAIN --> R
    API --> R
    R --> S --> T
    T --> U

    style SOURCE fill:#e3f2fd,stroke:#1565c0
    style ETL fill:#f3e5f5,stroke:#6a1b9a
    style TRAIN fill:#e8f5e9,stroke:#2e7d32
    style API fill:#fff3e0,stroke:#e65100
    style INFRA fill:#fce4ec,stroke:#880e4f
    style USER fill:#f1f8e9,stroke:#558b2f
```

### Two distinct flows

| Flow | Frequency | Steps |
|---|---|---|
| **Offline** (training) | Once, or re-run when data changes | Source → ETL → Training → `model.pkl` |
| **Online** (inference) | Daily | Client → `POST /predict` → API → predicted price in USD |

---

## Project Structure

```text
open-housing-projet/
├── poc/
│   ├── README.md
│   ├── src/open_housing_poc/
│   │   ├── __init__.py
│   │   ├── app/main.py
│   │   ├── config.py
│   │   ├── etl.py
│   │   └── train.py
│   └── tests/test_smoke.py
├── mvp/
│   ├── README.md
│   ├── src/open_housing_mvp/
│   │   ├── __init__.py
│   │   ├── app/main.py
│   │   ├── config.py
│   │   ├── etl.py
│   │   └── train.py
│   └── tests/test_smoke.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── notebooks/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/ci.yml
```

### POC / MVP separation

- The [poc/README.md](poc/README.md) folder contains the proof-of-concept skeleton.
- The [mvp/README.md](mvp/README.md) folder contains the product-version skeleton.
- At the beginning, both subprojects share the same type of structure, but they are now separated so they can evolve independently.

## Tech stack

- Python 3.11+
- FastAPI
- Pydantic
- scikit-learn
- pandas
- joblib
- pytest
- Docker / Docker Compose

## Useful commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.open_housing.app.main:app --reload
pytest
```

## Phase

- POC: technical validation of the model and the API.
- MVP: robustness, data validation, containerization, and automation.
