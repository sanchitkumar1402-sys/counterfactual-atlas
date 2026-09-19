# Roadmap

Sixteen weeks, nine phases. The current phase is marked.

| Phase | Weeks | What gets built | Status |
|---|---|---|---|
| **1 · Setup and tooling** | 1–2 | Toolchain, repository, CI, containers, vertical slice | **← current** |
| 2 · Data model and API | 3–4 | Schema, migrations, CRUD endpoints, settings | |
| 3 · Ingestion | 5–6 | Wikidata/Wikipedia ETL, media pipeline, PostGIS, data-quality report | |
| 4 · Client | 7–8 | Map, timeline, routing, React Query, screenshot in the README | |
| 5 · Search and embeddings | 9–10 | pgvector, local embeddings, hybrid keyword + semantic search | |
| 6 · Counterfactual engine | 11–12 | Retrieval, prompt assembly, arq workers, validated structured output | |
| 7 · Classifiers | 12–13 | Event-type and tone models, fine-tuned in Colab | |
| 8 · Hardening | 14 | Tests, load testing, structured logging, Sentry | |
| 9 · Deploy | 15–16 | Dockerfile, managed Postgres, hosting, public URL | |

Every issue carries the milestone for its phase. Work in progress is limited to two items.
