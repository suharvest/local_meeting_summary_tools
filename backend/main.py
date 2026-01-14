"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import config
from .database import Database, db as db_module
from .llm.factory import LLMFactory, llm_factory as llm_module
from .api.devices import router as devices_router
from .api.meetings import router as meetings_router
import backend.database as database_mod
import backend.llm.factory as factory_mod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup: Initialize database and LLM factory
    logger.info("Starting Meeting Assistant Backend...")

    # Initialize database connection pool
    db = Database(config.database)
    await db.connect()
    database_mod.db = db
    logger.info(f"Database connected: {config.database['host']}:{config.database['port']}")

    # Initialize LLM factory
    llm_factory = LLMFactory(config.llm)
    factory_mod.llm_factory = llm_factory
    logger.info(f"LLM Factory initialized with default provider: {config.llm.get('default_provider', 'gemini')}")

    yield

    # Shutdown: Close connections
    logger.info("Shutting down...")
    await db.disconnect()
    logger.info("Database disconnected")


# Create FastAPI application
app = FastAPI(
    title="Meeting Assistant API",
    description="API for meeting recording, transcription, and AI-powered minutes generation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS (for development with separate frontend server)
# Note: allow_credentials=False when using wildcard origins for security
cors_origins = config.server.get("cors_origins", ["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,  # Disabled for security with wildcard origins
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict to needed methods
    allow_headers=["*"],
)

# Register API routers
app.include_router(devices_router)
app.include_router(meetings_router)


@app.get("/api/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_provider": config.llm.get("default_provider", "unknown")
    }


# Serve frontend static files
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    # Mount static assets
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    # Serve index.html for all non-API routes (SPA support)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend SPA - all non-API routes return index.html."""
        file_path = FRONTEND_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    @app.get("/")
    async def root():
        """Root endpoint when frontend is not built."""
        return {
            "name": "Meeting Assistant API",
            "version": "1.0.0",
            "message": "Frontend not built. Run 'npm run build' in frontend directory.",
            "endpoints": {
                "devices": "/api/devices",
                "meetings": "/api/meetings",
                "docs": "/docs"
            }
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.server.get("host", "0.0.0.0"),
        port=config.server.get("port", 5173),
        reload=True
    )
