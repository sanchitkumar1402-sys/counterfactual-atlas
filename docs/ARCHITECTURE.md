# Architecture

Five tiers. Data flows down; requests flow up.

```
                     ┌─────────────────────────────────────────┐
                     │  Client — React + TS, Vite, MapLibre GL │
                     │  map · timeline · counterfactual branch │
                     └────────────────────┬────────────────────┘
                                          │ HTTP / JSON
                     ┌────────────────────┴────────────────────┐
                     │  API — FastAPI on Uvicorn               │
                     │  validation · auth · rate limiting      │
                     └──────┬──────────────────────────┬───────┘
                            │                          │ enqueue
       ┌────────────────────┴─────────┐   ┌────────────┴──────────────────┐
       │  Counterfactual engine       │   │  Workers — arq on Redis       │
       │  retrieval · prompt assembly │   │  generation · embedding · ETL │
       │  LLM call · validation       │   └────────────┬──────────────────┘
       └────────────────────┬─────────┘                │
                            │                          │
       ┌────────────────────┴──────────────────────────┴───────┐
       │  Storage — PostgreSQL 16                              │
       │  relational events · pgvector embeddings · PostGIS    │
       │  Redis — cache, rate limits, job queue                │
       └────────────────────┬──────────────────────────────────┘
                            │
       ┌────────────────────┴──────────────────────────────────┐
       │  Ingestion — Wikidata SPARQL, Wikipedia, Commons,     │
       │  Europeana, Met, Smithsonian → normalise → load       │
       └───────────────────────────────────────────────────────┘
```

## Why each boundary is where it is

**The engine is not in the API process's request path.** A counterfactual generation takes
10–30 seconds. The API enqueues the job and returns a job id; the client polls. This is the
single decision that keeps the API responsive under load.

**Ingestion writes only to staging tables.** Source data is messy — ambiguous dates, duplicate
entities, missing coordinates — and normalisation is where most of the bugs live. Keeping raw
and production tables separate means a bad ingest run is reverted rather than untangled.

**The LLM provider sits behind one module.** `app/services/llm.py` is the only file that
imports a provider SDK, so changing providers touches one file.

Decision records live in [adr/](adr/).
