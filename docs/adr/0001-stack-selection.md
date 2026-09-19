# ADR 0001 — Stack selection

- **Status:** Accepted
- **Date:** 2026-09-19
- **Phase:** 1 (setup and tooling)

## Context

Counterfactual Atlas needs to serve a map and timeline of historical events, run slow
AI generation for counterfactual branches, and do hybrid keyword-plus-semantic search over
event text. It is built solo over sixteen weeks, deployed publicly, and has no budget beyond
free tiers. That last constraint rules out anything priced per-request at the storage or map
layer, and the solo constraint means every extra moving part is a part that will not get
maintained.

## Decision

**FastAPI (Python) for the API.** The AI and data-science libraries this project depends on —
sentence-transformers, pandas, the provider SDKs — are Python-first, and calling them from
another runtime would mean a second service for no gain. FastAPI validates requests from type
hints and generates OpenAPI docs with no extra work, and being ASGI it can hold thousands of
connections open while waiting on 10–30 second LLM calls, which a thread-per-request server
cannot.

**PostgreSQL 16 with pgvector for storage.** One database covers relational event data,
vector similarity search, full-text search, and — via PostGIS in Phase 3 — spatial queries.
The alternative is Postgres plus a dedicated vector database, which means two systems to
operate, two consistency stories, and a join we would have to do in application code.

**Redis for caching and the job queue.** Already required for caching and rate limiting, so
using it for background jobs via `arq` adds no infrastructure. Celery is the industry default
and substantially heavier; `arq` is a few hundred lines of concepts and async-native.

**React with TypeScript, built by Vite.** TypeScript makes the shape of every API response
known at the call site, which is what stops the class of bug this project is most exposed to:
deeply nested event data read wrongly. MapLibre GL renders the map — the open-source fork of
Mapbox GL, so no API key, no usage ceiling, and no billing surprise on a public portfolio site.

**Containers for Postgres and Redis in development.** Dev/prod parity: the container pins the
exact image, version and extension set that CI and production use.

## Alternatives considered

| Considered | Why not |
|---|---|
| Django + DRF | Batteries we would not use, and sync-first request handling is a poor fit for long AI calls |
| Node/Express API | Would force a second Python service for the ML work, or reimplementing it worse |
| MongoDB | Event data is highly relational — entities, places, causal links — and we would rebuild joins by hand |
| Pinecone / Weaviate | A second datastore and a paid tier, to do what pgvector does inside the database we already run |
| Mapbox GL | Requires an API key and meters usage; a public project should not carry that risk |
| Redux | More ceremony than this app's small amount of genuinely global state needs; Zustand is sufficient |
| Homebrew Postgres | Different version and extension set from production — every gap becomes a bug that only appears after deploy |

## Consequences

- One language for API, ingestion and ML, which keeps the shared domain model in one place.
- One database to back up, migrate and reason about — but it also becomes the single point of
  failure, so connection pooling and read performance will need attention by Phase 8.
- The TypeScript frontend costs a few hours of friction in week one and pays it back through
  safe renames and typed API responses for the remaining fifteen weeks.
- pgvector's index performance is adequate at this project's scale (tens of thousands of
  events). If the corpus grew by two orders of magnitude, revisit the dedicated vector store.
