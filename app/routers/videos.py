"""FastAPI router for videos."""

import logging

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from app.database.metadata import create_metadata, update_metadata
from app.database.videos import check_video_exists, create_video, read_added_at
from app.models import VideoCreate, VideoMetadataResponse
from app.youtube import get_youtube_video_information

logger = logging.getLogger("api.routers.videos")

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("", response_model=VideoMetadataResponse, status_code=201)
def add_video(video: VideoCreate) -> VideoMetadataResponse:
    """Add a new video to be tracked."""
    logger.debug(f"Attempting to add video with ID {video.video_id}.")
    try:
        check_video_exists(video.video_id, raise_for="already_existing")
    except HTTPException:
        logger.error(f"Video with ID {video.video_id} already exists in database.")
        raise

    now = datetime.now(timezone.utc).isoformat()

    create_video(video, added_at=now)
    logger.debug(f"Added video with ID {video.video_id}.")

    items = get_youtube_video_information(video.video_id)

    metadata = VideoMetadataResponse.from_youtube_api_response_items(
        video.video_id,
        items,
        video_added_at=now,
        metadata_updated_at=now,
        my_comment=video.my_comment,
    )

    create_metadata(metadata)
    logger.debug(f"Added metadata for video with ID {video.video_id}.")

    return metadata


@router.post(
    "/{video_id}/update_metadata", response_model=VideoMetadataResponse, status_code=201
)
def update_video_metadata(video_id: str) -> VideoMetadataResponse:
    """Update the metadata for an existing video."""
    try:
        check_video_exists(video_id, raise_for="not_found")
    except HTTPException:
        logger.error(f"Video with ID {video_id} not found in database.")
        raise

    logger.debug(f"Attempting to update metadata for video with ID {video_id}.")

    video_added_at = read_added_at(video_id)
    if video_added_at is None:
        logger.error(
            f"Video with ID {video_id} exists in videos database, but not in metadata."
        )
        raise HTTPException(
            status_code=500,
            detail=f"Video with ID {video_id} is missing from metadata.",
        )

    items = get_youtube_video_information(video_id)

    now = datetime.now(timezone.utc).isoformat()
    metadata = VideoMetadataResponse.from_youtube_api_response_items(
        video_id,
        items,
        video_added_at=video_added_at,
        metadata_updated_at=now,
        my_comment=None,
    )
    update_metadata(metadata)

    logger.debug(f"Finished updating for video with ID {video_id}.")

    return metadata
