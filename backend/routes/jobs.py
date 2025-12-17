"""Jobs routes - Async job tracking endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, Job, JobStatus
from schemas import JobResponse
from services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=List[JobResponse])
def list_jobs(
    univers_slug: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all jobs with optional filters."""
    job_status = None
    if status:
        try:
            job_status = JobStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    jobs = job_service.get_jobs(
        db=db,
        univers_slug=univers_slug,
        status=job_status,
        limit=limit
    )
    
    return [
        JobResponse(
            id=j.id,
            type=j.type,
            univers_slug=j.univers_slug,
            status=j.status,
            progress=j.progress,
            total_steps=j.total_steps,
            current_step=j.current_step,
            message=j.message,
            error=j.error,
            created_at=j.created_at,
            started_at=j.started_at,
            completed_at=j.completed_at
        )
        for j in jobs
    ]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific job by ID."""
    job = job_service.get_job(db, job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")
    
    return JobResponse(
        id=job.id,
        type=job.type,
        univers_slug=job.univers_slug,
        status=job.status,
        progress=job.progress,
        total_steps=job.total_steps,
        current_step=job.current_step,
        message=job.message,
        error=job.error,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at
    )


@router.delete("/cleanup")
def cleanup_jobs(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Delete completed/failed jobs older than X days."""
    deleted = job_service.delete_old_jobs(db, days)
    
    return {
        "success": True,
        "message": f"Deleted {deleted} old jobs",
        "deleted_count": deleted
    }
