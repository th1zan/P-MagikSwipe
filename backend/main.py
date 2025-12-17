"""
MagikSwipe Backend API
======================

A clean FastAPI backend with:
- SQLite database (mirroring Supabase structure)
- Local file storage (mirroring Supabase Storage)
- Bidirectional sync with Supabase
- AI content generation via Replicate
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import init_db
from routes import universes_router, generation_router, sync_router, jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    print("🚀 Starting MagikSwipe Backend...")
    init_db()
    print(f"📁 Storage path: {settings.STORAGE_PATH}")
    print(f"💾 Database: {settings.DB_PATH}")
    print(f"🪣 Buckets: {settings.BUCKETS_PATH}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MagikSwipe Backend",
    description="Backend API for MagikSwipe - AI-powered children's learning app",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for local storage
app.mount(
    "/storage/buckets",
    StaticFiles(directory=str(settings.BUCKETS_PATH)),
    name="buckets"
)

# Include routers
app.include_router(universes_router, prefix="/api")
app.include_router(generation_router, prefix="/api")
app.include_router(sync_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")

# Admin router (dangerous operations - use with caution)
from routes.admin import router as admin_router
app.include_router(admin_router)


# Root endpoint
@app.get("/")
def root():
    """API root - health check."""
    return {
        "name": "MagikSwipe Backend",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    from services.supabase_service import supabase_service
    from services.generation_service import generation_service
    
    return {
        "status": "healthy",
        "database": "sqlite",
        "supabase_connected": supabase_service.is_connected,
        "ai_available": generation_service.is_available
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
