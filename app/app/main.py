"""FastAPI service used as the deployable workload for this DevOps portfolio.

The app is intentionally small; the value of this repository is in *how it is
built, shipped, observed and operated*, not in the business logic itself.
"""
from __future__ import annotations

import logging
import os
import socket

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='{"level":"%(levelname)s","logger":"%(name)s","msg":"%(message)s"}',
)
logger = logging.getLogger("api")

APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
app = FastAPI(
    title="bjcf-devops-portfolio API",
    description="Sample workload demonstrating a full cloud-native delivery pipeline.",
    version=APP_VERSION,
)

# Expose Prometheus metrics at /metrics (request latency, counts, in-progress...).
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


class HelloResponse(BaseModel):
    message: str
    host: str
    version: str


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {
        "service": "bjcf-devops-portfolio",
        "version": APP_VERSION,
        "docs": "/docs",
        "metrics": "/metrics",
    }


@app.get("/api/v1/hello", response_model=HelloResponse, tags=["api"])
def hello(name: str = "world") -> HelloResponse:
    logger.info("greeting requested for %s", name)
    return HelloResponse(
        message=f"Hello, {name}!",
        host=socket.gethostname(),
        version=APP_VERSION,
    )


@app.get("/health/live", tags=["health"])
def liveness() -> JSONResponse:
    """Liveness probe: is the process up?"""
    return JSONResponse({"status": "alive"})


@app.get("/health/ready", tags=["health"])
def readiness() -> JSONResponse:
    """Readiness probe: is the app ready to serve traffic?

    In a real service this would check DB/cache connectivity. Kept trivial here.
    """
    return JSONResponse({"status": "ready"})
