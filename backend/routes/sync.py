"""Sync routes - Synchronization with Supabase."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from schemas import SyncRequest, SyncResponse, SyncInitResponse
from services.sync_service import sync_service
from services.supabase_service import supabase_service

router = APIRouter(prefix="/sync", tags=["sync"])


@router.get("/status")
def get_sync_status():
    """Check Supabase connection status."""
    return {
        "supabase_connected": supabase_service.is_connected,
        "supabase_url": supabase_service.client.supabase_url if supabase_service.is_connected else None
    }


@router.post("/init", response_model=SyncInitResponse)
def sync_init(
    db: Session = Depends(get_db)
):
    """
    Initialize local database from Supabase.
    
    Downloads ALL universes from Supabase to local SQLite + storage.
    Use this when starting fresh or to fully sync.
    """
    if not supabase_service.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Supabase not connected. Configure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
        )
    
    result = sync_service.pull_all(db)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)
    
    return result


@router.post("/pull/{slug}", response_model=SyncResponse)
def sync_pull(
    slug: str,
    data: SyncRequest = SyncRequest(),
    db: Session = Depends(get_db)
):
    """
    Pull a single universe from Supabase to local.
    
    Downloads universe data + media files.
    """
    if not supabase_service.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Supabase not connected"
        )
    
    result = sync_service.pull_universe(db, slug, force=data.force)

    if not result.success:
        if "not found" in result.message.lower():
            raise HTTPException(status_code=404, detail=result.message)
        else:
            raise HTTPException(status_code=500, detail=result.message)
    
    return result


@router.post("/push/{slug}", response_model=SyncResponse)
def sync_push(
    slug: str,
    data: SyncRequest = SyncRequest(),
    db: Session = Depends(get_db)
):
    """
    Push a local universe to Supabase.
    
    Uploads universe data + media files.
    """
    if not supabase_service.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Supabase not connected"
        )
    
    result = sync_service.push_universe(db, slug, force=data.force)
    
    if not result.success:
        raise HTTPException(status_code=500, detail=result.message)
    
    return result


@router.post("/pull-all", response_model=SyncInitResponse)
def sync_pull_all(
    db: Session = Depends(get_db)
):
    """
    Pull all universes from Supabase.
    
    Same as /init but can be called anytime.
    """
    return sync_init(db)
