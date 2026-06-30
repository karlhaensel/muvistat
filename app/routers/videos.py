"""FastAPI router for videos."""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.models import VideoCreate, VideoResponse
from app.database import get_db


router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("", response_model=VideoResponse, status_code=201)
def add_video(video: VideoCreate):
    """Add a new video to be tracked."""
    conn = get_db()

    existing = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video.video_id,)
    ).fetchone()
    if existing:
        conn.close()
        raise HTTPException(
            status_code=409, detail=f"Video with ID {video.video_id} already tracked."
        )

    added_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        "INSERT INTO videos (video_id, title, added_at) VALUES (?, ?, ?)",
        (video.video_id, video.title, added_at),
    )
    conn.commit()
    conn.close()

    return VideoResponse(video_id=video.video_id, title=video.title, added_at=added_at)
