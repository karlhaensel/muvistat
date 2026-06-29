"""Main app module."""

from fastapi import FastAPI

from app.database import lifespan
from app.routers.videos import router as videos_router
from app.routers.snapshots import router as snapshots_router


app = FastAPI(
    title="muvistat",
    description="Track view and like counts for YouTube videos over time.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(videos_router)
app.include_router(snapshots_router)


@app.get("/")
def health_check():
    return {"name": "muvistat API", "status": "running"}
