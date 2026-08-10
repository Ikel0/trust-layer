# Trust Layer

Trust Layer est un contrôle qualité de données utilisable localement : l’application analyse un CSV et rend visibles les erreurs avant qu’elles n’alimentent un reporting ou une décision.

## Ce qui fonctionne

- vérification des identifiants, emails, montants et dates ;
- génération d’un rapport JSON et Markdown ;
- code de sortie non nul si une règle bloquante échoue (intégrable à une CI).

```bash
python3 src/server.py
```

Ouvrir ensuite `http://127.0.0.1:8000`, charger l’exemple ou coller un CSV. L’API est aussi disponible via `POST /api/check` avec le contenu CSV comme corps de requête.

## Ligne de commande

```bash
python3 src/run_quality.py
```

Cette commande génère un rapport JSON et Markdown dans `out/`, et retourne un code 1 si des erreurs bloquantes sont trouvées : pratique pour une CI.

## Docker et Render

```bash
docker build -t trust-layer .
docker run --rm -p 8000:8000 trust-layer
```

`render.yaml` prépare le déploiement sur Render via un Blueprint.

## Vérifier

```bash
python3 -m unittest discover -s tests
```
