from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
from routes import generation, universes, prompts
app.include_router(universes.router, prefix="/api", tags=["universes"])
app.include_router(generation.router, prefix="/api", tags=["generation"])
app.include_router(prompts.router, prefix="/api", tags=["prompts"])
app.mount("/storage", StaticFiles(directory="/app/storage"), name="storage")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)