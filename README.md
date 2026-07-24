# MVP

Version produit d'OpenHousing : ETL automatisé, entraînement, API FastAPI, containerisation, CI/CD, observabilité.

## Structure

```text
mvp/
├── src/open_housing_mvp/
│   ├── app/
│   │   ├── main.py      # FastAPI : GET /, GET /health, GET /metrics, POST /predict
│   │   ├── schemas.py   # modèles Pydantic (requête/réponse)
│   │   └── security.py  # vérification de la clé API (en-tête X-API-Key)
│   ├── config.py         # chemins, variables d'environnement
│   ├── etl.py             # US-04, 05, 06
│   └── train.py           # entraîne le modèle retenu en POC, sauvegarde artefacts + métriques
└── tests/
    ├── test_etl.py
    └── test_api.py
```

## Endpoints

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/health` | 200 si le modèle est chargé, 503 sinon | non |
| GET | `/metrics` | Dernières métriques d'entraînement (RMSE, MAE, R², `trained_at`) | non |
| POST | `/predict` | Prédit un prix à partir des 13 features | oui (`X-API-Key`) |

Doc interactive : `http://localhost:8000/docs` une fois le serveur lancé.

## Lancer en local

```bash
pip install -e .
python -m open_housing_mvp.etl
python -m open_housing_mvp.train
cp .env.example .env   # définis ton propre API_KEY
uvicorn open_housing_mvp.app.main:app --reload
```

## Lancer avec Docker

```bash
cp .env.example .env
docker compose up --build
```

`models/` et `data/` sont montés en volume : si `models/model.pkl` n'existe pas encore côté hôte, `/health` renverra 503 jusqu'à ce que tu lances l'entraînement (en local ou dans le conteneur : `docker compose exec api python -m open_housing_mvp.train`).

## Rollback (US-21)

Chaque image publiée par `.github/workflows/cd.yml` (déclenché sur push vers `main`) est taguée `ghcr.io/<repo>:v<run_number>` en plus de `:latest`. Pour revenir en arrière, redéployer manuellement le tag `v<N>` précédent — voir la liste des versions dans l'onglet **Packages** du repo GitHub.

## Limites assumées

Voir la section "Known limitations" du `README.md` à la racine du projet — notamment : pas de seuil de précision confirmé par le business, pas de re-comparaison des 4 modèles (Gradient Boosting est repris tel quel depuis la POC), pas de déploiement cloud réel (le CD s'arrête à la publication de l'image).
