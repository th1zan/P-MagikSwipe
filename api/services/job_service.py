"""
Service de gestion des jobs asynchrones en mémoire.
Les jobs sont exécutés en background et leur statut peut être polled.
"""
import threading
import uuid
from datetime import datetime
from typing import Callable, Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Stockage en mémoire des jobs
JOBS: Dict[str, dict] = {}


def create_job(
    job_type: str, 
    universe: str, 
    task_fn: Callable, 
    description: str = "",
    **params
) -> str:
    """
    Crée un job et lance l'exécution en background.
    
    Args:
        job_type: Type de job (generate_music, translate_lyrics, etc.)
        universe: ID de l'univers concerné
        task_fn: Fonction à exécuter (doit retourner un résultat sérialisable)
        description: Description pour l'UI
        **params: Paramètres à passer à task_fn
    
    Returns:
        job_id: Identifiant unique du job
    """
    job_id = str(uuid.uuid4())[:8]
    
    JOBS[job_id] = {
        "id": job_id,
        "type": job_type,
        "universe": universe,
        "description": description,
        "status": "pending",
        "progress": None,
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    def wrapped_task():
        """Wrapper qui met à jour le statut du job"""
        try:
            JOBS[job_id]["status"] = "running"
            logger.info(f"Job {job_id} started: {job_type} for {universe}")
            
            # Exécute la tâche longue
            result = task_fn(**params)
            
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["result"] = result
            JOBS[job_id]["completed_at"] = datetime.now().isoformat()
            logger.info(f"Job {job_id} completed successfully")
            
        except Exception as e:
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["error"] = str(e)
            JOBS[job_id]["completed_at"] = datetime.now().isoformat()
            logger.error(f"Job {job_id} failed: {e}")
    
    # Lancer en background (daemon=True pour ne pas bloquer l'arrêt du serveur)
    thread = threading.Thread(target=wrapped_task, daemon=True)
    thread.start()
    
    logger.info(f"Job {job_id} created and started in background")
    return job_id


def update_job_progress(job_id: str, progress: str):
    """Met à jour le message de progression d'un job"""
    if job_id in JOBS:
        JOBS[job_id]["progress"] = progress


def get_job(job_id: str) -> Optional[dict]:
    """Récupère le statut d'un job"""
    return JOBS.get(job_id)


def list_jobs(universe: str = None, limit: int = 50) -> List[dict]:
    """
    Liste les jobs, optionnellement filtrés par univers.
    Retourne les plus récents en premier.
    """
    jobs = list(JOBS.values())
    
    if universe:
        jobs = [j for j in jobs if j["universe"] == universe]
    
    # Trier par date de création décroissante
    jobs = sorted(jobs, key=lambda x: x["created_at"], reverse=True)
    
    return jobs[:limit]


def cleanup_old_jobs(max_age_hours: int = 24):
    """
    Nettoie les jobs terminés plus vieux que max_age_hours.
    Appelé périodiquement pour éviter une fuite mémoire.
    """
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    to_delete = []
    
    for job_id, job in JOBS.items():
        if job["status"] in ("completed", "failed"):
            created = datetime.fromisoformat(job["created_at"])
            if created < cutoff:
                to_delete.append(job_id)
    
    for job_id in to_delete:
        del JOBS[job_id]
    
    if to_delete:
        logger.info(f"Cleaned up {len(to_delete)} old jobs")


def get_active_jobs_count() -> int:
    """Retourne le nombre de jobs en cours"""
    return sum(1 for j in JOBS.values() if j["status"] in ("pending", "running"))
