# services/agents — golden path

LangGraph orchestre seulement le raisonnement et les gates. Temporal reste
réservé au paiement et au provisioning.

```powershell
cd services/agents
python -m pip install -r requirements.txt
python check.py
python check_adapters.py
python check_openhands.py
```

En local, le checkpointer est en mémoire. Pour une reprise durable :

```powershell
$env:AGENTS_DATABASE_URL='postgresql://.../afrosite_agents'
```

Chaque run utilise un `thread_id`, s’interrompt après Gate 1 et ne poursuit la
génération qu’après une approbation explicite. Les outils autorisés sont définis
dans `runtime/tools.py`; aucun shell généraliste ni secret PSP n’entre dans le
graphe.

## Outils réels

`runtime/adapters.py` fournit `StudioTools`, la version non simulée du protocole :

| Étape | Ce qui l’exécute réellement |
|---|---|
| Intent + Architect | `POST /api/studio/run`, flux NDJSON, seul l’événement `result` est retenu |
| Gate 1 | second avis Python via le miroir Pydantic de `packages/contracts` |
| Code | `runtime/code_agent.py` dans un conteneur épinglé par digest, renvoie un diff |
| Security | `scan_generated_artifact`, mêmes règles que le TypeScript (`generation-guardrails.json`) |
| QA | commandes fixes (`check`, `eval:agents`, `eval:llm`, `lint`), jamais de shell |
| Preview | `POST /api/studio/preview` + capture desktop/mobile sandbox `/t/{slug}` uniquement |

```powershell
$env:STUDIO_BASE_URL='http://127.0.0.1:3000'
$env:AFROSITE_STUDIO_ACCESS_KEY='...'
```

Le graphe ne pousse ni ne fusionne jamais : il s’arrête sur une branche
`feature/generated-*` et un diff à relire.
