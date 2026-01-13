"""API routes module."""
from .devices import router as devices_router
from .meetings import router as meetings_router

__all__ = ["devices_router", "meetings_router"]
