"""Job service - Persistent async job tracking with SQLite."""
import json
import threading
import traceback
from datetime import datetime
from typing import Optional, Callable, Any, List
from sqlalchemy.orm import Session

from database import Job, JobStatus, SessionLocal


class JobService:
    """
    Manages async jobs with persistence in SQLite.
    
    Jobs survive server restarts and can be monitored via API.
    """
    
    def __init__(self):
        self._lock = threading.Lock()
    
    # =========================================================================
    # JOB CRUD
    # =========================================================================
    
    def create_job(
        self,
        db: Session,
        job_type: str,
        univers_slug: Optional[str] = None,
        total_steps: int = 0
    ) -> Job:
        """
        Create a new job in PENDING state.
        
        Args:
            db: Database session
            job_type: Type of job (e.g., "generate_images", "sync_pull")
            univers_slug: Related universe slug (optional)
            total_steps: Total number of steps for progress tracking
        
        Returns:
            Created Job object
        """
        job = Job(
            type=job_type,
            univers_slug=univers_slug,
            status=JobStatus.PENDING,
            progress=0,
            total_steps=total_steps,
            current_step=0
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return job
    
    def get_job(self, db: Session, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return db.query(Job).filter(Job.id == job_id).first()
    
    def get_jobs(
        self,
        db: Session,
        univers_slug: Optional[str] = None,
        status: Optional[JobStatus] = None,
        limit: int = 50
    ) -> List[Job]:
        """
        Get jobs with optional filters.
        
        Args:
            db: Database session
            univers_slug: Filter by universe
            status: Filter by status
            limit: Max number of jobs to return
        
        Returns:
            List of jobs
        """
        query = db.query(Job)
        
        if univers_slug:
            query = query.filter(Job.univers_slug == univers_slug)
        
        if status:
            query = query.filter(Job.status == status)
        
        return query.order_by(Job.created_at.desc()).limit(limit).all()
    
    def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        progress: Optional[int] = None,
        current_step: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
        result: Optional[Any] = None
    ):
        """
        Update job progress/status.
        
        Thread-safe - can be called from background threads.
        """
        with self._lock:
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if not job:
                    return
                
                if status:
                    job.status = status
                    if status == JobStatus.RUNNING and not job.started_at:
                        job.started_at = datetime.utcnow()
                    elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                        job.completed_at = datetime.utcnow()
                
                if progress is not None:
                    job.progress = progress
                
                if current_step is not None:
                    job.current_step = current_step
                    if job.total_steps > 0:
                        job.progress = int((current_step / job.total_steps) * 100)
                
                if message:
                    job.message = message
                
                if error:
                    job.error = error
                
                if result is not None:
                    job.result = json.dumps(result) if not isinstance(result, str) else result
                
                db.commit()
                
            finally:
                db.close()
    
    def delete_old_jobs(self, db: Session, days: int = 7) -> int:
        """
        Delete completed/failed jobs older than X days.
        
        Returns:
            Number of deleted jobs
        """
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        result = db.query(Job)\
            .filter(Job.status.in_([JobStatus.COMPLETED, JobStatus.FAILED]))\
            .filter(Job.completed_at < cutoff)\
            .delete()
        
        db.commit()
        return result
    
    # =========================================================================
    # JOB EXECUTION
    # =========================================================================
    
    def run_async(
        self,
        db: Session,
        job_type: str,
        task_func: Callable,
        univers_slug: Optional[str] = None,
        total_steps: int = 0,
        **kwargs
    ) -> Job:
        """
        Create a job and run task in background thread.
        
        Args:
            db: Database session
            job_type: Type of job
            task_func: Function to execute (receives job_id as first arg)
            univers_slug: Related universe
            total_steps: Total steps for progress
            **kwargs: Additional args passed to task_func
        
        Returns:
            Created Job object (execution continues in background)
        """
        # Create job
        job = self.create_job(db, job_type, univers_slug, total_steps)
        job_id = job.id
        
        # Define wrapper
        def run_task():
            try:
                self.update_job(job_id, status=JobStatus.RUNNING, message="Starting...")
                
                # Execute task
                result = task_func(job_id, **kwargs)
                
                self.update_job(
                    job_id,
                    status=JobStatus.COMPLETED,
                    progress=100,
                    message="Completed successfully",
                    result=result
                )
                
            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                self.update_job(
                    job_id,
                    status=JobStatus.FAILED,
                    error=error_msg,
                    message=f"Failed: {str(e)}"
                )
        
        # Start background thread
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()
        
        return job
    
    # =========================================================================
    # PROGRESS HELPERS
    # =========================================================================
    
    def step(self, job_id: str, message: Optional[str] = None):
        """Increment current step by 1."""
        with self._lock:
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.current_step += 1
                    if job.total_steps > 0:
                        job.progress = int((job.current_step / job.total_steps) * 100)
                    if message:
                        job.message = message
                    db.commit()
            finally:
                db.close()
    
    def set_total_steps(self, job_id: str, total: int):
        """Update total steps (useful when count is determined during execution)."""
        self.update_job(job_id, current_step=0)
        
        with self._lock:
            db = SessionLocal()
            try:
                job = db.query(Job).filter(Job.id == job_id).first()
                if job:
                    job.total_steps = total
                    db.commit()
            finally:
                db.close()


# Singleton instance
job_service = JobService()
