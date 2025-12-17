"""Admin endpoints for system maintenance and cleanup operations."""

import re
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db, Univers, UniversAsset, UniversAssetPrompts, UniversAssetTranslation, UniversTranslation, UniversPrompts, UniversMusicPrompts
from services.storage_service import storage_service
from services.supabase_service import supabase_service

router = APIRouter(prefix="/api/admin", tags=["admin"])


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def is_test_universe(slug: str) -> bool:
    """Validate that a slug corresponds to a test universe."""
    # Case-insensitive pattern: any slug containing 'test' anywhere (test, Test, TEST, etc.)
    test_pattern = re.compile(r'(?i).*test.*')
    return bool(test_pattern.match(slug))


def validate_cleanup_request(slug: str, confirm: bool) -> None:
    """Validations before cleanup."""
    if not is_test_universe(slug):
        raise HTTPException(
            status_code=400,
            detail=f"Slug '{slug}' is not a test universe. Only slugs containing 'test' (case-insensitive) are allowed."
        )

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set confirm=true to proceed with deletion."
        )


# =============================================================================
# CLEANUP OPERATIONS
# =============================================================================

def cleanup_local_universe(slug: str, db: Session) -> Dict[str, Any]:
    """Clean up a universe in local database."""
    try:
        univers = db.query(Univers).filter(Univers.slug == slug).first()
        if not univers:
            return {"status": "not_found", "slug": slug}

        # Delete in order to respect FK constraints
        # 1. Delete asset translations
        db.query(UniversAssetTranslation).filter(
            UniversAssetTranslation.asset_id.in_(
                db.query(UniversAsset.id).filter(UniversAsset.univers_id == univers.id)
            )
        ).delete()

        # 2. Delete asset prompts
        db.query(UniversAssetPrompts).filter(
            UniversAssetPrompts.asset_id.in_(
                db.query(UniversAsset.id).filter(UniversAsset.univers_id == univers.id)
            )
        ).delete()

        # 3. Delete assets (files will be deleted after DB cleanup)
        db.query(UniversAsset).filter(UniversAsset.univers_id == univers.id).delete()

        # 4. Delete music prompts
        db.query(UniversMusicPrompts).filter(UniversMusicPrompts.univers_id == univers.id).delete()

        # 5. Delete translations and prompts
        db.query(UniversTranslation).filter(UniversTranslation.univers_id == univers.id).delete()
        db.query(UniversPrompts).filter(UniversPrompts.univers_id == univers.id).delete()

        # 6. Delete the universe
        db.delete(univers)
        db.commit()

        # 7. Delete local files after successful DB cleanup
        files_deleted = storage_service.delete_universe_folder(slug)

        return {
            "status": "deleted",
            "slug": slug,
            "local_cleanup": True,
            "local_files_deleted": files_deleted
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "slug": slug, "error": str(e), "local_cleanup": False}


def cleanup_supabase_universe(slug: str) -> Dict[str, Any]:
    """Clean up a universe on Supabase completely."""
    operations = []

    try:
        # 1. Récupérer les données de l'univers
        operations.append({"step": "get_universe", "status": "in_progress"})
        univers_data = supabase_service.get_univers_by_slug(slug)

        if not univers_data:
            operations[-1].update({"status": "not_found", "details": "Universe not found on Supabase"})
            return {
                "status": "not_found_remote",
                "slug": slug,
                "supabase_cleanup": False,
                "operations": operations
            }

        univers_id = univers_data["id"]
        operations[-1].update({"status": "success", "univers_id": univers_id})

        # 2. Récupérer tous les assets
        operations.append({"step": "get_assets", "status": "in_progress"})
        assets = supabase_service.get_assets(univers_id)
        operations[-1].update({"status": "success", "assets_count": len(assets)})

        # 3. Supprimer les fichiers du storage Supabase
        if assets:
            operations.append({"step": "delete_files", "status": "in_progress"})
            file_paths = []
            for asset in assets:
                if asset.get("image_name"):
                    file_paths.append(f"{slug}/{asset['image_name']}")
                # Ajouter vidéos si elles existent
                if asset.get("video_name"):
                    file_paths.append(f"{slug}/{asset['video_name']}")

            if file_paths:
                try:
                    supabase_service.delete_from_storage(file_paths)
                    operations[-1].update({"status": "success", "files_deleted": len(file_paths)})
                except Exception as e:
                    operations[-1].update({"status": "warning", "error": str(e), "files_deleted": 0})
            else:
                operations[-1].update({"status": "success", "files_deleted": 0})
        else:
            operations.append({"step": "delete_files", "status": "skipped", "reason": "no assets"})

        # 4. Supprimer tous les assets
        operations.append({"step": "delete_assets", "status": "in_progress"})
        try:
            supabase_service.delete_all_assets(univers_id)
            operations[-1].update({"status": "success"})
        except Exception as e:
            operations[-1].update({"status": "error", "error": str(e)})
            return {
                "status": "partial_failure",
                "slug": slug,
                "supabase_cleanup": False,
                "operations": operations,
                "error": "Failed to delete assets"
            }

        # 5. Supprimer les prompts musique
        operations.append({"step": "delete_music", "status": "in_progress"})
        try:
            supabase_service.delete_univers_music_prompts(univers_id)
            operations[-1].update({"status": "success"})
        except Exception as e:
            operations[-1].update({"status": "warning", "error": str(e)})

        # 6. Supprimer les traductions
        operations.append({"step": "delete_translations", "status": "in_progress"})
        try:
            supabase_service.delete_univers_translations(univers_id)
            operations[-1].update({"status": "success"})
        except Exception as e:
            operations[-1].update({"status": "warning", "error": str(e)})

        # 7. Supprimer l'univers lui-même
        operations.append({"step": "delete_universe", "status": "in_progress"})
        try:
            supabase_service.delete_univers(univers_id)
            operations[-1].update({"status": "success"})
        except Exception as e:
            operations[-1].update({"status": "error", "error": str(e)})
            return {
                "status": "partial_failure",
                "slug": slug,
                "supabase_cleanup": False,
                "operations": operations,
                "error": "Failed to delete universe"
            }

        return {
            "status": "success",
            "slug": slug,
            "supabase_cleanup": True,
            "operations": operations
        }

    except Exception as e:
        operations.append({"step": "unexpected_error", "status": "error", "error": str(e)})
        return {
            "status": "error",
            "slug": slug,
            "supabase_cleanup": False,
            "operations": operations,
            "error": str(e)
        }


def cleanup_universe_complete(slug: str, db: Session) -> Dict[str, Any]:
    """Clean up a universe completely (local + Supabase)."""

    results = {
        "slug": slug,
        "timestamp": datetime.utcnow().isoformat(),
        "operations": []
    }

    # 1. Local cleanup
    local_result = cleanup_local_universe(slug, db)
    results["operations"].append({
        "type": "local_cleanup",
        "result": local_result
    })

    # 2. Supabase cleanup
    supabase_result = cleanup_supabase_universe(slug)
    results["operations"].append({
        "type": "supabase_cleanup",
        "result": supabase_result
    })

    # 3. Final summary
    successful_ops = [op for op in results["operations"]
                     if op["result"]["status"] in ["deleted", "not_found", "not_found_remote"]]

    results["overall_status"] = "success" if len(successful_ops) == len(results["operations"]) else "partial_failure"

    return results


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================

@router.post("/cleanup-test-universes")
def cleanup_all_test_universes(
    confirm: bool = Query(False, description="Must be true to proceed with deletion"),
    dry_run: bool = Query(True, description="If true, only show what would be deleted"),
    db: Session = Depends(get_db)
):
    """Clean up all test universes (matching test-* pattern).

    This endpoint will:
    1. Find all universes with slugs matching 'test-*' pattern
    2. Delete them from local database
    3. Delete them from Supabase
    4. Delete associated files from storage

    Args:
        confirm: Must be true to actually perform deletion
        dry_run: If true, only list what would be deleted

    Returns:
        Detailed report of cleanup operations
    """
    if not confirm and not dry_run:
        raise HTTPException(
            status_code=400,
            detail="Either set dry_run=true for preview, or confirm=true to proceed with deletion."
        )

    # Find all test universes
    all_universes = db.query(Univers).all()
    test_universes = [u for u in all_universes if is_test_universe(u.slug)]

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "dry_run": dry_run,
        "confirmed": confirm,
        "found_test_universes": len(test_universes),
        "test_universe_slugs": [u.slug for u in test_universes],
        "operations": []
    }

    if dry_run:
        results["message"] = f"DRY RUN: Would delete {len(test_universes)} test universes"
        return results

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set confirm=true to proceed with deletion."
        )

    # Perform cleanup for each test universe
    successful_cleanups = 0
    failed_cleanups = 0

    for universe in test_universes:
        try:
            cleanup_result = cleanup_universe_complete(universe.slug, db)
            results["operations"].append(cleanup_result)

            if cleanup_result["overall_status"] == "success":
                successful_cleanups += 1
            else:
                failed_cleanups += 1

        except Exception as e:
            results["operations"].append({
                "slug": universe.slug,
                "overall_status": "error",
                "error": str(e)
            })
            failed_cleanups += 1

    results["successful_cleanups"] = successful_cleanups
    results["failed_cleanups"] = failed_cleanups
    results["message"] = f"Cleaned up {successful_cleanups} test universes successfully"

    if failed_cleanups > 0:
        results["message"] += f", {failed_cleanups} failed"

    return results


@router.delete("/cleanup-test-universes/{slug}")
def cleanup_single_test_universe(
    slug: str,
    confirm: bool = Query(False, description="Must be true to proceed with deletion"),
    db: Session = Depends(get_db)
):
    """Clean up a single test universe.

    Args:
        slug: Universe slug to delete (must match test-* pattern)
        confirm: Must be true to proceed with deletion

    Returns:
        Detailed report of cleanup operations
    """
    # Validate the request
    validate_cleanup_request(slug, confirm)

    # Perform complete cleanup
    result = cleanup_universe_complete(slug, db)

    if result["overall_status"] == "success":
        return {
            "message": f"Test universe '{slug}' successfully cleaned up",
            "details": result
        }
    else:
        # Some operations failed
        failed_ops = [op for op in result["operations"] if op["result"]["status"] not in ["deleted", "not_found", "not_found_remote"]]
        raise HTTPException(
            status_code=500,
            detail=f"Partial cleanup failure for universe '{slug}'. Failed operations: {failed_ops}"
        )


@router.get("/cleanup-test-universes")
def list_test_universes(db: Session = Depends(get_db)):
    """List all test universes that can be cleaned up.

    Returns:
        List of test universe slugs found in the system
    """
    all_universes = db.query(Univers).all()
    test_universes = [u for u in all_universes if is_test_universe(u.slug)]

    return {
        "test_universes_count": len(test_universes),
        "test_universe_slugs": [u.slug for u in test_universes],
        "pattern": "*test* (case-insensitive)"
    }