"""FastAPI router for videos."""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.database.videos import check_video_exists, create_video
from app.models import VideoCreate, VideoResponse


router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("", response_model=VideoResponse, status_code=201)
def add_video(video: VideoCreate):
    """Add a new video to be tracked."""
    check_video_exists(video.video_id, raise_for="already_existing")

    added_at = datetime.now(timezone.utc).isoformat()

    create_video(video, added_at)

    return VideoResponse(video_id=video.video_id, title=video.title, added_at=added_at)
