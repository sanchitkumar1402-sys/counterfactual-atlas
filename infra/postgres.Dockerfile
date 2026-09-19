# Phase 3 only. No public image ships pgvector and PostGIS together, so when the
# spatial work starts, build this and swap the compose `image:` line for
#   build: {context: ., dockerfile: postgres.Dockerfile}
FROM pgvector/pgvector:pg16
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-16-postgis-3 \
 && rm -rf /var/lib/apt/lists/*
