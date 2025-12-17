"""Routes module - API endpoints."""
from .universes import router as universes_router
from .generation import router as generation_router
from .sync import router as sync_router
from .jobs import router as jobs_router

__all__ = [
    "universes_router",
    "generation_router",
    "sync_router",
    "jobs_router"
]
