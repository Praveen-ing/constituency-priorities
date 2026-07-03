"""
FastAPI application entrypoint.
"""
from __future__ import annotations

import logging

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import submissions, themes, priorities, webhooks, chat
from app.config import get_settings

# ── Logging ──────────────────────────────────────────────────────────────────
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger()

# ── App ───────────────────────────────────────────────────────────────────────
settings = get_settings()

app = FastAPI(
    title="Constituency Priorities API",
    description="AI platform for constituency development planning — Track 1, Code for Communities",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(submissions.router)
app.include_router(themes.router)
app.include_router(priorities.router)
app.include_router(webhooks.router)
app.include_router(chat.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {
        "status": "ok",
        "version": "0.1.0",
        "constituency": settings.pilot_constituency,
        "environment": settings.environment,
    }


@app.get("/", tags=["meta"])
async def root() -> dict:
    return {
        "name": "Constituency Priorities API",
        "docs": "/docs",
        "health": "/health",
    }
