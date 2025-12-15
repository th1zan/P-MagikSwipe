"""
Routes pour la gestion des jobs asynchrones
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from services.job_service import get_job, list_jobs, get_active_jobs_count, cleanup_old_jobs

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("")
@router.get("/")
async def list_all_jobs(universe: str = None, limit: int = 50):
    """
    Liste tous les jobs, optionnellement filtrés par univers.
    
    Args:
        universe: Filtrer par univers (optionnel)
        limit: Nombre maximum de jobs à retourner (défaut: 50)
    """
    jobs = list_jobs(universe=universe, limit=limit)
    return {
        "jobs": jobs,
        "total": len(jobs),
        "active": get_active_jobs_count()
    }


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Récupère le statut d'un job spécifique.
    
    Returns:
        - id: Identifiant du job
        - type: Type de job (generate_music, translate_lyrics, etc.)
        - universe: Univers concerné
        - status: pending | running | completed | failed
        - progress: Message de progression (optionnel)
        - result: Résultat si completed
        - error: Message d'erreur si failed
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=404, 
            detail="Job not found. It may have expired or the API was restarted."
        )
    return job


@router.delete("/cleanup")
async def cleanup_jobs(max_age_hours: int = 24):
    """
    Nettoie les anciens jobs terminés.
    Utile pour libérer de la mémoire.
    """
    cleanup_old_jobs(max_age_hours)
    return {"message": f"Cleaned up jobs older than {max_age_hours} hours"}
