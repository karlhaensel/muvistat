"""FastAPI routers for snapshots."""

import logging
import os

import httpx
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.models import SnapshotCreate, SnapshotResponse
from app.database import get_db


ERROR_MSG_VIDEO_NOT_FOUND = "Video with ID {video_id} not found in videos table of database. Please add it first."

logger = logging.getLogger("api.routers.snapshots")

router = APIRouter(prefix="/videos", tags=["Statistics snapshots"])


@router.post(
    "/{video_id}/live_record", response_model=SnapshotResponse, status_code=201
)
def record_live_snapshot(video_id: str):
    """Fetch live statistics snapshot for given video from YouTube API and record it."""
    api_key = os.environ.get("YOUTUBE_API_KEY", "")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="YOUTUBE_API_KEY environment variable not set"
        )

    conn = get_db()
    video = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=ERROR_MSG_VIDEO_NOT_FOUND.format(video_id=video_id),
        )

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": video_id,
        "key": api_key,
    }

    response = httpx.get(url, params=params)
    if response.status_code != 200:
        conn.close()
        logger.error(
            f"YouTube API failed for video with ID {video_id}.\n"
            f"Status code: {response.status_code}\n"
            f"Response: {response.text}"
        )
        # Raise own error without further details to avoid security risks:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "YouTube API request failed.",
                "upstream_status_code": response.status_code,
            },
        )

    items = response.json().get("items")
    if not items:
        conn.close()
        logger.error(
            f"YouTube API did not find with ID {video_id}.\n"
            f"Status code: {response.status_code}\n"
            f"Response: {response.text}"
        )
        raise HTTPException(
            status_code=404, detail=f"Video with ID {video_id} not found on YouTube."
        )

    stats = items[0]["statistics"]
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))
    comments = int(stats.get("commentCount", 0))
    recorded_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        "INSERT INTO snapshots (video_id, views, likes, comments, recorded_at) VALUES (?, ?, ?, ?, ?)",
        (video_id, views, likes, comments, recorded_at),
    )
    conn.commit()
    conn.close()

    return SnapshotResponse(
        video_id=video_id,
        views=views,
        likes=likes,
        comments=comments,
        recorded_at=recorded_at,
    )


@router.post(
    "/{video_id}/manual_record", response_model=SnapshotResponse, status_code=201
)
def record_manual_snapshot(video_id: str, snapshot: SnapshotCreate):
    """Record video statistics snapshot manually (for dev, testing, backfills...)"""
    conn = get_db()

    video = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=ERROR_MSG_VIDEO_NOT_FOUND.format(video_id=video_id),
        )

    recorded_at = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO snapshots (video_id, views, likes, comments, recorded_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (video_id, snapshot.views, snapshot.likes, snapshot.comments, recorded_at),
    )
    conn.commit()
    conn.close()
    return SnapshotResponse(
        video_id=video_id,
        views=snapshot.views,
        likes=snapshot.likes,
        comments=snapshot.comments,
        recorded_at=recorded_at,
    )


@router.get("/{video_id}/history", response_model=list[SnapshotResponse])
def get_history(video_id: str):
    """Get history of video statistics snapshots."""
    conn = get_db()

    video = conn.execute(
        "SELECT video_id FROM videos WHERE video_id = ?", (video_id,)
    ).fetchone()
    if not video:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"No snapshots for video with ID {video_id}."
            "Add video and/or fetch statistics first.",
        )

    rows = conn.execute(
        "SELECT video_id, views, likes, comments, recorded_at FROM snapshots "
        "WHERE video_id = ? ORDER BY recorded_at",
        (video_id,),
    ).fetchall()
    conn.close()
    return [SnapshotResponse(**dict(row)) for row in rows]
