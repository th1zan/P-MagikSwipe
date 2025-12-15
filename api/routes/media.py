from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/media", tags=["media"])

STORAGE_PATH = Path("/app/storage")
UNIVERS_PATH = STORAGE_PATH / "univers"

@router.get("/univers/{folder_name}/{filename:path}")
async def serve_universe_media(folder_name: str, filename: str):
    """Sert les médias depuis les univers"""

    # Support pour assets/ subdirectory
    if filename.startswith("assets/"):
        file_path = UNIVERS_PATH / folder_name / filename
    else:
        file_path = UNIVERS_PATH / folder_name / "assets" / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Media {filename} not found")

    return FileResponse(file_path)
