# Trust Layer

Trust Layer est un contrôle qualité de données utilisable localement : l’application analyse un CSV et rend visibles les erreurs avant qu’elles n’alimentent un reporting ou une décision.

## Test en moins d’une minute

Lance l’application, ouvre `http://localhost:8000`, puis clique sur **Tester le CSV fourni**. Le chargement et les contrôles se font dans le même geste. Le jeu contient volontairement plusieurs anomalies pour rendre le rapport immédiatement lisible.

Le parcours World Bank est séparé et optionnel. Il sert à vérifier récupération, profilage, valeurs absentes et provenance d’une vraie source publique. Si la source ne répond pas, le contrôle CSV local reste entièrement utilisable.

## Ce qui fonctionne

- vérification du schéma exact, des identifiants, emails, montants strictement positifs et dates ;
- génération d’un rapport JSON et Markdown ;
- code de sortie non nul si une règle bloquante échoue (intégrable à une CI).
- profilage à la demande d’une série open data officielle World Bank, avec provenance et valeurs manquantes visibles.
- contrat `orders.v1` versionné, empreinte du contenu analysé et synthèse des règles en échec dans chaque rapport API.

```bash
python3 src/server.py
```

Ouvrir ensuite `http://127.0.0.1:8000`, charger l’exemple ou coller un CSV. L’API est aussi disponible via `POST /api/check` avec le contenu CSV comme corps de requête.

Le bouton « Analyser les données World Bank » appelle `GET /api/open-data/world-bank`. Cette source est volontairement séparée du contrôle métier : elle sert à tester le parcours de récupération, de profilage et de traçabilité d’une donnée publique. L’application garde un message clair si la source externe n’est pas joignable.

`GET /api/contracts/orders` expose le contrat utilisé par l’interface. `POST /api/check` retourne également la version du contrat et une empreinte de la source. Ces éléments permettent de rattacher une décision de qualité au jeu de données exact qui a été analysé.

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
