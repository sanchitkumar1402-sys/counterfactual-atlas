# Counterfactual Atlas

A virtual museum of world history with AI-driven counterfactual timelines — explore what
happened, then ask what might have happened instead.

<!-- ![screenshot](docs/screenshot.png)  <- add in week 8 -->

## Why

History is taught as a fixed sequence of dates. It was contingent: a treaty signed a week
later, a battle lost instead of won, and the map looks different. This project makes that
contingency explorable — a map and timeline of real events, with grounded AI-generated
counterfactual branches you can follow and compare against the record.

## Quickstart

```bash
git clone https://github.com/<you>/counterfactual-atlas.git
cd counterfactual-atlas

# 1. services
docker compose -f infra/docker-compose.yml up -d

# 2. backend
cd backend
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload          # http://localhost:8000/docs

# 3. frontend
cd ../frontend
npm install
npm run dev                            # http://localhost:5173
```

## Architecture

Five tiers: ingestion → storage → API → counterfactual engine → client.
See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI + Uvicorn | Validation from type hints, free OpenAPI docs, async for slow LLM calls |
| Storage | PostgreSQL 16 + pgvector | One database for relational, vector and (later) spatial data |
| Cache / queue | Redis + arq | Caching and background AI jobs without Celery's weight |
| ORM | SQLAlchemy 2 + Alembic | Versioned, reversible schema changes |
| Frontend | React + TypeScript + Vite | Typed API responses, instant dev server |
| Map | MapLibre GL | Open source, no API key, no usage ceiling |
| ML | sentence-transformers, DistilBERT | Local embeddings, fine-tuned classifiers |

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). **Current phase: Phase 1 — setup and tooling.**

## Development

```bash
pytest                                            # tests
ruff check . && ruff format --check .             # lint and format
alembic upgrade head                              # migrations
python -m data.ingest.seed                        # seed data
pre-commit run --all-files                        # everything CI runs
```

## Licence

Code: MIT, see [LICENSE](LICENSE).
Content and data: see [DATA_LICENSES.md](DATA_LICENSES.md) — not all of it is MIT, and not
all of it is ours to relicense.

## Acknowledgements

Wikidata and Wikipedia (Wikimedia Foundation), Wikimedia Commons, Europeana, the
Metropolitan Museum of Art and the Smithsonian Open Access programme.
