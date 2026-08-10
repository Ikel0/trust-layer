# Trust Layer

Un moteur de data quality qui analyse un CSV et produit un rapport exploitable : erreurs, lignes concernées et sévérité.

## Ce qui fonctionne

- vérification des identifiants, emails, montants et dates ;
- génération d’un rapport JSON et Markdown ;
- code de sortie non nul si une règle bloquante échoue (intégrable à une CI).

```bash
cd projects/trust-layer
python3 src/run_quality.py
```

Suite : connecteur Snowflake/dbt, historique de qualité et alerting.
