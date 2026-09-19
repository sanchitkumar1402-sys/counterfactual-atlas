"""Liveness endpoint.

Kept dependency-free on purpose: it answers "is this process up", not "is the database
reachable". A readiness check that also pings Postgres and Redis belongs alongside it
once there is a database to ping.
"""

from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
