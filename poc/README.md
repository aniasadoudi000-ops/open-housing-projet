# POC

Le POC est **uniquement** le notebook Jupyter : [`../notebooks/OpenHousing_POC_EN.ipynb`](../notebooks/OpenHousing_POC_EN.ipynb).

Objectif : prouver la faisabilité technique — ETL (chargement, nettoyage, EDA) et comparaison de 4 modèles de régression (Linear Regression, Ridge, Random Forest, Gradient Boosting) — sans API, sans Docker, sans CI/CD à ce stade. Voir `BACKLOG_PRODUIT_v2.md` pour le détail des user stories couvertes (US-01, 02, 03, 07, 08, 09) et la Definition of Done spécifique à la phase POC.

Ce dossier ne contient volontairement plus de code (`src/`, `tests/`) : l'ancien scaffold ici correspondait à une version antérieure du backlog où l'API faisait encore partie du scope POC. Depuis la correction du backlog, tout le code de production vit dans `mvp/`.
