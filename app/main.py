"""Main app module."""

import logging

from fastapi import FastAPI

from app.database import lifespan
from app.routers.videos import router as videos_router
from app.routers.snapshots import router as snapshots_router


# Configure logger on main level and handler:
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
# Every module just needs to create a logger starting with "api." to inherit settings.

# Create fastAPI app and include routers:
app = FastAPI(
    title="muvistat",
    description="Track view, like, and comment counts for YouTube videos over time.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(videos_router)
app.include_router(snapshots_router)


# Add default health check:
@app.get("/")
def health_check():
    return {"name": "muvistat API", "status": "running"}
