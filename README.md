# Clinical Trials LangChain FastAPI

Production-ready FastAPI service that demonstrates a LangChain-inspired clinical trials workflow with three nodes:

- **Orchestrator** – coordinates the request lifecycle
- **ClinOps** – operational summary of matched trials
- **InsightGenerator** – aggregates insight metrics

The application includes a deterministic Text-to-SQL agent that maps natural language questions to SQL queries against a public clinical trials-style dataset.

## Dataset

The dataset (`data/clinical_trials.csv`) is a small, curated subset modeled after common fields from public clinical trial registries (e.g., ClinicalTrials.gov). It is used locally to demonstrate SQL filtering and orchestration.

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Query the service:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question":"Show Phase 2 recruiting trials for Alzheimer\'s disease"}'
```

## Docker

```bash
docker compose up --build
```

Then query the service at `http://127.0.0.1:8000/query`.

## Notes

- The Text-to-SQL agent uses deterministic rules for interpretability and reliability.
- Assumptions were made to keep the example self-contained and production-ready without external dependencies.
