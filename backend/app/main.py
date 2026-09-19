"""Application entry point.

Deliberately almost empty. The point of this commit is the vertical slice: a request
leaves the browser, reaches this process, and comes back. Everything after it is a
modification of a system that already works.
"""

from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="Counterfactual Atlas",
    description="A virtual museum of world history with AI-driven counterfactual timelines",
    version="0.1.0",
)

app.include_router(health_router)
