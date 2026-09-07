"""FastAPI router for videos."""

import logging

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.database.videos import check_video_exists, create_video
from app.models import VideoCreate, VideoResponse

logger = logging.getLogger("api.routers.videos")

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("", response_model=VideoResponse, status_code=201)
def add_video(video: VideoCreate):
    """Add a new video to be tracked."""
    logger.debug(f"Attempting to add video with ID {video.video_id}.")
    try:
        check_video_exists(video.video_id, raise_for="already_existing")
    except HTTPException:
        logger.error(f"Video with ID {video.video_id} already exists in database.")
        raise

    added_at = datetime.now(timezone.utc).isoformat()

    create_video(video, added_at)

    logger.debug(f"Added video with ID {video.video_id}.")

    return VideoResponse(video_id=video.video_id, title=video.title, added_at=added_at)
