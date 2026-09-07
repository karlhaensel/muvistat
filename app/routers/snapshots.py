"""FastAPI routers for snapshots."""

import logging

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.database.snapshots import create_snapshot, read_all_snapshots
from app.database.videos import check_video_exists
from app.models import SnapshotCreate, SnapshotResponse
from app.youtube import get_youtube_video_information

ERROR_MSG_VIDEO_NOT_FOUND = "Video with ID {video_id} not found in videos table of database. Please add it first."

logger = logging.getLogger("api.routers.snapshots")

router = APIRouter(prefix="/videos", tags=["Statistics snapshots"])


@router.post(
    "/{video_id}/live_record", response_model=SnapshotResponse, status_code=201
)
def record_live_snapshot(video_id: str):
    """Fetch live statistics snapshot for given video from YouTube API and record it."""
    logger.debug(f"Attempting to record live snapshot for video with ID {video_id}.")

    try:
        check_video_exists(video_id, raise_for="not_found")
    except HTTPException:
        logger.error(ERROR_MSG_VIDEO_NOT_FOUND.format(video_id))
        raise
    logger.debug(
        f"Video with ID {video_id} exists in database. Proceeding to fetch stats."
    )

    items = get_youtube_video_information(video_id)

    logger.debug(f"Successfully fetched live stats for video with ID {video_id}.")

    recorded_at = datetime.now(timezone.utc).isoformat()
    stats_snapshot = SnapshotResponse.from_youtube_api_response_items(
        video_id, items, recorded_at
    )

    create_snapshot(
        video_id,
        stats_snapshot.views,
        stats_snapshot.likes,
        stats_snapshot.dislikes,
        stats_snapshot.comments,
        stats_snapshot.recorded_at,
    )

    logger.debug(
        f"Successfully recorded statistics snapshot for video with ID {video_id} "
        "in database."
    )

    return stats_snapshot


@router.post(
    "/{video_id}/manual_record", response_model=SnapshotResponse, status_code=201
)
def record_manual_snapshot(video_id: str, snapshot: SnapshotCreate):
    """Record video statistics snapshot manually (for dev, testing, backfills...)"""
    logger.debug(f"Attempting to record manual snapshot for video with ID {video_id}.")
    try:
        check_video_exists(video_id, raise_for="not_found")
    except HTTPException:
        logger.error(ERROR_MSG_VIDEO_NOT_FOUND.format(video_id))
        raise

    recorded_at = datetime.now(timezone.utc).isoformat()

    create_snapshot(
        video_id,
        snapshot.views,
        snapshot.likes,
        snapshot.dislikes,
        snapshot.comments,
        recorded_at,
    )

    logger.debug(
        f"Successfully recorded manual statistics snapshot for video with ID {video_id} "
        "in database."
    )

    return SnapshotResponse(
        video_id=video_id,
        views=snapshot.views,
        likes=snapshot.likes,
        dislikes=snapshot.dislikes,
        comments=snapshot.comments,
        recorded_at=recorded_at,
    )


@router.get("/{video_id}/history", response_model=list[SnapshotResponse])
def get_history(video_id: str):
    """Get history of video statistics snapshots."""
    logger.debug(
        f"Attempting to fetch statistics history for video with ID {video_id}."
    )

    try:
        check_video_exists(video_id, raise_for="not_found")
    except HTTPException:
        logger.error(ERROR_MSG_VIDEO_NOT_FOUND.format(video_id))
        raise

    rows = read_all_snapshots(video_id)

    logger.debug(
        f"Successfully fetched history for video with ID {video_id}. "
        f"Found {len(rows)} snapshots."
    )

    return [SnapshotResponse(**dict(row)) for row in rows]
