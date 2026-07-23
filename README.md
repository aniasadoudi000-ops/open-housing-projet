# OpenHousing

Projet de preuve de concept et MVP pour l'estimation de prix immobiliers à partir du dataset Boston Housing.

## Objectif

Ce projet vise à :
- préparer les données via un pipeline ETL,
- entraîner un modèle de régression,
- exposer une API REST avec FastAPI,
- empaqueter l'application en Docker,
- préparer l'automatisation CI/CD et le déploiement cloud.

## Architecture proposée

```text
open-housing-projet/
├── src/open_housing/
│   ├── __init__.py
│   ├── app/
│   │   └── main.py
│   ├── etl.py
│   ├── train.py
│   └── config.py
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── tests/
├── notebooks/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── .github/workflows/ci.yml
```

## Stack technique

- Python 3.11+
- FastAPI
- Pydantic
- scikit-learn
- pandas
- joblib
- pytest
- Docker / Docker Compose

## Commandes utiles

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.open_housing.app.main:app --reload
pytest
```

## Phase

- POC : validation technique du modèle et de l'API.
- MVP : robustesse, validation des données, conteneurisation et automatisation.
